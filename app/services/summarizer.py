import json
import time
from pathlib import Path
from typing import Any, Dict, List

from config import OPENAI_MODEL, SUMMARY_DIR, llm
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from prompts import combine_prompt_template, map_prompt_template, stuff_template

from services.pdf_processor import PDFProcessor


class Summarizer:
    """
    Responsável por gerar resumos de documentos usando LLMs.
    """

    def __init__(self):
        self.llm = llm

    def stuff(self, pdf_path: Path, chunks: List[Document] = None) -> Dict[str, Any]:
        """
        Resume um PDF usando o modelo de "stuff".
        Retorna um dicionário com o texto resumido e metadados.

        Args:
            pdf_path: Caminho para o arquivo PDF
            chunks: Lista de documentos já extraídos (opcional)
        """
        if chunks is None:
            chunks = PDFProcessor.extract_text(pdf_path)

        if not chunks:
            return {"error": "Não foi possível extrair texto do PDF"}

        prompt = PromptTemplate(template=stuff_template, input_variables=["text"])

        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="stuff",
            prompt=prompt,
            verbose=True,
        )

        start_time = time.time()
        summary = chain.invoke(chunks)
        execution_time = time.time() - start_time

        result = {
            "summary": summary["output_text"],
            "metadata": {
                "source_file": pdf_path.name,
                "chunks_processed": len(chunks),
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model_used": OPENAI_MODEL,
            },
        }

        self._save_summary(result, pdf_path)

        return result

    def map_reduce(
        self, pdf_path: Path, chunks: List[Document] = None
    ) -> Dict[str, Any]:
        """
        Resume um PDF usando o modelo de map-reduce.
        Retorna um dicionário com o texto resumido e metadados.

        Args:
            pdf_path: Caminho para o arquivo PDF
            chunks: Lista de documentos já extraídos (opcional)
        """
        if chunks is None:
            chunks = PDFProcessor.extract_text(pdf_path)

        if not chunks:
            return {"error": "Não foi possível extrair texto do PDF"}

        map_prompt = PromptTemplate(
            template=map_prompt_template, input_variables=["text"]
        )

        combine_prompt = PromptTemplate(
            template=combine_prompt_template, input_variables=["text"]
        )

        # Criar e executar a chain de resumo
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True,
        )

        start_time = time.time()
        summary = chain.invoke(chunks)
        execution_time = time.time() - start_time

        result = {
            "summary": summary["output_text"],
            "metadata": {
                "source_file": pdf_path.name,
                "chunks_processed": len(chunks),
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model_used": OPENAI_MODEL,
            },
        }

        self._save_summary(result, pdf_path)

        return result

    def _save_summary(self, summary_data: Dict[str, Any], pdf_path: Path) -> Path:
        """Salva o resumo em um arquivo JSON.

        Args:
            summary_data: Dados do resumo
            pdf_path: Caminho para o arquivo PDF
        """
        base_name = pdf_path.stem
        summary_path = SUMMARY_DIR / f"{base_name}_summary.json"

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        return summary_path
