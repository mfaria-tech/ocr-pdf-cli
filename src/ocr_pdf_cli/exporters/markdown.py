"""Exportador para formato Markdown (MD)."""

from pathlib import Path
from ocr_pdf_cli.models.document import Document

class MarkdownExporter:
    """Exporta o conteúdo textual do Document estruturado em Markdown."""

    def export(self, document: Document, output_path: Path) -> None:
        """Gera um arquivo Markdown a partir do Document.

        Contém cabeçalhos indicando a origem e páginas correspondentes.

        Args:
            document: O modelo de documento processado.
            output_path: Caminho do arquivo de destino.
        """
        md_lines = []
        md_lines.append(f"# Documento: {Path(document.file_path).name}\n")
        
        for page in document.pages:
            md_lines.append(f"## Página {page.page_number}\n")
            if page.ocr_result:
                text = page.ocr_result.text.strip()
                if text:
                    md_lines.append(text)
                else:
                    md_lines.append("*[Sem texto extraído nesta página]*")
            else:
                md_lines.append("*[Processamento de OCR indisponível]*")
            md_lines.append("\n")

        output_path.write_text("\n".join(md_lines), encoding="utf-8")
