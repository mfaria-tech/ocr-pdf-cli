"""Módulo para pós-processamento do texto extraído por OCR."""

import re

class TextPostprocessor:
    """Limpa e formata o texto retornado pelo OCR para remover artefatos comuns."""

    def postprocess(self, text: str) -> str:
        """Limpa o texto extraído do OCR.

        Remove espaços múltiplos, quebras de linhas desnecessárias extras
        e remove caracteres de controle indesejados.

        Args:
            text: Texto bruto retornado pelo OCR.

        Returns:
            Texto formatado e limpo.
        """
        if not text:
            return ""
            
        # Normaliza quebras de linha para \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove quebras de página ou blocos invisíveis indesejados
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)
        
        # Divide em linhas e limpa espaços extras no início e fim de cada uma
        lines = []
        for line in text.split("\n"):
            # Substitui múltiplos espaços por um único
            cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(cleaned_line)
            
        # Junta novamente as linhas mantendo uma estrutura limpa
        result = "\n".join(lines)
        
        # Remove mais de duas quebras de linha seguidas
        result = re.sub(r"\n{3,}", "\n\n", result)
        
        return result.strip()
