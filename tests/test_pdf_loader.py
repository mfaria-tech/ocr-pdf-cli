"""Testes unitários do carregador de PDFs."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from ocr_pdf_cli.core.pdf_loader import PDFLoader

def test_pdf_loader_file_not_found() -> None:
    """Verifica se lança FileNotFoundError quando o arquivo não existe."""
    loader = PDFLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_pdf(Path("inexistente.pdf"))

@patch("ocr_pdf_cli.core.pdf_loader.pdfium.PdfDocument")
def test_pdf_loader_success(mock_pdf_doc_class: MagicMock, tmp_path: Path) -> None:
    """Verifica se o PDFLoader renderiza as páginas do PDF simulado com sucesso."""
    # Cria arquivo PDF simulado real na pasta temporária para passar na checagem de existência
    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.5")
    
    # Configura mocks para simular um PDF de 2 páginas
    mock_page = MagicMock()
    mock_page.get_size.return_value = (595.0, 842.0)  # tamanho A4 em pontos
    
    mock_bitmap = MagicMock()
    dummy_image = Image.new("RGB", (100, 100))
    mock_bitmap.to_pil.return_value = dummy_image
    mock_page.render.return_value = mock_bitmap
    
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 2
    mock_doc.get_page.side_effect = lambda idx: mock_page
    mock_pdf_doc_class.return_value = mock_doc
    
    # Executa o loader
    loader = PDFLoader()
    doc_model, images = loader.load_pdf(dummy_pdf, dpi=300)
    
    # Asserções
    assert len(images) == 2
    assert doc_model.metadata["pages_count"] == 2
    assert len(doc_model.pages) == 2
    assert doc_model.pages[0].page_number == 1
    assert doc_model.pages[0].width == 595
    assert doc_model.pages[0].height == 842
    assert images[0] == dummy_image


@patch("ocr_pdf_cli.core.pipeline.get_engine")
@patch("ocr_pdf_cli.core.pipeline.PDFLoader")
def test_ocr_pipeline_run(mock_loader_class: MagicMock, mock_get_engine: MagicMock, tmp_path: Path) -> None:
    """Verifica a execução integrada do OCRPipeline."""
    # Setup mock loader
    mock_loader = MagicMock()
    mock_loader_class.return_value = mock_loader
    
    from ocr_pdf_cli.models.document import Document
    from ocr_pdf_cli.models.page import Page
    from ocr_pdf_cli.models.ocr_result import OCRResult, OCRWord
    
    mock_doc = Document(file_path="mock.pdf")
    mock_page = Page(page_number=1, width=100, height=100)
    mock_doc.pages.append(mock_page)
    
    dummy_image = Image.new("RGB", (100, 100), color="white")
    mock_loader.load_pdf.return_value = (mock_doc, [dummy_image])
    
    # Setup mock engine
    mock_engine = MagicMock()
    mock_engine.is_available = True
    mock_engine.extract_page.return_value = OCRResult(
        text="Texto do Pipeline",
        words=[OCRWord(text="Texto", left=0, top=0, width=10, height=10, confidence=90.0)],
        confidence=90.0,
        language="por"
    )
    mock_get_engine.return_value = mock_engine
    
    # Instancia o pipeline
    from ocr_pdf_cli.core.pipeline import OCRPipeline
    pipeline = OCRPipeline(engine_name="tesseract", language="por", dpi=150)
    
    input_file = tmp_path / "mock.pdf"
    input_file.write_bytes(b"%PDF-1.5")
    
    output_dir = tmp_path / "output"
    
    # Testa exportação em TXT
    out_txt = pipeline.run(input_file, output_dir, output_format="txt")
    assert out_txt.exists()
    assert "Texto do Pipeline" in out_txt.read_text(encoding="utf-8")
    
    # Testa exportação em PDF
    out_pdf = pipeline.run(input_file, output_dir, output_format="pdf")
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0

