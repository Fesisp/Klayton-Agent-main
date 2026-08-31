"""
Navigate Skill - Máquina de Estados de Navegação em Ciclo Fechado
===================================================================

Executa a navegação espacial em ciclo fechado:
ACQUIRE_LOCATION ➔ RESOLVE_DESTINATION ➔ PLAN_ROUTE ➔ EXECUTE_SEGMENT ➔ VERIFY_PROGRESS ➔ ARRIVED

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NavigateSkill")

from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState
from ..world.model.world_location import WorldLocation, LocationConfidence
from ..world.model.world_model import WorldModel
from ..world.model.world_model_store import WorldModelStore
from ..navigation.runtime.navigation_observation import NavigationObservation
from ..navigation.runtime.localization import LocalizationEngine
from ..navigation.runtime.destination_resolver import DestinationResolver
from ..navigation.runtime.navigation_action import NavigationAction, NavigationActionType
from ..navigation.runtime.navigation_executor import NavigationExecutor, NavigationExecutorPhase
from ..navigation.runtime.navigation_progress import NavigationProgress
from ..navigation.runtime.navigation_progress_verifier import NavigationProgressVerifier
from ..navigation.runtime.stuck_detector import StuckDetector, StuckSeverity
from ..navigation.runtime.route_state import RouteState


class NavigatePhase(Enum):
    """Fases da máquina de estados de navegação."""
    ACQUIRE_LOCATION = "acquire_location"
    RESOLVE_DESTINATION = "resolve_destination"
    PLAN_ROUTE = "plan_route"
    EXECUTE_SEGMENT = "execute_segment"
    VERIFY_PROGRESS = "verify_progress"
    RECOVER = "recover"
    REPLAN = "replan"
    ARRIVED = "arrived"
    FAILED = "failed"


class NavigateSkill(BaseSkill):
    """
    Skill autônoma de navegação espacial em ciclo fechado.
    """

    def __init__(self, target_map: Optional[str] = None, config: Dict[str, Any] = None):
        super().__init__(name="NavigateSkill", config=config)
        self.target_map = target_map

        self.phase: NavigatePhase = NavigatePhase.ACQUIRE_LOCATION
        self.localizer: LocalizationEngine = LocalizationEngine()
        self.resolver: DestinationResolver = DestinationResolver()
        self.executor: NavigationExecutor = NavigationExecutor()
        self.verifier: NavigationProgressVerifier = NavigationProgressVerifier()
        self.stuck_detector: StuckDetector = StuckDetector()

        self.world_model_store = WorldModelStore()
        self.world_model: WorldModel = self.world_model_store.load_model()

        self.current_location: Optional[WorldLocation] = None
        self.destination: Optional[WorldLocation] = None
        self.route_state: Optional[RouteState] = None
        self.before_loc: Optional[WorldLocation] = None
        self.current_action: Optional[NavigationAction] = None

    def reset_runtime_state(self) -> None:
        super().reset_runtime_state()
        self.phase = NavigatePhase.ACQUIRE_LOCATION
        self.executor.reset()
        self.stuck_detector.reset()
        self.current_location = None
        self.destination = None
        self.route_state = None
        self.before_loc = None
        self.current_action = None

    def can_execute(self, world: WorldState) -> bool:
        # Pausa navegação durante combate sem destruir a rota ativa
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        # Se houver combate em andamento, suspende temporariamente
        if world.battle.in_battle:
            return SkillResult(status=SkillStatus.RUNNING, message="Navegação pausada temporariamente para combate.")

        now = time.time()
        target = self.target_map or getattr(self, 'target_map', None)
        if not target:
            return SkillResult(status=SkillStatus.FAILED, message="NavigateSkill: NENHUM MAPA DESTINO FORNECIDO")

        # Constrói observação de navegação instantânea
        obs = NavigationObservation(
            timestamp=now,
            map_id=world.location.current_map,
            world_x=float(world.location.coordinates[0]) if world.location.coordinates else None,
            world_y=float(world.location.coordinates[1]) if world.location.coordinates else None,
            confidence=0.90
        )

        # 1. ACQUIRE_LOCATION
        self.current_location = self.localizer.locate(obs, self.current_location)
        world.navigation.current_location = self.current_location

        # 2. RESOLVE_DESTINATION
        if self.destination is None or (self.target_map and self.destination.map_id != self.target_map):
            self.destination = self.resolver.resolve(target, self.world_model)
            world.navigation.destination = self.destination
            self.phase = NavigatePhase.PLAN_ROUTE

        # 3. PLAN_ROUTE
        if self.phase == NavigatePhase.PLAN_ROUTE or self.route_state is None:
            nodes = [self.current_location.map_id or "Unknown", target]
            self.route_state = RouteState(route_id=f"route_{int(now)}", nodes=nodes)
            self.phase = NavigatePhase.EXECUTE_SEGMENT

        # Checa chegada ao destino
        if self.current_location and self.current_location.map_id and self.current_location.map_id.lower() == target.lower():
            self.phase = NavigatePhase.ARRIVED
            return SkillResult(status=SkillStatus.SUCCESS, message=f"Chegamos com sucesso ao mapa '{target}'!")

        # 4. EXECUTE_SEGMENT
        if self.phase in [NavigatePhase.EXECUTE_SEGMENT, NavigatePhase.REPLAN]:
            self.before_loc = self.current_location
            self.current_action = NavigationAction(
                type=NavigationActionType.MOVE,
                direction="w",
                target_map=target,
                reason=f"Mover em direção a {target}"
            )
            self.executor.start(self.current_action)
            self.executor.tick(input_sim, obs)
            self.phase = NavigatePhase.VERIFY_PROGRESS

        # 5. VERIFY_PROGRESS
        if self.phase == NavigatePhase.VERIFY_PROGRESS:
            progress = self.verifier.verify(self.before_loc, self.current_action, self.current_location, self.route_state, self.destination)
            stuck_sev = self.stuck_detector.update(progress)

            if stuck_sev in [StuckSeverity.CONFIRMED, StuckSeverity.HARD]:
                self.phase = NavigatePhase.RECOVER
                if hasattr(input_sim, 'press'):
                    input_sim.press('d')  # Tenta direção de alívio
                self.stuck_detector.reset()
                return SkillResult(status=SkillStatus.RUNNING, message=f"Navegação: Trava de stuck ({stuck_sev.value}) ativada! Executando recuperação...")

            if progress in [NavigationProgress.PROGRESS, NavigationProgress.WAYPOINT_REACHED, NavigationProgress.MAP_CHANGED]:
                self.phase = NavigatePhase.EXECUTE_SEGMENT
            elif progress == NavigationProgress.ARRIVED:
                self.phase = NavigatePhase.ARRIVED
                return SkillResult(status=SkillStatus.SUCCESS, message=f"Chegamos com sucesso ao destino '{target}'!")
            else:
                self.phase = NavigatePhase.EXECUTE_SEGMENT

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Navegando: {self.current_location.map_id} ➔ Destino: {target}"
        )

    def is_complete(self, world: WorldState) -> bool:
        target = self.target_map or getattr(self, 'target_map', None)
        if not target:
            return False
        return world.location.current_map == target
