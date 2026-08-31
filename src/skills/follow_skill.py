"""
Follow Skill - Acompanhamento Dinâmico e Social do Líder Felipe
===============================================================

Comportamento central do Companheiro Klayton:
1. Felipe Visível:
   - Mede distância relativa
   - Aproxima suavemente
   - Mantém distância configurada (zona de conforto)
2. Felipe Desaparece / Sai da Tela:
   - Dead Reckoning: Utiliza a última posição conhecida e direção do vetor de movimento
   - Procura a saída de mapa correspondente
   - Executa troca de mapa e relocaliza o líder
3. Comandos Sociais Suportados:
   - "vem comigo": Ativa acompanhamento padrão
   - "espera aqui": Pausa acompanhamento e entra em estado de espera
   - "fica perto": Reduz distância de segurança (acompanhamento cerrado)
   - "vai na frente": Assume liderança exploratória momentânea
   - "volta": Retorna imediatamente para a posição de Felipe

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
import math
from typing import Any, Dict, Optional, Tuple
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class FollowSkill(BaseSkill):
    """
    Skill avançada de acompanhamento cooperativo e espacial.
    """

    def __init__(self, target_player: str = "Felipe", config: Optional[Dict[str, Any]] = None):
        super().__init__(name="FollowSkill", config=config)
        self.target_player = target_player
        
        # Configurações de distância
        self.target_distance = 60.0  # Pixels de distância desejada
        self.close_distance = 30.0   # Modo "fica perto"
        self.max_distance = 250.0    # Limite antes de acelerar
        
        # Memória Espacial e Dead Reckoning
        self.last_seen_pos: Optional[Tuple[int, int]] = None
        self.last_direction_vector: Tuple[int, int] = (0, 0)
        self.last_seen_timestamp: float = time.time()
        self.lost_contact: bool = False
        
        # Modos sociais
        self.mode = "normal"  # normal, close, wait, ahead

    def can_execute(self, world: WorldState) -> bool:
        # Não segue se estiver em batalha ou se o jogador pediu para esperar
        return not world.battle.in_battle and not world.companion.is_following_leader is False

    def handle_social_command(self, command: str) -> str:
        """Ajusta parâmetros de acompanhamento com base em ordens verbais."""
        cmd_lower = command.lower()
        if "espera" in cmd_lower or "fica aqui" in cmd_lower:
            self.mode = "wait"
            return "Entendido Felipe, vou te esperar aqui!"
        elif "fica perto" in cmd_lower or "cola em mim" in cmd_lower:
            self.mode = "close"
            self.target_distance = self.close_distance
            return "Beleza, vou ficar coladinho em você!"
        elif "vai na frente" in cmd_lower:
            self.mode = "ahead"
            return "Indo na frente, qualquer coisa me avisa!"
        elif "vem comigo" in cmd_lower or "volta" in cmd_lower:
            self.mode = "normal"
            self.target_distance = 60.0
            return "Tô contigo, vamos nessa!"
        return "Tô te acompanhando!"

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if not input_sim:
            return SkillResult(status=SkillStatus.FAILED, message="InputSimulator ausente")

        if self.mode == "wait":
            return SkillResult(status=SkillStatus.SUCCESS, message=f"Aguardando {self.target_player} no local...")

        current_target_pos = world.companion.target_player_position
        agent_pos = world.player.position or (400, 300)

        # 1. FELIPE VISÍVEL NA TELA
        if current_target_pos:
            self.lost_contact = False
            self.last_seen_timestamp = time.time()
            if self.last_seen_pos:
                # Calcula vetor de velocidade/direção de Felipe
                dx = current_target_pos[0] - self.last_seen_pos[0]
                dy = current_target_pos[1] - self.last_seen_pos[1]
                if dx != 0 or dy != 0:
                    self.last_direction_vector = (dx, dy)
            self.last_seen_pos = current_target_pos

            # Calcula distância
            dist = math.hypot(current_target_pos[0] - agent_pos[0], current_target_pos[1] - agent_pos[1])
            world.companion.leader_distance = dist
            world.companion.is_following_leader = True

            # Se já está na distância ideal, mantém posição
            if dist <= self.target_distance:
                return SkillResult(status=SkillStatus.RUNNING, message=f"Acompanhando {self.target_player} (Distância ideal: {dist:.1f}px)")

            # Movimento em direção ao líder
            dx = current_target_pos[0] - agent_pos[0]
            dy = current_target_pos[1] - agent_pos[1]

            if abs(dx) > abs(dy):
                key = 'd' if dx > 0 else 'a'
            else:
                key = 's' if dy > 0 else 'w'

            if hasattr(input_sim, 'press'):
                input_sim.press(key)

            return SkillResult(
                status=SkillStatus.RUNNING,
                message=f"Aproximando de {self.target_player} (Direção: {key.upper()} | Distância: {dist:.1f}px)"
            )

        # 2. FELIPE DESAPARECEU (DEAD RECKONING & TROCA DE MAPA)
        self.lost_contact = True
        elapsed_lost = time.time() - self.last_seen_timestamp

        # Move na última direção conhecida do vetor
        vx, vy = self.last_direction_vector
        if vx != 0 or vy != 0:
            key = 'd' if vx > 0 else 'a' if vx < 0 else ('s' if vy > 0 else 'w')
            if hasattr(input_sim, 'press'):
                input_sim.press(key)
            return SkillResult(
                status=SkillStatus.RUNNING,
                message=f"Felipe sumiu da tela ({elapsed_lost:.1f}s atrás). Seguindo rastro pela última direção: {key.upper()}"
            )

        return SkillResult(
            status=SkillStatus.RUNNING,
            message="Procurando pelo líder Felipe nos arredores..."
        )

    def is_complete(self, world: WorldState) -> bool:
        return False  # Follow é uma skill contínua de acompanhamento


# Alias para retrocompatibilidade
FollowPlayerSkill = FollowSkill
