"""Engine OCR baseada em EasyOCR."""

import logging
import numpy as np
from typing import List, Optional, TYPE_CHECKING

from PIL import Image

from ocr_pdf_cli.engines.base import OCREngine
from ocr_pdf_cli.models.ocr_result import OCRResult, OCRWord

if TYPE_CHECKING:
    import easyocr  # type: ignore

logger = logging.getLogger("ocr_pdf_cli")

# Mapeamento de códigos de idioma para o formato aceito pelo EasyOCR
_LANG_MAP: dict[str, str] = {
    "por": "pt",
    "eng": "en",
    "spa": "es",
    "fra": "fr",
    "pt": "pt",
    "en": "en",
    "es": "es",
    "fr": "fr",
}


class EasyOCREngine(OCREngine):
    """Engine OCR que utiliza a biblioteca EasyOCR com lazy loading e cache do Reader.

    O modelo é carregado somente quando a engine é utilizada pela primeira vez,
    evitando sobrecarga desnecessária no import do módulo.
    """

    def __init__(self) -> None:
        """Inicializa a engine sem carregar o modelo."""
        self._reader: Optional["easyocr.Reader"] = None
        self._reader_lang: Optional[str] = None

    @property
    def name(self) -> str:
        """Retorna o identificador da engine."""
        return "easyocr"

    @property
    def is_available(self) -> bool:
        """Verifica se o pacote easyocr está instalado."""
        try:
            import easyocr  # type: ignore  # noqa: F401
            return True
        except ImportError:
            return False

    def _map_lang(self, lang: str) -> str:
        """Converte código de idioma para o formato EasyOCR.

        Args:
            lang: Código no estilo Tesseract ('por', 'eng', etc.).

        Returns:
            Código de idioma aceito pelo EasyOCR ('pt', 'en', etc.).
        """
        return _LANG_MAP.get(lang.lower(), lang)

    def _get_reader(self, lang: str) -> "easyocr.Reader":
        """Retorna o Reader EasyOCR, criando-o na primeira chamada (lazy loading).

        O Reader é cacheado e reutilizado enquanto o idioma não mudar.

        Args:
            lang: Código do idioma (será convertido internamente).

        Returns:
            Instância de easyocr.Reader pronta para uso.

        Raises:
            RuntimeError: Se o EasyOCR não estiver instalado.
        """
        if not self.is_available:
            raise RuntimeError(
                "EasyOCR não está instalado. Instale com: pip install ocr-pdf-cli[easyocr]"
            )

        mapped_lang = self._map_lang(lang)

        # Reutiliza Reader existente se o idioma for o mesmo
        if self._reader is None or self._reader_lang != mapped_lang:
            import easyocr  # type: ignore

            logger.info(f"Carregando modelo EasyOCR para idioma: '{mapped_lang}'...")
            self._reader = easyocr.Reader(
                lang_list=[mapped_lang],
                gpu=False,  # Seguro para ambientes sem GPU
                verbose=False,
            )
            self._reader_lang = mapped_lang
            logger.info("Modelo EasyOCR carregado com sucesso.")

        return self._reader

    def _pil_to_numpy(self, image: Image.Image) -> np.ndarray:
        """Converte imagem PIL para array NumPy RGB aceito pelo EasyOCR.

        Args:
            image: Imagem PIL de entrada.

        Returns:
            Array NumPy no formato RGB.
        """
        img = image.convert("RGB")
        return np.array(img)

    def extract_text(self, image: Image.Image, lang: str) -> str:
        """Extrai texto puro de uma imagem usando EasyOCR.

        Args:
            image: Imagem PIL da página.
            lang: Código do idioma (ex: 'por', 'eng').

        Returns:
            Texto concatenado extraído da imagem.

        Raises:
            RuntimeError: Se o EasyOCR não estiver instalado ou ocorrer falha.
        """
        reader = self._get_reader(lang)
        img_array = self._pil_to_numpy(image)

        try:
            results = reader.readtext(img_array, detail=0, paragraph=True)
            return "\n".join(str(r) for r in results)
        except Exception as e:
            logger.error(f"Erro ao extrair texto com EasyOCR: {e}")
            raise RuntimeError(f"Falha no processamento do EasyOCR: {e}") from e

    def extract_page(self, image: Image.Image, lang: str, page_number: int) -> OCRResult:
        """Realiza extração estruturada de OCR de uma página com bounding boxes.

        Args:
            image: Imagem PIL da página.
            lang: Código do idioma.
            page_number: Número da página (1-indexed).

        Returns:
            OCRResult contendo texto, palavras com coordenadas e confiança média.

        Raises:
            RuntimeError: Se o EasyOCR não estiver instalado ou ocorrer falha.
        """
        reader = self._get_reader(lang)
        img_array = self._pil_to_numpy(image)

        try:
            # detail=1 retorna lista de [bbox, text, confidence]
            raw_results = reader.readtext(img_array, detail=1)
        except Exception as e:
            logger.error(f"Erro ao processar página {page_number} com EasyOCR: {e}")
            raise RuntimeError(f"Falha no EasyOCR (página {page_number}): {e}") from e

        words: List[OCRWord] = []
        texts: List[str] = []
        confidences: List[float] = []

        for item in raw_results:
            # Formato: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], text, confidence]
            bbox, text, confidence = item
            text = str(text).strip()
            if not text:
                continue

            # Converter 4 pontos do bbox para left/top/width/height
            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            left = int(min(xs))
            top = int(min(ys))
            width = int(max(xs) - min(xs))
            height = int(max(ys) - min(ys))

            # EasyOCR retorna confidence entre 0 e 1; normalizar para 0-100
            conf_pct = float(confidence) * 100.0

            words.append(
                OCRWord(
                    text=text,
                    left=left,
                    top=top,
                    width=max(1, width),
                    height=max(1, height),
                    confidence=conf_pct,
                )
            )
            texts.append(text)
            confidences.append(conf_pct)

        full_text = " ".join(texts)
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
            logger.debug(f"EasyOCR: processando página {idx + 1}/{len(images)}")
            results.append(self.extract_page(img, lang=lang, page_number=idx + 1))
        return results
