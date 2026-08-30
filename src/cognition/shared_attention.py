"""
Shared Attention - Resolução de Referências Contextuais
======================================================

Resolve referências vagas de linguagem natural como "Pega esse", "Olha aquele",
"Me ajuda nesse" cruzando alvos de combate, posição do mouse e entidades no centro da tela.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Optional, Dict, Any
from ..world.world_state import WorldState


class SharedAttention:
    """
    Mecanismo de Atenção Compartilhada entre o Humano e o Companheiro.
    """

    def resolve_target(self, phrase: str, world: WorldState) -> Optional[str]:
        phrase_clean = phrase.lower()

        # Se a frase contém "esse", "aquele", "este"
        if any(ref in phrase_clean for ref in ["esse", "este", "aquele", "nessa", "nesse"]):
            # 1. Se estamos em batalha ou há oponente visível
            if world.battle.in_battle and world.battle.opponent_name:
                return world.battle.opponent_name

            # 2. Se há alvo detectado no ambiente
            if world.raw_data.get('hovered_entity'):
                return str(world.raw_data.get('hovered_entity'))

        return None
