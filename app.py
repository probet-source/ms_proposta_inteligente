from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

from core.config import CONFIG
from core.session_state import init_session, go_to_step
from core.logger import logger
from modules.ingestao import process_upload
from modules.leitura_edital import build_certame_summary
from modules.extracao_tabelas import extract_items_from_pdf
from modules.normalizacao import normalize_items
from modules.oficina_proposta import build_proposal_frame
from modules.validacao import validate_proposal
from modules.exportacao import export_all
from services.persistence_service import append_history, load_history
from ui.layout import render_header
from ui.sidebar import render_sidebar
from ui.dashboard import render_certame_cards
from ui.alerts import info_box, success_box, warning_box, error_box
from ui.tables import editable_dataframe
from ui.download import render_download_buttons

st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout=CONFIG.layout,
    initial_sidebar_state=CONFIG.initial_sidebar_state,
)

init_session()
current_step = render_sidebar(st.session_state['current_step'])
st.session_state['current_step'] = current_step
render_header(st.session_state['certame'])


def _sidebar_company_form() -> None:
    with st.sidebar.expander('Dados da empresa', expanded=False):
        for key, value in st.session_state['company_data'].items():
            st.session_state['company_data'][key] = st.text_input(key.replace('_', ' ').title(), value=value)


_sidebar_company_form()

if st.session_state['certame']:
    render_certame_cards(st.session_state['certame'], st.session_state['proposal_df'], st.session_state['checklist_df'])

if current_step == 'upload':
    st.subheader('Upload do edital')
    uploaded = st.file_uploader('Envie o edital em PDF pesquisável', type=['pdf'])
    col1, col2 = st.columns([1, 1])
    process_btn = col1.button('Ler edital', type='primary', disabled=uploaded is None)
    new_btn = col2.button('Limpar fluxo atual')
    if new_btn:
        for key in ['certame', 'raw_items_df', 'items_df', 'proposal_df', 'checklist_df', 'generated_files', 'uploaded_file_path']:
            st.session_state[key] = {} if key in {'certame', 'generated_files'} else None
        st.session_state['current_step'] = 'upload'
        st.rerun()

    if process_btn and uploaded is not None:
        try:
            upload_result = process_upload(uploaded)
            if not upload_result['has_text']:
                warning_box('O PDF parece não possuir texto pesquisável. A V1 funciona melhor com PDF textual.')
            certame = build_certame_summary(upload_result)
            raw_items_df, _ = extract_items_from_pdf(certame['_source_path'])
            items_df = normalize_items(raw_items_df)
            proposal_df = build_proposal_frame(items_df)
            checklist_df = validate_proposal(proposal_df)

            st.session_state['uploaded_file_path'] = certame['_source_path']
            st.session_state['certame'] = certame
            st.session_state['raw_items_df'] = raw_items_df
            st.session_state['items_df'] = items_df
            st.session_state['proposal_df'] = proposal_df
            st.session_state['checklist_df'] = checklist_df
            success_box('Edital processado com sucesso.')
            go_to_step('resumo')
            st.rerun()
        except Exception as exc:
            logger.exception(exc)
            error_box(f'Falha ao processar o edital: {exc}')

    history = load_history()[:10]
    if history:
        st.subheader('Últimos certames exportados')
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
    else:
        info_box('Nenhum histórico de exportação ainda.')

