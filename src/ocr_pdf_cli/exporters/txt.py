"""Exportador para formato de texto simples (TXT)."""

from pathlib import Path
from ocr_pdf_cli.models.document import Document

class TXTExporter:
    """Exporta o conteúdo textual do Document para um arquivo .txt."""

    def export(self, document: Document, output_path: Path) -> None:
        """Gera um arquivo de texto a partir do Document.

        Cada página é separada por uma marcação visível de quebra de página.
        
        Args:
            document: O modelo de documento processado.
            output_path: Caminho do arquivo de destino.
        """
        pages_text = []
        for page in document.pages:
            if page.ocr_result:
                text = page.ocr_result.text.strip()
                pages_text.append(text if text else f"[Página {page.page_number} sem texto]")
            else:
                pages_text.append(f"[Página {page.page_number} sem resultado de OCR]")

        # Junta as páginas com uma marcação limpa
        delimiter = "\n\n" + "-" * 40 + "\n\n"
        full_text = delimiter.join(pages_text) + "\n"
        
        output_path.write_text(full_text, encoding="utf-8")
