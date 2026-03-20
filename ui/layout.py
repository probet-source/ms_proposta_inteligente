from __future__ import annotations
import streamlit as st
from core.constants import APP_NAME, APP_SUBTITLE


def render_header(certame: dict | None = None) -> None:
    st.title(APP_NAME)
    st.caption(APP_SUBTITLE)
    if certame:
        cols = st.columns(4)
        cols[0].metric('Órgão', certame.get('orgao') or '-')
        cols[1].metric('Modalidade', certame.get('modalidade') or '-')
        cols[2].metric('Processo', certame.get('numero_processo') or '-')
        cols[3].metric('Páginas', certame.get('page_count') or '-')
        st.divider()
