"""Ponto de entrada da carga (chamado pelo Airflow e na linha de comando).

O codigo fica no pacote `scdp` (extracao, carga, transformacao, controle e pipeline).
O Python em modo isolado (-I) nao inclui a pasta do script no sys.path, por isso ela e adicionada aqui.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scdp.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
