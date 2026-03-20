import pandas as pd
from modules.validacao import validate_proposal


def test_validacao_gera_alerta():
    df = pd.DataFrame([
        {'lote': '1', 'item': '1', 'descricao': 'Teste', 'unidade': 'UN', 'quantidade': 1, 'valor_unitario': 0}
    ])
    out = validate_proposal(df)
    assert not out.empty
