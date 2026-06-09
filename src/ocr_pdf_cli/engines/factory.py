"""Factory de engines OCR — ponto central de criação e descoberta de engines."""

from typing import List

from ocr_pdf_cli.engines.base import OCREngine
from ocr_pdf_cli.engines.tesseract import TesseractEngine
from ocr_pdf_cli.engines.easyocr import EasyOCREngine
from ocr_pdf_cli.engines.paddleocr import PaddleOCREngine

# Registro central de engines disponíveis no projeto
_ENGINE_REGISTRY: dict[str, type[OCREngine]] = {
    "tesseract": TesseractEngine,
    "easyocr": EasyOCREngine,
    "paddleocr": PaddleOCREngine,
}


def create_engine(name: str) -> OCREngine:
    """Cria e retorna uma instância da engine especificada.

    Ponto central de criação de engines — elimina if/else espalhados pelo projeto.

    Args:
        name: Identificador da engine (ex: 'tesseract', 'easyocr', 'paddleocr').

    Returns:
        Nova instância da engine correspondente.

    Raises:
        ValueError: Se o nome da engine for desconhecido.

    Examples:
        >>> engine = create_engine("tesseract")
        >>> engine = create_engine("easyocr")
        >>> engine = create_engine("paddleocr")
    """
    normalized = name.strip().lower()
    if normalized not in _ENGINE_REGISTRY:
        valid = ", ".join(f"'{k}'" for k in _ENGINE_REGISTRY)
        raise ValueError(
            f"Engine desconhecida '{name}'. Engines suportadas: {valid}"
        )
    return _ENGINE_REGISTRY[normalized]()


def supported_engines() -> List[str]:
    """Retorna a lista de todas as engines registradas no projeto.

    Inclui engines indisponíveis no ambiente atual.

    Returns:
        Lista de nomes de engines registradas.
    """
    return list(_ENGINE_REGISTRY.keys())


def available_engines() -> List[str]:
    """Retorna apenas as engines disponíveis no ambiente atual.

    Uma engine é considerada disponível se seu método `is_available` retornar True
    (executável/biblioteca instalada e acessível).

    Returns:
        Lista de nomes de engines disponíveis.
    """
    result: List[str] = []
    for name, cls in _ENGINE_REGISTRY.items():
        try:
            if cls().is_available:
                result.append(name)
        except Exception:
            pass
    return result


__all__ = [
    "create_engine",
    "supported_engines",
    "available_engines",
    "_ENGINE_REGISTRY",
]
