"""
Visual Grounder - Mapeador de Coordenadas Visuais para Espaço de Jogo
======================================================================

Converte coordenadas normalizadas [0..1] retornadas pelo VLM em coordenadas de pixel
e offsets de tiles egocêntricos em relação ao centro (0.5, 0.5) do jogador.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from typing import Tuple, Optional, Any, Dict


class VisualGrounder:
    """
    Ancorador visual de coordenadas normais para espaço de pixels e grade do jogo.
    """

    @staticmethod
    def normalized_to_pixel(center_norm: Tuple[float, float], frame_size: Tuple[int, int]) -> Tuple[int, int]:
        """Converte coordenadas normais (x_norm, y_norm) [0..1] em pixels (x_px, y_px)."""
        width, height = frame_size
        x_px = int(center_norm[0] * width)
        y_px = int(center_norm[1] * height)
        return x_px, y_px

    @staticmethod
    def bbox_to_pixel_rect(bbox_norm: Tuple[float, float, float, float], frame_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Converte bbox normalizado (ymin, xmin, ymax, xmax) em retângulo de pixels (x, y, w, h)."""
        width, height = frame_size
        ymin, xmin, ymax, xmax = bbox_norm
        x = int(xmin * width)
        y = int(ymin * height)
        w = int((xmax - xmin) * width)
        h = int((ymax - ymin) * height)
        return x, y, w, h

    @staticmethod
    def to_egocentric_tile_offset(center_norm: Tuple[float, float], tile_size_pct: float = 0.05) -> Tuple[int, int]:
        """Converte ponto normalizado em offset de tiles em relação ao centro (0.5, 0.5)."""
        dx_pct = center_norm[0] - 0.5
        dy_pct = center_norm[1] - 0.5
        tile_x = round(dx_pct / tile_size_pct)
        tile_y = round(dy_pct / tile_size_pct)
        return tile_x, tile_y
