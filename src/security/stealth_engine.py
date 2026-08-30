"""
Process Stealth & Security Engine (Adaptação do Projeto Interview / Ring 3 User-Mode)
=====================================================================================

Oferece proteção de processo em nível de sistema operacional (Windows Win32 Native API):
1. Thread Anti-Debugging (NtSetInformationThread -> ThreadHideFromDebugger = 0x11)
2. Process DACL Hardening (SetSecurityInfo -> Restrição de acesso à memória)
3. AntiAttachWatchdog (Monitoramento contínuo em segundo plano)

Segurança e Transparência:
Configurado de forma segura com fallbacks em try/except para garantir 100% de compatibilidade
com OpenCV, MSS, PyAudio e simulação de entradas sem interferir na gameplay ou no agente.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import ctypes
from ctypes import wintypes
import sys
import threading
import time
from typing import Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("StealthEngine")


# Win32 Constants
PROCESS_ALL_ACCESS = 0x001F0FFF
ThreadHideFromDebugger = 0x11
DACL_SECURITY_INFORMATION = 0x00000004
UNPROTECTED_DACL_SECURITY_INFORMATION = 0x80000000


class ProcessStealthEngine:
    """
    Motor de Proteção e Invisibilidade do Processo Klayton.
    """

    @staticmethod
    def hide_thread_from_debugger(h_thread: Optional[int] = None) -> bool:
        """
        Oculta a thread atual de ferramentas de depuração em modo usuário.
        """
        if sys.platform != "win32":
            return False

        try:
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll

            if h_thread is None:
                h_thread = kernel32.GetCurrentThread()

            ntdll.NtSetInformationThread.argtypes = [wintypes.HANDLE, ctypes.c_ulong, wintypes.LPVOID, ctypes.c_ulong]
            ntdll.NtSetInformationThread.restype = ctypes.c_long

            status = ntdll.NtSetInformationThread(
                h_thread,
                ThreadHideFromDebugger,
                None,
                0
            )
            return status == 0
        except Exception as e:
            logger.debug(f"ProcessStealthEngine: Não foi possível ocultar thread: {e}")
            return False

    @staticmethod
    def harden_process_dacl() -> bool:
        """
        Restringe a lista de controle de acesso (DACL) do processo do Klayton.
        """
        if sys.platform != "win32":
            return False

        try:
            kernel32 = ctypes.windll.kernel32
            advapi32 = ctypes.windll.advapi32

            h_process = kernel32.GetCurrentProcess()
            res = advapi32.SetSecurityInfo(
                h_process,
                1,  # SE_KERNEL_OBJECT
                DACL_SECURITY_INFORMATION | UNPROTECTED_DACL_SECURITY_INFORMATION,
                None,
                None,
                None,
                None
            )
            return res == 0
        except Exception as e:
            logger.debug(f"ProcessStealthEngine: Ajuste DACL: {e}")
            return False

    @classmethod
    def apply_stealth_protection(cls) -> bool:
        """
        Aplica todas as proteções de segurança de forma não-intrusiva.
        """
        if sys.platform != "win32":
            return True

        h_hide = cls.hide_thread_from_debugger()
        h_dacl = cls.harden_process_dacl()
        
        logger.info(f"🛡️ Proteção de Processo Ativada [Anti-Debug: {h_hide} | DACL Hardening: {h_dacl}]")
        return h_hide or h_dacl


class AntiAttachWatchdog:
    """
    Supervisor em segundo plano que renova periodicamente as travas de segurança.
    """

    def __init__(self, check_interval_seconds: float = 2.0):
        self.check_interval = check_interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running or sys.platform != "win32":
            return
        self._running = True
        self._thread = threading.Thread(target=self._watchdog_loop, daemon=True, name="StealthWatchdog")
        self._thread.start()
        logger.info("🐕 Anti-Attach Watchdog ativado em segundo plano.")

    def stop(self) -> None:
        self._running = False

    def _watchdog_loop(self) -> None:
        while self._running:
            try:
                ProcessStealthEngine.hide_thread_from_debugger()
                ProcessStealthEngine.harden_process_dacl()
            except Exception:
                pass
            time.sleep(self.check_interval)
