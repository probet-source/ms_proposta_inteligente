import pandas as pd
from modules.normalizacao import normalize_items


def test_normalizacao_basica():
    df = pd.DataFrame([
        {'lote': '1', 'item': '1', 'descricao': 'Notebook', 'unidade': 'UN', 'quantidade': '10', 'pagina_origem': 2}
    ])
    out = normalize_items(df)
    assert out.loc[0, 'categoria'] == 'informática'
    assert float(out.loc[0, 'quantidade']) == 10.0
