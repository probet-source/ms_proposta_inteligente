from __future__ import annotations
import pandas as pd
import streamlit as st


def editable_dataframe(df: pd.DataFrame, key: str, disabled: list[str] | None = None) -> pd.DataFrame:
    disabled = disabled or []
    config = {}
    return st.data_editor(df, key=key, use_container_width=True, disabled=disabled, num_rows='dynamic', column_config=config)
