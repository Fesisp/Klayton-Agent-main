"""
Personality Matrix - Modelo de Personalidade do Companheiro
============================================================

Define os traços de personalidade do Klayton em escala [0.0, 1.0].
A personalidade altera dinamicamente as pontuações de utilidade e as decisões
sociais/exploratórias do agente.

Atributos:
- independence: Propensão a agir por conta própria vs. colar no líder.
- curiosity: Vontade de investigar novos elementos/áreas no mapa.
- risk_tolerance: Tolerância a batalhas arriscadas ou HP baixo.
- helpfulness: Prioridade em responder aos pedidos e combates do jogador humano.
- persistence: Resistência em abandonar um objetivo pessoal.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass


@dataclass
class Personality:
    """Matriz de traços de personalidade do Agente Companheiro."""
    independence: float = 0.35
    curiosity: float = 0.70
    risk_tolerance: float = 0.40
    helpfulness: float = 0.85
    persistence: float = 0.65

    def adjust_utility(self, action_type: str, base_utility: float) -> float:
        """
        Ajusta a utilidade de uma ação com base na personalidade.
        """
        multiplier = 1.0

        if action_type == "explore":
            multiplier += (self.curiosity - 0.5) * 0.4
        elif action_type == "follow":
            multiplier += (self.helpfulness - 0.5) * 0.5 - (self.independence - 0.5) * 0.3
        elif action_type == "risky_battle":
            multiplier += (self.risk_tolerance - 0.5) * 0.6
        elif action_type == "personal_goal":
            multiplier += (self.persistence - 0.5) * 0.4

        return base_utility * max(0.1, multiplier)
