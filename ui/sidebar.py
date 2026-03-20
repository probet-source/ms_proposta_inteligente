from __future__ import annotations
import streamlit as st
from core.constants import STEP_KEYS

STEP_LABELS = {
    'upload': '1. Upload',
    'resumo': '2. Resumo do edital',
    'itens': '3. Itens extraídos',
    'oficina': '4. Oficina da proposta',
    'validacao': '5. Validação',
    'exportacao': '6. Exportar',
}


def render_sidebar(current_step: str) -> str:
    st.sidebar.header('Fluxo do Certame')
    step = st.sidebar.radio(
        'Navegação',
        STEP_KEYS,
        format_func=lambda x: STEP_LABELS[x],
        index=STEP_KEYS.index(current_step) if current_step in STEP_KEYS else 0,
    )
    st.sidebar.divider()
    st.sidebar.caption('V1 profissional para operação de propostas em licitações.')
    return step
