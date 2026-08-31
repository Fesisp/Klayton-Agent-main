"""
Intent Parser - Processador de Intenções em Linguagem Natural com Parâmetros
=============================================================================

Converte comandos de voz/texto livre em intenções estruturadas (AgentIntent)
e instancia Objetivos Parametrizados (GoalInstance).

Exemplo:
"Klayton, treina meu Pikachu até o nível 35"
--> AgentIntent(action="farm_xp", target="Pikachu", constraints={"target_level": 35})
--> GoalInstance(type=Goal.FARM_XP, target="Pikachu", target_level=35)

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ..decision.goal_engine import Goal, GoalInstance
from ..knowledge.knowledge_base import KnowledgeBase


@dataclass
class AgentIntent:
    action: str
    target: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""

    def to_goal(self) -> Goal:
        """Converte a ação para Enum Goal legado."""
        action_lower = self.action.lower()
        if "farm" in action_lower or "xp" in action_lower or "treina" in action_lower:
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

    def to_goal_instance(self) -> GoalInstance:
        """Converte a intenção em uma instância parametrizada de objetivo preservando o alvo e restrições."""
        goal_type = self.to_goal()
        target_lvl = self.constraints.get("target_level")
        loc_hint = self.constraints.get("location_hint")
        
        return GoalInstance(
            type=goal_type,
            target=self.target,
            target_level=target_lvl,
            location_hint=loc_hint,
            constraints=self.constraints,
            success_conditions={"level": target_lvl} if target_lvl else {}
        )


class IntentParser:
    """
    Parser de intenções com extração de alvos (Pokémon), níveis e locais via dicionário SQLite.
    """

    def __init__(self):
        self.kb = KnowledgeBase()

    def parse(self, text: str) -> AgentIntent:
        text_clean = text.strip().lower()

        # Extração de alvo (Pokémon) via busca na base SQLite
        target_pokemon = None
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_clean)
        for w in words:
            if w in ["ate", "nivel", "level", "farma", "treina", "meu", "pro", "para"]:
                continue
            pk_info = self.kb.get_pokemon(w)
            if pk_info:
                target_pokemon = pk_info["name"]
                break

        # Extração de Nível Alvo
        lvl = None
        lvl_match = re.search(r'(?:até|ate|ao|lvl|level|nível|nivel)\s*(\d+)', text_clean)
        if lvl_match:
            lvl = int(lvl_match.group(1))

        constraints = {}
        if lvl:
            constraints['target_level'] = lvl

        # 1. Padrão: "farma" / "treinar" / "upar" / "farm xp"
        if any(w in text_clean for w in ["farma", "farmar", "treinar", "treina", "treino", "upar", "xp"]):
            return AgentIntent(action="farm_xp", target=target_pokemon, constraints=constraints, raw_text=text)

        # 2. Padrão: "pesca" / "vai pescar"
        if "pesca" in text_clean or "fish" in text_clean:
            return AgentIntent(action="fish", target=target_pokemon, constraints=constraints, raw_text=text)

        # 3. Padrão: "segue" / "fica comigo"
        if "segue" in text_clean or "comigo" in text_clean or "follow" in text_clean:
            return AgentIntent(action="follow", target=target_pokemon, raw_text=text)

        # 4. Padrão: "cura" / "vai pro pokemon center"
        if "cura" in text_clean or "center" in text_clean or "heal" in text_clean:
            return AgentIntent(action="heal_team", target=target_pokemon, raw_text=text)

        # 5. Padrão: "para" / "fica parado"
        if "para" in text_clean or "stop" in text_clean or "idle" in text_clean:
            return AgentIntent(action="idle", target=target_pokemon, raw_text=text)

        return AgentIntent(action="unknown", target=target_pokemon, constraints=constraints, raw_text=text)
