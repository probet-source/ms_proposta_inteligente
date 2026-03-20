# MS Proposta Inteligente

Plataforma em Streamlit para transformar editais em planilhas operacionais e proposta comercial base.

## O que a V1 faz
- Upload de edital em PDF pesquisável
- Leitura estrutural do certame
- Extração de tabelas e itens
- Revisão dos itens em grade editável
- Oficina da proposta com marca/modelo/fabricante/preços
- Validação com checklist
- Exportação para Excel, DOCX, JSON e ZIP final

## Estrutura
- `app.py`: ponto de entrada Streamlit
- `core/`: configuração, paths, sessão e logging
- `modules/`: regras de negócio
- `services/`: PDF, Excel, DOCX, ZIP e persistência
- `ui/`: componentes da interface
- `storage/`: uploads, processados e exportações

## Como rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no GitHub + Streamlit
1. Suba esta pasta inteira para um repositório no GitHub.
2. No Streamlit Community Cloud, conecte o repositório.
3. Defina `app.py` como arquivo principal.
4. Garanta que os arquivos de `storage/` tenham permissão de escrita no ambiente escolhido.

## Limitações conhecidas da V1
- PDFs escaneados podem exigir OCR externo.
- A extração de tabelas varia conforme a diagramação do edital.
- A proposta DOCX gerada é uma base operacional e deve ser revisada antes do envio.

## Licença
Uso interno / comercial conforme sua estratégia de produto.
