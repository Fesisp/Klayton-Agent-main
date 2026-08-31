"""
Placeholders & Calibration Sentinels - Klayton Companion Agent
==============================================================

Define valores placeholder formais para dados dependentes de calibração oficial
do PokeOne ou detectores em desenvolvimento.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

class CalibrationRequired:
    """
    Placeholder formal para indicar que uma variável ou calibração
    do jogo ainda precisa ser capturada ou configurada.
    """
    def __init__(self, reason: str = "Aguardando calibração oficial do PokeOne"):
        self.reason = reason

    def __repr__(self) -> str:
        return f"<CalibrationRequired: {self.reason}>"

    def __bool__(self) -> bool:
        return False