elif current_step == 'resumo':
    st.subheader('Resumo do edital')
    certame = st.session_state['certame']
    if not certame:
        warning_box('Envie um edital primeiro.')
    else:
        resumo_df = pd.DataFrame([
            {'Campo': k.replace('_', ' ').title(), 'Valor': v}
            for k, v in certame.items() if not k.startswith('_')
        ])
        st.dataframe(resumo_df, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        if col1.button('Ir para itens extraídos', type='primary'):
            go_to_step('itens')
            st.rerun()
        if col2.button('Reprocessar arquivo'):
            go_to_step('upload')
            st.rerun()

elif current_step == 'itens':
    st.subheader('Itens extraídos do edital')
    items_df = st.session_state['items_df']
    if items_df is None:
        warning_box('Nenhum item disponível. Faça o upload do edital.')
    else:
        st.caption('Revise lotes, itens, descrições, unidades e quantidades antes de avançar.')
        edited = editable_dataframe(items_df, key='items_editor', disabled=['categoria'])
        if st.button('Salvar revisão dos itens', type='primary'):
            st.session_state['items_df'] = edited
            st.session_state['proposal_df'] = build_proposal_frame(edited)
            st.session_state['checklist_df'] = validate_proposal(st.session_state['proposal_df'])
            success_box('Itens revisados com sucesso.')
        if st.button('Avançar para oficina da proposta'):
            go_to_step('oficina')
            st.rerun()

elif current_step == 'oficina':
    st.subheader('Oficina da proposta')
    proposal_df = st.session_state['proposal_df']
    if proposal_df is None:
        warning_box('Nenhuma proposta disponível. Revise os itens primeiro.')
    else:
        st.caption('Preencha dados comerciais, marca, modelo, fabricante e valor unitário.')
        edited = editable_dataframe(proposal_df, key='proposal_editor', disabled=['valor_total', 'categoria', 'status_extracao'])
        if 'valor_unitario' in edited.columns:
            edited['valor_unitario'] = pd.to_numeric(edited['valor_unitario'], errors='coerce').fillna(0.0)
        if 'quantidade' in edited.columns:
            edited['quantidade'] = pd.to_numeric(edited['quantidade'], errors='coerce')
        edited['valor_total'] = (edited['quantidade'].fillna(0) * edited['valor_unitario'].fillna(0)).round(2)
        total = float(edited['valor_total'].sum()) if 'valor_total' in edited.columns else 0.0
        st.metric('Valor global estimado', f"R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        require_brand = st.checkbox('Tratar marca como obrigatória na validação', value=False)
        if st.button('Salvar proposta e validar', type='primary'):
            st.session_state['proposal_df'] = edited
            st.session_state['checklist_df'] = validate_proposal(edited, require_brand=require_brand)
            success_box('Proposta atualizada e validada.')
        if st.button('Ir para validação'):
            go_to_step('validacao')
            st.rerun()

elif current_step == 'validacao':
    st.subheader('Checklist de validação')
    checklist_df = st.session_state['checklist_df']
    if checklist_df is None:
        warning_box('Nenhum checklist disponível.')
    else:
        st.dataframe(checklist_df, use_container_width=True, hide_index=True)
        criticos = int((checklist_df['tipo'] == 'crítico').sum()) if 'tipo' in checklist_df.columns else 0
        atencoes = int((checklist_df['tipo'] == 'atenção').sum()) if 'tipo' in checklist_df.columns else 0
        col1, col2 = st.columns(2)
        col1.metric('Pendências críticas', criticos)
        col2.metric('Alertas de atenção', atencoes)
        if st.button('Ir para exportação', type='primary'):
            go_to_step('exportacao')
            st.rerun()

elif current_step == 'exportacao':
    st.subheader('Exportação dos arquivos finais')
    certame = st.session_state['certame']
    proposal_df = st.session_state['proposal_df']
    checklist_df = st.session_state['checklist_df']
    if not certame or proposal_df is None or checklist_df is None:
        warning_box('Fluxo incompleto. Faça o upload e revise a proposta antes de exportar.')
    else:
        if st.button('Gerar pacote final', type='primary'):
            try:
                files = export_all(certame, st.session_state['company_data'], proposal_df, checklist_df)
                st.session_state['generated_files'] = files
                append_history({
                    'orgao': certame.get('orgao', ''),
                    'processo': certame.get('numero_processo', ''),
                    'arquivo': certame.get('nome_arquivo', ''),
                    'itens': len(proposal_df),
                    'valor_global': float(proposal_df['valor_total'].fillna(0).sum()) if 'valor_total' in proposal_df.columns else 0,
                    'zip': files['zip'],
                })
                success_box('Pacote final gerado com sucesso.')
            except Exception as exc:
                logger.exception(exc)
                error_box(f'Falha ao gerar exportações: {exc}')

        if st.session_state['generated_files']:
            render_download_buttons(st.session_state['generated_files'])
            st.code(st.session_state['generated_files']['folder'])
        else:
            info_box('Clique em gerar pacote final para criar Excel, DOCX, JSON e ZIP.')
