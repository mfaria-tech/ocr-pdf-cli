"""Exportador para formato PDF pesquisável."""

from pathlib import Path
from reportlab.pdfgen import canvas  # type: ignore
from ocr_pdf_cli.models.document import Document
from ocr_pdf_cli.config.settings import settings

class PDFExporter:
    """Exporta o documento gerando um novo PDF contendo as imagens originais
    sobrepostas com o texto OCR invisível correspondente (tornando-o pesquisável).
    """

    def export(self, document: Document, output_path: Path) -> None:
        """Gera um PDF pesquisável a partir do Document.

        Args:
            document: O modelo de documento processado contendo imagens e palavras detectadas.
            output_path: Caminho do arquivo de destino.
        """
        # Criar canvas do ReportLab
        c = canvas.Canvas(str(output_path))
        
        # O DPI original configurado (para recalcular escala das coordenadas)
        # Se não estiver no metadata, assume settings.default_dpi (300)
        dpi = document.metadata.get("dpi", settings.default_dpi)
        scale_factor = 72.0 / dpi  # 72 pontos PDF por polegada

        for page in document.pages:
            # Configura o tamanho da página no canvas (em pontos PDF)
            c.setPageSize((page.width, page.height))
            
            # Desenha a imagem correspondente cobrindo toda a página
            if page.image_path and Path(page.image_path).exists():
                c.drawImage(page.image_path, 0, 0, width=page.width, height=page.height)
            
            # Desenha o texto OCR como camada invisível
            if page.ocr_result and page.ocr_result.words:
                # 3 Tr: Modo de renderização de texto PDF "invisível" (neither fill nor stroke text)
                c._code.append("3 Tr")
                
                for word in page.ocr_result.words:
                    # Converte posições de pixels da imagem (300 DPI) para pontos PDF (72 DPI)
                    pts_left = word.left * scale_factor
                    pts_top = word.top * scale_factor
                    pts_width = word.width * scale_factor
                    pts_height = word.height * scale_factor
                    
                    # ReportLab usa coordenadas com Y começando de baixo (0,0 no canto inferior esquerdo)
                    # Tesseract usa Y começando do topo da imagem (0,0 no canto superior esquerdo)
                    # Portanto, Y_bottom = page_height - Y_top - height
                    rl_x = pts_left
                    rl_y = page.height - pts_top - pts_height
                    
                    # Define tamanho da fonte estimado com base na altura da palavra
                    font_size = max(1.0, pts_height)
                    c.setFont("Helvetica", font_size)
                    
                    # Desenha a palavra invisível na posição
                    c.drawString(rl_x, rl_y, word.text)
                
                # Retorna ao modo de renderização normal para evitar efeitos colaterais
                c._code.append("0 Tr")
            
            c.showPage()
            
        c.save()
