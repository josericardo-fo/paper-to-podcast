from pathlib import Path

from config import PDF_DIR
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from services.pdf_processor import PDFProcessor
from services.summarizer import Summarizer

summarizer = Summarizer()

app = FastAPI(
    title="Paper-to-Podcast API",
    description="API para converter artigos científicos em podcasts",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"],
)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload um arquivo PDF para o servidor"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Apenas arquivos PDF são permitidos"
        )

    try:
        contents = await file.read()
        temp_path = PDF_DIR / file.filename

        with open(temp_path, "wb") as f:
            f.write(contents)

        saved_path = PDFProcessor.save_pdf(str(temp_path))
        Path(temp_path).unlink(missing_ok=True)  # Remove arquivo temporário

        return {
            "filename": saved_path.name,
            "path": str(saved_path),
            "message": f"PDF '{file.filename}' enviado com sucesso",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar arquivo: {str(e)}"
        )


@app.get("/pdfs")
def list_pdfs():
    """Lista todos os PDFs disponíveis no servidor"""
    try:
        pdfs = PDFProcessor.get_all_pdfs()
        if not pdfs:
            return {"message": "Nenhum PDF encontrado."}
        return {
            "pdfs": [
                {
                    "filename": pdf.name,
                    "path": str(pdf),
                    "metadata": PDFProcessor.get_pdf_metadata(pdf),
                }
                for pdf in pdfs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar PDFs: {str(e)}")


@app.post("/summarize/{pdf_name}")
async def summarize_pdf(
    pdf_name: str, method: str = Form("stuff"), remove_references: bool = Form(True)
):
    """
    Sumariza um PDF específico

    - method: 'stuff' ou 'map_reduce'
    - remove_references: se True, remove a seção de referências antes da sumarização
    """
    try:
        # Procurar PDF pelo nome
        pdf_files = PDFProcessor.get_all_pdfs()
        pdf_path = None

        for pdf in pdf_files:
            if pdf.name == pdf_name:
                pdf_path = pdf
                break

        if not pdf_path:
            raise HTTPException(
                status_code=404, detail=f"PDF '{pdf_name}' não encontrado"
            )

        # Extrair texto do PDF
        chunks = PDFProcessor.extract_text(pdf_path)

        # Remover referências se solicitado
        if remove_references:
            chunks, refs_removed = PDFProcessor.remove_references(chunks)

        # Escolher método de sumarização
        if method == "stuff":
            result = summarizer.stuff(pdf_path, chunks=chunks)
        else:
            result = summarizer.map_reduce(pdf_path, chunks=chunks)

        # Adicionar informação sobre remoção de referências aos metadados
        if remove_references:
            result["metadata"]["references_removed"] = refs_removed

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro durante sumarização: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
