"""Módulo de escrita de PDFs pesquisáveis."""

from pathlib import Path
from ocr_pdf_cli.models.document import Document
from ocr_pdf_cli.exporters.pdf import PDFExporter

class PDFWriter:
    """Orquestra a escrita física de um PDF pesquisável a partir de um Document."""

    def __init__(self) -> None:
        self.exporter = PDFExporter()

    def write(self, document: Document, output_path: Path) -> None:
        """Gera o arquivo PDF de saída no local especificado.

        Args:
            document: Documento contendo as imagens e dados das palavras mapeadas pelo OCR.
            output_path: Local onde o PDF final será salvo.
        """
        self.exporter.export(document, output_path)
