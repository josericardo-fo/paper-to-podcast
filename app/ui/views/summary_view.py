import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, ttk

from core.pdf_processor import PDFProcessor
from core.summarizer import Summarizer


class SummaryView(ttk.Frame):
    """
    View para exibição e geração de resumos.
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.summarizer = Summarizer()
        self.current_pdf = None
        self.current_summary = None

        self._create_widgets()

    def _create_widgets(self):
        # Frame superior para informações do PDF
        info_frame = ttk.LabelFrame(self, text="Informações do PDF")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.pdf_info_var = tk.StringVar(value="Nenhum PDF selecionado")
        pdf_info_label = ttk.Label(info_frame, textvariable=self.pdf_info_var)
        pdf_info_label.pack(fill=tk.X, padx=10, pady=5)

        # Frame de ações
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        self.summarize_button = ttk.Button(
            action_frame,
            text="Gerar Resumo",
            command=self._generate_summary,
            state=tk.DISABLED,
        )
        self.summarize_button.pack(side=tk.LEFT, padx=5)

        self.podcast_button = ttk.Button(
            action_frame,
            text="Gerar Podcast do Resumo",
            command=self._generate_podcast,
            state=tk.DISABLED,
        )
        self.podcast_button.pack(side=tk.LEFT, padx=5)

        # Área de texto para o resumo
        summary_frame = ttk.LabelFrame(self, text="Resumo")
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            bg="#2a2a2a",
            fg="white",
            font=("Arial", 11),
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.summary_text.config(state=tk.DISABLED)

    def process_pdf(self, pdf_path: Path):
        """
        Configura a view para processar um PDF específico.
        """
        self.current_pdf = pdf_path

        # Atualizar informações do PDF
        metadata = PDFProcessor.get_pdf_metadata(pdf_path)
        info_text = f"Arquivo: {metadata['filename']}\nTamanho: {metadata['size_kb']} KB\nData: {metadata['created_date']}"
        self.pdf_info_var.set(info_text)

        # Habilitar botão de resumo
        self.summarize_button.config(state=tk.NORMAL)

        # Limpar área de texto
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(
            tk.END, "Clique em 'Gerar Resumo' para processar o PDF."
        )
        self.summary_text.config(state=tk.DISABLED)

        # Desabilitar botão de podcast
        self.podcast_button.config(state=tk.DISABLED)

    def _generate_summary(self):
        """Gera resumo do PDF atual."""
        if not self.current_pdf:
            return

        self.app.set_status(
            "Gerando resumo... Isso pode demorar um pouco.", show_progress=True
        )
        self.summarize_button.config(state=tk.DISABLED)

        # Limpar e preparar área de texto
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "Processando PDF e gerando resumo...")
        self.summary_text.config(state=tk.DISABLED)

        def summarize_task():
            try:
                # Extrair texto do PDF
                chunks = PDFProcessor.extract_text(self.current_pdf)

                # Gerar resumo
                summary_result = self.summarizer.create_summary(
                    self.current_pdf, chunks
                )
                self.current_summary = summary_result

                # Atualizar UI no thread principal
                self.after(0, lambda: self._update_summary_ui(summary_result))
            except Exception as e:
                error_msg = f"Erro ao gerar resumo: {str(e)}"
                self.after(0, lambda: self._handle_summary_error(error_msg))

        # Executar em thread separada
        threading.Thread(target=summarize_task, daemon=True).start()

    def _update_summary_ui(self, summary_result):
        """Atualiza a interface com o resumo gerado."""
        if "error" in summary_result:
            self._handle_summary_error(summary_result["error"])
            return

        # Exibir resumo
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_result["summary"])
        self.summary_text.config(state=tk.DISABLED)

        # Atualizar status
        self.app.set_status("Resumo gerado com sucesso!")

        # Habilitar botões
        self.summarize_button.config(state=tk.NORMAL)
        self.podcast_button.config(state=tk.NORMAL)

    def _handle_summary_error(self, error_msg):
        """Manipula erros na geração do resumo."""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, f"Erro: {error_msg}")
        self.summary_text.config(state=tk.DISABLED)

        self.app.set_status(f"Erro: {error_msg}")
        self.summarize_button.config(state=tk.NORMAL)

    def _generate_podcast(self):
        """Envia o resumo para a geração de podcast."""
        if not self.current_summary:
            self.app.set_status("Nenhum resumo disponível para gerar podcast")
            return

        # Mudar para a aba de podcast
        self.app.notebook.select(2)  # Índice da aba de podcast

        # Iniciar geração do podcast com o resumo atual
        summary_text = self.summary_text.get(1.0, tk.END)
        self.app.podcast_view.prepare_podcast(summary_text, self.current_pdf.name)
