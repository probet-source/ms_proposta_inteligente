from __future__ import annotations
import streamlit as st


def info_box(message: str) -> None:
    st.info(message)


def success_box(message: str) -> None:
    st.success(message)


def warning_box(message: str) -> None:
    st.warning(message)


def error_box(message: str) -> None:
    st.error(message)
