import logging
import sys
try:
    import pygetwindow as gw
except Exception:
    gw = None


class WindowHandler:
    """
    Gerencia a janela do jogo (PokeOne) com validação de foco e isolamento de entradas.
    """

    def __init__(self, window_title="PokeOne"):
        self.window_title = window_title

    def get_window_rect(self):
        """Retorna (x, y, width, height) da janela do jogo."""
        if gw is None or sys.platform != 'win32':
            return (0, 0, 800, 600)  # Rect fallback seguro em testes
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                return win.left, win.top, win.width, win.height
            return None
        except Exception as e:
            logging.error(f"Erro ao detectar janela '{self.window_title}': {e}")
            return None

    def is_window_active(self) -> bool:
        """Verifica se a janela do jogo está em foco para isolamento de entradas."""
        if gw is None or sys.platform != 'win32':
            return True
        try:
            active_win = gw.getActiveWindow()
            if active_win and self.window_title.lower() in active_win.title.lower():
                return True
            return False
        except Exception:
            return True

    def activate_window(self) -> bool:
        """Traz a janela do jogo para o primeiro plano."""
        if gw is None or sys.platform != 'win32':
            return True
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                win.activate()
                return True
            return False
        except Exception:
            return False

    def get_relative_coords(self, rel_x, rel_y, win_rect):
        """Converte 0.0-1.0 em pixels reais da janela."""
        if not win_rect:
            return int(rel_x * 800), int(rel_y * 600)
        x_base, y_base, w, h = win_rect
        return int(x_base + (rel_x * w)), int(y_base + (rel_y * h))
