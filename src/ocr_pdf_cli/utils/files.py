"""Utilitários de manipulação de arquivos e diretórios."""

import contextlib
import shutil
import tempfile
from pathlib import Path
from typing import Generator

def get_project_root() -> Path:
    """Retorna o caminho absoluto para o diretório raiz do projeto."""
    return Path(__file__).resolve().parent.parent.parent.parent

@contextlib.contextmanager
def temp_dir_context() -> Generator[Path, None, None]:
    """Gerenciador de contexto que cria e limpa automaticamente um diretório temporário.

    Yields:
        Path: O caminho absoluto do diretório temporário gerado.
    """
    temp_dir = tempfile.mkdtemp(prefix="ocr_pdf_cli_")
    temp_path = Path(temp_dir)
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)
