"""Engine OCR baseada em PaddleOCR."""

import logging
import numpy as np
from typing import List, Optional, Any, TYPE_CHECKING

from PIL import Image

from ocr_pdf_cli.engines.base import OCREngine
from ocr_pdf_cli.models.ocr_result import OCRResult, OCRWord

if TYPE_CHECKING:
    from paddleocr import PaddleOCR  # type: ignore

logger = logging.getLogger("ocr_pdf_cli")

# Mapeamento de código de idioma para o formato aceito pelo PaddleOCR
_LANG_MAP: dict[str, str] = {
    "por": "pt",
    "eng": "en",
    "pt": "pt",
    "en": "en",
}


class PaddleOCREngine(OCREngine):
    """Engine OCR que utiliza a biblioteca PaddleOCR com lazy loading e cache do modelo.

    O modelo é carregado somente quando a engine é utilizada pela primeira vez,
    evitando sobrecarga desnecessária no import do módulo.
    """

    def __init__(self) -> None:
        """Inicializa a engine sem carregar o modelo."""
        self._ocr: Optional[Any] = None
        self._ocr_lang: Optional[str] = None

    @property
    def name(self) -> str:
        """Retorna o identificador da engine."""
        return "paddleocr"

    @property
    def is_available(self) -> bool:
        """Verifica se o pacote paddleocr está instalado."""
        try:
            import paddleocr  # type: ignore  # noqa: F401
            return True
        except ImportError:
            return False

    def _map_lang(self, lang: str) -> str:
        """Converte código de idioma para o formato PaddleOCR.

        Args:
            lang: Código no estilo Tesseract ('por', 'eng', etc.).

        Returns:
            Código de idioma aceito pelo PaddleOCR ('pt', 'en', etc.).
        """
        return _LANG_MAP.get(lang.lower(), "en")

    def _get_ocr(self, lang: str) -> "PaddleOCR":
        """Retorna o objeto PaddleOCR, criando-o na primeira chamada (lazy loading).

        O objeto é cacheado e reutilizado enquanto o idioma não mudar.

        Args:
            lang: Código do idioma (será convertido internamente).

        Returns:
            Instância de PaddleOCR pronta para uso.

        Raises:
            RuntimeError: Se o PaddleOCR não estiver instalado.
        """
        if not self.is_available:
            raise RuntimeError(
                "PaddleOCR não está instalado. Instale com: pip install ocr-pdf-cli[paddleocr]"
            )

        mapped_lang = self._map_lang(lang)

        # Reutiliza instância existente se o idioma for o mesmo
        if self._ocr is None or self._ocr_lang != mapped_lang:
            from paddleocr import PaddleOCR  # type: ignore

            logger.info(f"Carregando modelo PaddleOCR para idioma: '{mapped_lang}'...")
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=mapped_lang,
                show_log=False,
                use_gpu=False,
            )
            self._ocr_lang = mapped_lang
            logger.info("Modelo PaddleOCR carregado com sucesso.")

        return self._ocr  # type: ignore[return-value]

    def _pil_to_numpy(self, image: Image.Image) -> np.ndarray:
        """Converte imagem PIL para array NumPy RGB aceito pelo PaddleOCR.

        Args:
            image: Imagem PIL de entrada.

        Returns:
            Array NumPy no formato RGB.
        """
        return np.array(image.convert("RGB"))

    def _bbox_to_rect(self, bbox: List[List[float]]) -> tuple[int, int, int, int]:
        """Converte bounding box de 4 pontos para left/top/width/height.

        O PaddleOCR retorna 4 pontos [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] enquanto
        o modelo OCRWord espera left/top/width/height.

        Args:
            bbox: Lista de 4 pontos representando os cantos da caixa.

        Returns:
            Tupla (left, top, width, height) em pixels inteiros.
        """
        xs = [float(pt[0]) for pt in bbox]
        ys = [float(pt[1]) for pt in bbox]
        left = int(min(xs))
        top = int(min(ys))
        width = int(max(xs) - min(xs))
        height = int(max(ys) - min(ys))
        return left, top, max(1, width), max(1, height)

    def extract_text(self, image: Image.Image, lang: str) -> str:
        """Extrai texto puro de uma imagem usando PaddleOCR.

        Args:
            image: Imagem PIL da página.
            lang: Código do idioma (ex: 'por', 'eng').

        Returns:
            Texto concatenado extraído da imagem.

        Raises:
            RuntimeError: Se o PaddleOCR não estiver instalado ou ocorrer falha.
        """
        ocr = self._get_ocr(lang)
        img_array = self._pil_to_numpy(image)

        try:
            raw_results = ocr.ocr(img_array, cls=True)
        except Exception as e:
            logger.error(f"Erro ao extrair texto com PaddleOCR: {e}")
            raise RuntimeError(f"Falha no processamento do PaddleOCR: {e}") from e

        texts: List[str] = []
        if raw_results:
            for page_results in raw_results:
                if page_results:
                    for line in page_results:
                        # Formato: [bbox, (text, confidence)]
                        text = str(line[1][0]).strip()
                        if text:
                            texts.append(text)
        return "\n".join(texts)

    def extract_page(self, image: Image.Image, lang: str, page_number: int) -> OCRResult:
        """Realiza extração estruturada de OCR de uma página com bounding boxes.

        Args:
            image: Imagem PIL da página.
            lang: Código do idioma.
            page_number: Número da página (1-indexed).

        Returns:
            OCRResult contendo texto, palavras com coordenadas e confiança média.

        Raises:
            RuntimeError: Se o PaddleOCR não estiver instalado ou ocorrer falha.
        """
        ocr = self._get_ocr(lang)
        img_array = self._pil_to_numpy(image)

        try:
            raw_results = ocr.ocr(img_array, cls=True)
        except Exception as e:
            logger.error(f"Erro ao processar página {page_number} com PaddleOCR: {e}")
            raise RuntimeError(f"Falha no PaddleOCR (página {page_number}): {e}") from e

        words: List[OCRWord] = []
        texts: List[str] = []
        confidences: List[float] = []

        if raw_results:
            for page_results in raw_results:
                if page_results:
                    for line in page_results:
                        # Formato: [[[x1,y1],...,[x4,y4]], (text, confidence)]
                        bbox = line[0]
                        text = str(line[1][0]).strip()
                        confidence = float(line[1][1])

                        if not text:
                            continue

                        left, top, width, height = self._bbox_to_rect(bbox)

                        # PaddleOCR retorna confidence entre 0 e 1; normalizar para 0-100
                        conf_pct = confidence * 100.0

                        words.append(
                            OCRWord(
                                text=text,
                                left=left,
                                top=top,
                                width=width,
                                height=height,
                                confidence=conf_pct,
                            )
                        )
                        texts.append(text)
                        confidences.append(conf_pct)

        full_text = "\n".join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            text=full_text,
            words=words,
            confidence=avg_confidence,
            language=lang,
        )

    def extract_document(self, images: List[Image.Image], lang: str) -> List[OCRResult]:
        """Processa uma lista de imagens gerando OCRResult para cada página.

        Args:
            images: Lista de imagens PIL das páginas.
            lang: Código do idioma.

        Returns:
            Lista de OCRResult correspondente a cada página.
        """
        results: List[OCRResult] = []
        for idx, img in enumerate(images):
            logger.debug(f"PaddleOCR: processando página {idx + 1}/{len(images)}")
            results.append(self.extract_page(img, lang=lang, page_number=idx + 1))
        return results
