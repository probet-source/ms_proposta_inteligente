from __future__ import annotations
import pandas as pd
import streamlit as st


def render_certame_cards(certame: dict, items_df: pd.DataFrame | None, checklist_df: pd.DataFrame | None) -> None:
    total_itens = 0 if items_df is None else len(items_df)
    total_lotes = 0 if items_df is None or 'lote' not in items_df.columns else items_df['lote'].astype(str).replace('', pd.NA).dropna().nunique()
    pendencias = 0 if checklist_df is None else len(checklist_df[checklist_df['resolvido'] == False])
    cols = st.columns(4)
    cols[0].metric('Itens encontrados', total_itens)
    cols[1].metric('Lotes', total_lotes)
    cols[2].metric('Pendências', pendencias)
    cols[3].metric('Arquivo', certame.get('nome_arquivo', '-'))
