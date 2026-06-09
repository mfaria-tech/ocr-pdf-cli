"""Testes unitários de pré-processamento de imagem e pós-processamento de texto."""

from PIL import Image
from ocr_pdf_cli.core.image_preprocessor import ImagePreprocessor
from ocr_pdf_cli.core.text_postprocessor import TextPostprocessor

def test_image_preprocessor_grayscale() -> None:
    """Verifica se a conversão para escala de cinza funciona."""
    preprocessor = ImagePreprocessor()
    # Cria imagem RGB vermelha de 10x10
    img = Image.new("RGB", (10, 10), color="red")
    
    processed = preprocessor.preprocess(img, grayscale=True, binarize=False)
    assert processed.mode == "L"

def test_image_preprocessor_binarize() -> None:
    """Verifica se a binarização retorna uma imagem P&B puro."""
    preprocessor = ImagePreprocessor()
    img = Image.new("RGB", (10, 10), color="gray")
    
    processed = preprocessor.preprocess(img, grayscale=True, binarize=True, threshold=128)
    assert processed.mode == "1"

def test_text_postprocessor_cleanup() -> None:
    """Verifica se remove caracteres inúteis, espaços extras e quebras excessivas."""
    postprocessor = TextPostprocessor()
    raw_text = "  Olá   mundo!  \n\n\n\nPróxima   linha.\r\nOutra linha.\x00"
    
    cleaned = postprocessor.postprocess(raw_text)
    
    assert "Olá mundo!" in cleaned
    assert "Próxima linha." in cleaned
    assert "Outra linha." in cleaned
    # Garante que reduziu quebras excessivas para no máximo duas (\n\n)
    assert "\n\n\n" not in cleaned
    # Garante que removeu caracteres nulos
    assert "\x00" not in cleaned
