import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from core.pdf_processor import PDFProcessor


class UploadView(ttk.Frame):
    """
    View para upload e seleção de PDFs.
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._create_widgets()
        self._update_pdf_list()

    def _create_widgets(self):
        # Frame principal com duas colunas
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Coluna da esquerda - Upload
        left_frame = ttk.LabelFrame(main_frame, text="Upload PDF")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        upload_button = ttk.Button(
            left_frame, text="Selecionar PDF", command=self._upload_pdf
        )
        upload_button.pack(pady=20, padx=10, fill=tk.X)

        info_label = ttk.Label(
            left_frame, text="Selecione um arquivo PDF para processar."
        )
        info_label.pack(fill=tk.X, padx=10, pady=5)

        # Coluna da direita - PDFs carregados
        right_frame = ttk.LabelFrame(main_frame, text="PDFs Disponíveis")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Lista de PDFs
        pdf_frame = ttk.Frame(right_frame)
        pdf_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(pdf_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Lista de PDFs
        self.pdf_listbox = tk.Listbox(
            pdf_frame,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            bg="#333333",
            fg="white",
            selectbackground="#a6a6a6",
            selectforeground="black",
        )
        self.pdf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pdf_listbox.yview)

        # Botões de ação
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=5)

        process_button = ttk.Button(
            button_frame,
            text="Processar PDF Selecionado",
            command=self._process_selected_pdf,
        )
        process_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        refresh_button = ttk.Button(
            button_frame, text="Atualizar Lista", command=self._update_pdf_list
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

    def _upload_pdf(self):
        """Abre diálogo para selecionar e fazer upload do PDF."""
        filepath = filedialog.askopenfilename(
            title="Selecione um PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )

        if not filepath:
            return

        self.app.set_status("Fazendo upload do PDF...", show_progress=True)

        def upload_task():
            try:
                saved_path = PDFProcessor.save_pdf(filepath)

                # Atualizar UI no thread principal
                self.after(0, lambda: self._update_pdf_list(select_new=saved_path.name))
                self.after(
                    0,
                    lambda: self.app.set_status(
                        f"PDF '{saved_path.name}' carregado com sucesso"
                    ),
                )
            except Exception:
                self.after(0, lambda: self.app.set_status("Erro ao carregar PDF"))

        # Executar em thread separada para não bloquear a UI
        threading.Thread(target=upload_task, daemon=True).start()

    def _update_pdf_list(self, select_new=None):
        """Atualiza a lista de PDFs disponíveis."""
        pdfs = PDFProcessor.get_all_pdfs()

        # Limpar lista atual
        self.pdf_listbox.delete(0, tk.END)

        # Adicionar PDFs à lista
        for pdf_path in pdfs:
            self.pdf_listbox.insert(tk.END, pdf_path.name)

        # Selecionar novo PDF se especificado
        if select_new:
            for i, item in enumerate(self.pdf_listbox.get(0, tk.END)):
                if item == select_new:
                    self.pdf_listbox.selection_set(i)
                    self.pdf_listbox.see(i)
                    break

    def _process_selected_pdf(self):
        """Processa o PDF selecionado."""
        selection = self.pdf_listbox.curselection()
        if not selection:
            self.app.set_status("Nenhum PDF selecionado")
            return

        pdf_name = self.pdf_listbox.get(selection[0])
        pdf_path = Path(PDFProcessor.get_all_pdfs()[0].parent, pdf_name)

        # Mudar para a aba de resumo e iniciar processamento
        self.app.notebook.select(1)  # Índice da aba de resumo
        self.app.summary_view.process_pdf(pdf_path)
