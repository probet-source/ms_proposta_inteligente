from __future__ import annotations
from pathlib import Path
import streamlit as st


def render_download_buttons(files: dict[str, str]) -> None:
    for label, path in files.items():
        file_path = Path(path)
        if not file_path.exists():
            continue
        mime = 'application/octet-stream'
        if file_path.suffix == '.zip':
            mime = 'application/zip'
        elif file_path.suffix == '.xlsx':
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_path.suffix == '.docx':
            mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_path.suffix == '.json':
            mime = 'application/json'
        with file_path.open('rb') as f:
            st.download_button(f'Baixar {file_path.name}', data=f.read(), file_name=file_path.name, mime=mime)
