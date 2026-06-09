"""Testes unitários dos exportadores (PDF, TXT, MD)."""

from pathlib import Path
import pytest
from ocr_pdf_cli.models.document import Document
from ocr_pdf_cli.models.page import Page
from ocr_pdf_cli.models.ocr_result import OCRResult, OCRWord
from ocr_pdf_cli.exporters.txt import TXTExporter
from ocr_pdf_cli.exporters.markdown import MarkdownExporter
from ocr_pdf_cli.exporters.pdf import PDFExporter
from ocr_pdf_cli.utils.files import temp_dir_context

@pytest.fixture
def sample_document() -> Document:
    """Fixture que fornece um modelo Document preenchido para os testes."""
    doc = Document(file_path="documento_teste.pdf")
    
    # Adiciona página 1
    page1 = Page(page_number=1, width=595, height=842)
    page1.ocr_result = OCRResult(
        text="Esta é a primeira página.",
        words=[
            OCRWord(text="Esta", left=10, top=20, width=30, height=12, confidence=90.0),
            # Adiciona mais palavras mockadas se necessário
        ],
        confidence=90.0,
        language="por"
    )
    
    # Adiciona página 2
    page2 = Page(page_number=2, width=595, height=842)
    page2.ocr_result = OCRResult(
        text="Esta é a segunda página.",
        words=[
            OCRWord(text="Esta", left=10, top=20, width=30, height=12, confidence=85.0),
        ],
        confidence=85.0,
        language="por"
    )
    
    doc.pages.extend([page1, page2])
    return doc

def test_txt_exporter(sample_document: Document) -> None:
    """Verifica a exportação de texto simples (TXT)."""
    exporter = TXTExporter()
    with temp_dir_context() as temp_dir:
        output_file = temp_dir / "output.txt"
        exporter.export(sample_document, output_file)
        
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "Esta é a primeira página." in content
        assert "Esta é a segunda página." in content
        assert "----------------------------------------" in content  # divisor de página

def test_markdown_exporter(sample_document: Document) -> None:
    """Verifica a exportação em Markdown."""
    exporter = MarkdownExporter()
    with temp_dir_context() as temp_dir:
        output_file = temp_dir / "output.md"
        exporter.export(sample_document, output_file)
        
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "# Documento: documento_teste.pdf" in content
        assert "## Página 1" in content
        assert "Esta é a primeira página." in content
        assert "## Página 2" in content

def test_pdf_exporter(sample_document: Document) -> None:
    """Verifica a exportação de PDF pesquisável via ReportLab."""
    exporter = PDFExporter()
    with temp_dir_context() as temp_dir:
        output_file = temp_dir / "output_searchable.pdf"
        
        # Cria imagens temporárias vazias para simular as páginas originais do PDF
        from PIL import Image
        img = Image.new("RGB", (100, 100), color="white")
        
        for idx, page in enumerate(sample_document.pages):
            img_path = temp_dir / f"img_page_{page.page_number}.png"
            img.save(img_path)
            page.image_path = str(img_path)
            
        exporter.export(sample_document, output_file)
        
        assert output_file.exists()
        # Verifica se o arquivo não está vazio e tem cabeçalho de assinatura PDF
        assert output_file.stat().st_size > 0
        with open(output_file, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"
