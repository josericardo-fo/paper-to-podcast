import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from config import PDF_DIR
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFProcessor:
    """
    Gerencia o processamento de arquivos PDF, incluindo carregamento,
    armazenamento e extração de conteúdo.
    """

    @staticmethod
    def get_all_pdfs() -> List[Path]:
        """Retorna lista de todos os PDFs armazenados."""
        return list(PDF_DIR.glob("*.pdf"))

    @staticmethod
    def save_pdf(filepath: str) -> Path:
        """
        Salva um PDF no diretório de PDFs.
        Retorna o caminho do arquivo salvo.
        """
        source_path = Path(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_filename = f"{timestamp}_{source_path.name}"
        dest_path = PDF_DIR / dest_filename

        shutil.copy2(source_path, dest_path)
        return dest_path

    @staticmethod
    def extract_text(pdf_path: Path) -> List[Document]:
        """
        Extrai texto do PDF usando PyPDFLoader.
        Retorna lista de documentos Langchain.
        """
        try:
            loader = PyPDFLoader(str(pdf_path))
            return loader.load()
        except Exception as e:
            print(f"Erro ao extrair texto do PDF: {e}")
            return []

    @staticmethod
    def get_pdf_metadata(pdf_path: Path) -> dict:
        """Extrai metadados do PDF."""
        # Implementar extração de metadados quando necessário
        return {
            "filename": pdf_path.name,
            "size_kb": round(pdf_path.stat().st_size / 1024, 2),
            "created_date": datetime.fromtimestamp(pdf_path.stat().st_ctime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
