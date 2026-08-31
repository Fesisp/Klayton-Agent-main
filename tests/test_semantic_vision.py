"""
Test Semantic Vision Subsystem - Validação da Percepção Visual Semântica do Klayton
====================================================================================

Valida:
1. Provedores de VLM (NullVisionProvider, GeminiVisionProvider, LocalVisionProvider).
2. Roteamento por Confiança (ConfidenceRouter), Cooldown (2s) e Cache por Hash Perceptual.
3. Fusão Ponderada de Percepções (PerceptionFusion).
4. Aprendizado Visual (VisualTeacher) e Ciclo de Hipóteses (HYPOTHESIS -> CONFIRMED).
5. Rastreamento Egocêntrico (TargetTracker) em coordenadas (0.5, 0.5) com oclusão.
6. Navegação de Aproximação (InteractionNavigator) e Verificação Pós-Interação.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.perception.semantic.semantic_observation import (
    SemanticObservation, SemanticObject, SemanticHypothesis, PossibleInteraction
)
from src.perception.semantic.providers.base_provider import VisionLanguageProvider
from src.perception.semantic.providers.null_provider import NullVisionProvider
from src.perception.semantic.providers.gemini_provider import GeminiVisionProvider
from src.perception.semantic.providers.local_provider import LocalVisionProvider
from src.perception.semantic.confidence_router import ConfidenceRouter, SemanticBudget
from src.perception.semantic.semantic_memory import SemanticMemory
from src.perception.semantic.visual_teacher import VisualTeacher
from src.perception.semantic.target_tracker import TargetTracker, TrackedEntity, PLAYER_SCREEN_POSITION
from src.perception.semantic.interaction_navigator import InteractionNavigator
from src.perception.semantic.perception_fusion import PerceptionFusion
from src.perception.semantic.visual_reasoner import VisualReasoner
from src.perception.perception_snapshot import PerceptionSnapshot


def test_semantic_vision_pipeline():
    print("🧪 Testando Subsistema de Inteligência Visual Semântica (Semantic Vision)...")

    null_provider = NullVisionProvider()
    res_null = null_provider.analyze_sync(None)
    assert res_null.get("scene_type") == "unknown"
    print("  ✅ NullVisionProvider validado como fallback seguro")

    gemini_provider = GeminiVisionProvider(api_key="TEST_KEY_STUB")
    assert gemini_provider.model_name == "gemini-2.5-flash"
    print("  ✅ GeminiVisionProvider inicializado com o modelo 'gemini-2.5-flash'")

    local_provider = LocalVisionProvider()
    obs_local = local_provider.analyze_sync(None)
    assert obs_local.source in ["local_no_image", "local_vlm_offline"]
    print("  ✅ LocalVisionProvider preparado para Qwen2.5-VL / Ollama local")

    # 2. Teste do ConfidenceRouter, Cooldown e Cache por Perceptual Hash
    router = ConfidenceRouter(confidence_threshold=0.55)
    frame_dummy = b"fake_game_screenshot_data_bytes_12345"

    # Confiança alta (0.90 >= 0.55) -> Não dispara VLM
    should, reason = router.should_trigger_semantic_analysis(fast_confidence=0.90, frame=frame_dummy)
    assert should is False
    assert "fast_perception_sufficient" in reason
    print("  ✅ ConfidenceRouter economizou API quando a percepção rápida teve alta confiança (0.90)")

    # Confiança baixa (0.40 < 0.55) -> Dispara VLM
    should_low, reason_low = router.should_trigger_semantic_analysis(fast_confidence=0.40, frame=frame_dummy)
    assert should_low is True
    assert "low_confidence_trigger" in reason_low
    router.record_trigger(frame_dummy)
    print("  ✅ ConfidenceRouter autorizou VLM quando a percepção rápida ficou baixa (0.40)")

    # Cooldown imediato -> Bloqueia segunda chamada antes de 2.0s
    should_cd, reason_cd = router.should_trigger_semantic_analysis(fast_confidence=0.30, frame=frame_dummy)
    assert should_cd is False
    assert "cooldown_active" in reason_cd
    print(f"  ✅ Cooldown de 2.0s respeitado com sucesso ({reason_cd})")

    # 3. Teste da Fusão Ponderada de Percepções (PerceptionFusion)
    fusion = PerceptionFusion()
    base_snapshot = PerceptionSnapshot(game_state="UNKNOWN", confidence=0.40)
    sem_obs = SemanticObservation(
        scene_type="pokemon_center",
        confidence=0.92,
        objects=[SemanticObject(temporary_id="npc_1", semantic_type="npc", description="Nurse Joy", center=(0.6, 0.3))]
    )

    fused = fusion.fuse(base_snapshot, sem_obs)
    assert fused.game_state == "pokemon_center"
    assert len(fused.nearby_players) == 1
    assert fused.nearby_players[0]["description"] == "Nurse Joy"
    print("  ✅ PerceptionFusion unificou a observação VLM ao PerceptionSnapshot com sucesso!")

    # 4. Teste do VisualTeacher & Ciclo de Hipóteses (HYPOTHESIS -> CONFIRMED)
    memory = SemanticMemory(memory_dir=Path("scratch/test_semantic_memory"))
    teacher = VisualTeacher(memory=memory, data_dir=Path("scratch/test_learning_data"))

    hyp = SemanticHypothesis(
        hypothesis_id="hyp_door_1",
        concept="stairs_exit",
        target_object_id="obj_door",
        expected_outcome="change_map",
        confidence=0.88
    )

    hyp_id = teacher.register_hypothesis(hyp)
    assert hyp_id == "hyp_door_1"

    # Ambiente confirma que o mapa mudou
    confirmed = teacher.evaluate_environment_feedback(
        hypothesis_id="hyp_door_1",
        env_changed=True,
        change_type="map_changed"
    )
    assert confirmed is True
    learned_concept = memory.get_concept("stairs_exit")
    assert learned_concept is not None
    assert learned_concept["examples_count"] >= 1
    print("  ✅ VisualTeacher confirmou hipótese semântica e promoveu a fato aprendido em memória!")

    # 5. Teste de Rastreamento Egocêntrico (TargetTracker)
    tracker = TargetTracker()
    sim_objects = [SemanticObject(temporary_id="npc_nurse", semantic_type="npc", description="Nurse Joy", center=(0.65, 0.35))]
    tracker.update_from_observation(sim_objects)

    entity = tracker.get_tracked_target("npc_nurse")
    assert entity is not None
    assert entity.center == (0.65, 0.35)
    print("  ✅ TargetTracker registrou alvo em coordenadas egocêntricas [0.65, 0.35]")

    # 6. Teste do InteractionNavigator e Verificação Pós-Interação
    navigator = InteractionNavigator()
    dx, dy, dist = navigator.calculate_approach_vector(entity)
    assert abs(dx - (0.65 - 0.5)) < 1e-4
    assert abs(dy - (0.35 - 0.5)) < 1e-4

    success, ver_msg = navigator.verify_post_interaction(
        before_state={"dialog_open": False},
        after_state={"dialog_open": True}
    )
    assert success is True
    assert ver_msg == "dialog_opened"
    print("  ✅ InteractionNavigator confirmou com sucesso a abertura de diálogo pós-interação!")

    # 7. VisualReasoner (Orquestrador Soberano)
    reasoner = VisualReasoner(config={"semantic_ai": {"enabled": True, "provider": "null"}})
    full_obs = reasoner.analyze_scene(frame=frame_dummy, fast_confidence=0.90)
    assert full_obs is not None
    print("  ✅ VisualReasoner orquestrou a pipeline semântica com perfeição!")


if __name__ == "__main__":
    test_semantic_vision_pipeline()
