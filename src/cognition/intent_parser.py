"""
Intent Parser - Processador de Intenções em Linguagem Natural
=============================================================

Converte comandos de voz/texto livre em intenções estruturadas (AgentIntent)
e mapeia diretamente para os Objetivos (Goals) do Agent Framework.

Exemplo:
"Klayton, farma XP pro Charmeleon até o 35"
--> AgentIntent(action="farm_xp", target="Charmeleon", constraints={"target_level": 35})
--> Goal.FARM_XP

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ..decision.goal_engine import Goal


@dataclass
class AgentIntent:
    action: str
    target: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""

    def to_goal(self) -> Goal:
        action_lower = self.action.lower()
        if "farm" in action_lower or "xp" in action_lower:
            return Goal.FARM_XP
        elif "pesca" in action_lower or "fish" in action_lower:
            return Goal.FISH
        elif "caça" in action_lower or "hunt" in action_lower:
            return Goal.HUNT
        elif "segue" in action_lower or "follow" in action_lower:
            return Goal.FOLLOW_PLAYER
        elif "historia" in action_lower or "quest" in action_lower or "missao" in action_lower:
            return Goal.PROGRESS_STORY
        elif "cura" in action_lower or "center" in action_lower or "heal" in action_lower:
            return Goal.HEAL_TEAM
        elif "para" in action_lower or "idle" in action_lower or "ocioso" in action_lower:
            return Goal.IDLE
        return Goal.IDLE


class IntentParser:
    """
    Parser de intenções baseado em regras de extração e expressões regulares.
    (Pode ser estendido para chamar um LLM local/Whisper).
    """

    def parse(self, text: str) -> AgentIntent:
        text_clean = text.strip().lower()

        # 1. Padrão: "farma xp pro [target] até o [level]"
        farm_match = re.search(r'(?:farma|farmar|treinar)\s+xp\s+(?:pro|para|o)?\s*(\w+)?\s*(?:até|ate)?\s*(?:o)?\s*(?:lvl|level)?\s*(\d+)?', text_clean)
        if farm_match:
            target = farm_match.group(1)
            lvl = int(farm_match.group(2)) if farm_match.group(2) else None
            constraints = {}
            if lvl:
                constraints['target_level'] = lvl
            return AgentIntent(action="farm_xp", target=target, constraints=constraints, raw_text=text)

        # 2. Padrão: "pesca" / "vai pescar"
        if "pesca" in text_clean or "fish" in text_clean:
            return AgentIntent(action="fish", raw_text=text)

        # 3. Padrão: "segue" / "fica comigo"
        if "segue" in text_clean or "comigo" in text_clean or "follow" in text_clean:
            return AgentIntent(action="follow", raw_text=text)

        # 4. Padrão: "cura" / "vai pro pokemon center"
        if "cura" in text_clean or "center" in text_clean or "heal" in text_clean:
            return AgentIntent(action="heal_team", raw_text=text)

        # 5. Padrão: "para" / "fica parado"
        if "para" in text_clean or "stop" in text_clean or "idle" in text_clean:
            return AgentIntent(action="idle", raw_text=text)

        # Fallback genérico
        return AgentIntent(action="unknown", raw_text=text)
