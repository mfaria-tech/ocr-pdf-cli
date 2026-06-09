"""Utilitários de sistema e ambiente operacional."""

import os
import platform
import shutil
import sys
from typing import Dict, Any

def get_system_info() -> Dict[str, Any]:
    """Retorna detalhes do ambiente operacional para ajudar no suporte multiplataforma.

    Retorna:
        Dicionário com sistema operacional, versão do python e detecção de Termux (Android).
    """
    is_termux = (
        "TERMUX_VERSION" in os.environ 
        or "com.termux" in sys.executable 
        or shutil.which("termux-setup-storage") is not None
    )
    
    # Determinar nome amigável do OS
    os_name = sys.platform
    if os_name == "win32":
        friendly_os = "Windows"
    elif os_name == "darwin":
        friendly_os = "macOS"
    elif os_name.startswith("linux"):
        friendly_os = "Termux (Android)" if is_termux else "Linux"
    else:
        friendly_os = platform.system() or "Desconhecido"

    return {
        "os": os_name,
        "friendly_os": friendly_os,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "is_termux": is_termux,
    }
