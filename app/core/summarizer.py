import json
import time
from pathlib import Path
from typing import Any, Dict, List

from config import SUMMARY_DIR, llm
from core.pdf_processor import PDFProcessor
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document


class Summarizer:
    """
    Responsável por gerar resumos de documentos usando LLMs.
    """

    def __init__(self):
        self.llm = llm

    def create_summary(
        self, pdf_path: Path, chunks: List[Document] = None
    ) -> Dict[str, Any]:
        """
        Cria um resumo do PDF usando LLM.
        Retorna um dicionário com o texto resumido e metadados.
        """
        if not chunks:
            chunks = PDFProcessor.extract_text(pdf_path)

        if not chunks:
            return {"error": "Não foi possível extrair texto do PDF"}

        # Template para resumo
        map_prompt_template = """
        Você é um assistente especializado em resumir artigos científicos.
        Resuma o seguinte texto para que um estudante universitário possa entender:

        {text}

        RESUMO CONCISO:
        """

        map_prompt = PromptTemplate(
            template=map_prompt_template, input_variables=["text"]
        )

        # Template para combinação dos resumos
        combine_prompt_template = """
        Você é um assistente especializado em resumir artigos científicos.

        Abaixo estão resumos de diferentes partes de um artigo científico.
        Seu trabalho é combiná-los em um resumo único, coerente e bem estruturado.

        {text}

        Crie um resumo final em português que:
        1. Mantenha a estrutura clássica de um artigo (introdução, metodologia, resultados, conclusão)
        2. Destaque as contribuições principais
        3. Explique a metodologia de forma simples
        4. Apresente os resultados mais importantes
        5. Termine com as conclusões e implicações do trabalho

        RESUMO FINAL:
        """

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
            },
        }

        # Salvar o resumo
        self._save_summary(result, pdf_path)

        return result

    def _save_summary(self, summary_data: Dict[str, Any], pdf_path: Path) -> Path:
        """Salva o resumo em um arquivo JSON."""
        base_name = pdf_path.stem
        summary_path = SUMMARY_DIR / f"{base_name}_summary.json"

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        return summary_path
