from etapa2.clasificador import claude_client


def test_clasificador_degrada_sin_api_key(monkeypatch):
    monkeypatch.setattr(claude_client, "ANTHROPIC_API_KEY", "")
    resultado = claude_client.clasificar("No puedo acceder al sistema")
    assert resultado.modo == "degradado"
    assert resultado.categoria == "otros"
    assert resultado.prioridad == "media"


def test_clasificador_limita_confianza():
    resultado = claude_client._parse_resultado(
        '{"content": [{"text": "{\\"categoria\\": \\"red\\", \\"prioridad\\": \\"alta\\", \\"confianza\\": 2}"}]}'
    )
    assert resultado.categoria == "red"
    assert resultado.prioridad == "alta"
    assert resultado.confianza == 1.0