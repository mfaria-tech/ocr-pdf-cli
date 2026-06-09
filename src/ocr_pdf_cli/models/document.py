"""Modelo de documento."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from .page import Page

class Document(BaseModel):
    """Representa um documento completo a ser processado ou já processado."""
    
    file_path: str = Field(..., description="Caminho do arquivo do documento original")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados gerais do documento")
    pages: List[Page] = Field(default_factory=list, description="Lista de páginas contidas no documento")
