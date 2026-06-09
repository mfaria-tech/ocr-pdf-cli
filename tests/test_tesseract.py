"""Testes unitários da engine Tesseract."""

from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from ocr_pdf_cli.engines.tesseract import TesseractEngine

@patch("ocr_pdf_cli.engines.tesseract.pytesseract.get_tesseract_version")
def test_tesseract_available(mock_get_ver: MagicMock) -> None:
    """Verifica se reporta is_available = True quando o tesseract está instalado."""
    mock_get_ver.return_value = "5.3.0"
    engine = TesseractEngine()
    assert engine.is_available is True

@patch("ocr_pdf_cli.engines.tesseract.pytesseract.get_tesseract_version", side_effect=Exception("not found"))
def test_tesseract_unavailable(mock_get_ver: MagicMock) -> None:
    """Verifica se reporta is_available = False quando ocorre falha ao acessar o tesseract."""
    engine = TesseractEngine()
    assert engine.is_available is False

@patch("ocr_pdf_cli.engines.tesseract.pytesseract.get_tesseract_version", return_value="5.3.0")
@patch("ocr_pdf_cli.engines.tesseract.pytesseract.image_to_string", return_value="Texto Extraído")
def test_tesseract_extract_text(mock_to_str: MagicMock, mock_get_ver: MagicMock) -> None:
    """Verifica a extração simples de texto."""
    engine = TesseractEngine()
    img = Image.new("L", (10, 10))
    text = engine.extract_text(img, "por")
    
    assert text == "Texto Extraído"
    mock_to_str.assert_called_once_with(img, lang="por")

@patch("ocr_pdf_cli.engines.tesseract.pytesseract.get_tesseract_version", return_value="5.3.0")
@patch("ocr_pdf_cli.engines.tesseract.pytesseract.image_to_string", return_value="Texto Extraído")
@patch("ocr_pdf_cli.engines.tesseract.pytesseract.image_to_data")
def test_tesseract_extract_page(mock_to_data: MagicMock, mock_to_str: MagicMock, mock_get_ver: MagicMock) -> None:
    """Verifica a extração estruturada da página com coordenadas das palavras."""
    # Simula dicionário de retorno de image_to_data
    mock_to_data.return_value = {
        "level": [1, 5, 5],
        "left": [0, 10, 30],
        "top": [0, 15, 15],
        "width": [100, 20, 25],
        "height": [100, 12, 12],
        "conf": [-1.0, 95.0, 80.0],
        "text": ["", "Texto", "Extraído"]
    }
    
    engine = TesseractEngine()
    img = Image.new("L", (100, 100))
    result = engine.extract_page(img, "por", 1)
    
    assert result.text == "Texto Extraído"
    assert len(result.words) == 2
    assert result.words[0].text == "Texto"
    assert result.words[0].left == 10
    assert result.words[0].top == 15
    assert result.words[0].confidence == 95.0
    assert result.words[1].text == "Extraído"
    assert result.words[1].confidence == 80.0
    assert result.confidence == 87.5  # média de 95 e 80
