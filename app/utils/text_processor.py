import re
from typing import List


class TextProcessor:
    """
    Processador de texto para a aplicação Paper-to-Podcast.
    Fornece métodos para manipular e preparar texto para diversas finalidades.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpa e formata texto para processamento.

        Args:
            text: Texto para limpar

        Returns:
            Texto limpo e formatado
        """
        if not text:
            return ""

        # Remover espaços em branco extras
        clean = re.sub(r"\s+", " ", text).strip()

        # Remover quebras de página e marcadores comuns em PDFs
        clean = re.sub(r"\f", " ", clean)
        clean = re.sub(r"\[PAGE \d+\]", "", clean)

        # Normalizar quebras de linha
        clean = re.sub(r"\n{3,}", "\n\n", clean)

        return clean

    @staticmethod
    def split_into_chunks(
        text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """
        Divide o texto em pedaços menores com sobreposição.

        Args:
            text: Texto para dividir
            chunk_size: Tamanho desejado de cada pedaço
            overlap: Quantidade de sobreposição entre pedaços

        Returns:
            Lista de pedaços de texto
        """
        if not text or chunk_size <= 0:
            return []

        clean_text = TextProcessor.clean_text(text)

        # Se o texto for menor que o tamanho do chunk, retornar o texto completo
        if len(clean_text) <= chunk_size:
            return [clean_text]

        chunks = []
        start = 0

        while start < len(clean_text):
            # Determinar o fim do chunk atual
            end = start + chunk_size

            # Se não estivermos no final do texto, tentar encontrar um ponto final ou quebra de linha
            if end < len(clean_text):
                # Procurar por um ponto final ou quebra de linha próximo ao fim para criar quebras naturais
                potential_end = end

                # Procurar por um ponto final seguido de espaço ou quebra de linha
                period_match = re.search(r"\.(?=\s)", clean_text[end - 50 : end + 50])
                if period_match:
                    potential_end = end - 50 + period_match.end()

                # Ou procurar por quebra de linha
                newline_match = re.search(r"\n", clean_text[end - 30 : end + 30])
                if newline_match:
                    potential_end = end - 30 + newline_match.end()

                end = potential_end

            # Garantir que não ultrapassamos o tamanho do texto
            end = min(end, len(clean_text))

            # Adicionar o pedaço à lista
            chunks.append(clean_text[start:end])

            # Avançar o início para o próximo chunk, considerando a sobreposição
            start = end - overlap

        return chunks

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """
        Extrai palavras-chave de um texto usando uma abordagem simples.

        Args:
            text: Texto para extrair palavras-chave
            max_keywords: Número máximo de palavras-chave a retornar

        Returns:
            Lista de palavras-chave
        """
        if not text:
            return []

        # Palavras comuns em inglês e português para remover
        stopwords = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "if",
            "because",
            "as",
            "what",
            "when",
            "where",
            "how",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "these",
            "those",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "to",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "o",
            "a",
            "os",
            "as",
            "um",
            "uma",
            "uns",
            "umas",
            "de",
            "do",
            "da",
            "dos",
            "das",
            "no",
            "na",
            "nos",
            "nas",
            "ao",
            "aos",
            "à",
            "às",
            "pelo",
            "pela",
            "pelos",
            "pelas",
            "em",
            "por",
            "para",
            "com",
            "sem",
            "como",
            "que",
            "quando",
            "onde",
            "qual",
            "quais",
            "quem",
            "cujo",
            "cuja",
            "cujos",
            "cujas",
            "este",
            "esta",
            "estes",
            "estas",
            "esse",
            "essa",
            "esses",
            "essas",
            "aquele",
            "aquela",
            "aqueles",
            "aquelas",
            "ser",
            "estar",
            "ter",
            "haver",
            "fazer",
        }

        # Limpar e dividir o texto
        clean_text = TextProcessor.clean_text(text.lower())

        # Remover caracteres não alfanuméricos e dividir em palavras
        words = re.findall(r"\b[a-zA-Z]{3,}\b", clean_text)

        # Filtrar stopwords
        filtered_words = [w for w in words if w not in stopwords]

        # Contar frequência das palavras
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Ordenar por frequência e pegar as top palavras
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:max_keywords]]

    @staticmethod
    def format_for_tts(text: str) -> str:
        """
        Formata o texto para TTS (Text-to-Speech), melhorando a pronúncia.

        Args:
            text: Texto para formatar

        Returns:
            Texto formatado para TTS
        """
        if not text:
            return ""

        # Limpar o texto
        formatted = TextProcessor.clean_text(text)

        # Substituir abreviações comuns
        abbreviations = {
            r"\bDr\.": "Doutor",
            r"\bSr\.": "Senhor",
            r"\bSra\.": "Senhora",
            r"\bProf\.": "Professor",
            r"\bEng\.": "Engenheiro",
            r"\be\.g\.": "por exemplo",
            r"\bi\.e\.": "isto é",
            r"\betc\.": "etcetera",
            r"\bpg\.": "página",
            r"\bcap\.": "capítulo",
            r"\bfig\.": "figura",
            r"\bEq\.": "Equação",
        }

        for abbr, full in abbreviations.items():
            formatted = re.sub(abbr, full, formatted)

        # Converter números para palavras em casos simples
        formatted = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", r"\1", formatted)

        # Lidar com símbolos especiais
        symbol_map = {
            "%": " por cento",
            "$": " dólares",
            "€": " euros",
            "£": " libras",
            "+": " mais",
            "=": " igual a",
            ">": " maior que",
            "<": " menor que",
            "&": " e",
            "@": " arroba",
            "#": " hashtag",
            "°C": " graus Celsius",
            "°F": " graus Fahrenheit",
            "/": " barra ",
            "\\": " barra invertida ",
        }

        for symbol, word in symbol_map.items():
            formatted = formatted.replace(symbol, word)

        # Remover marcadores de lista e outros caracteres problemáticos
        formatted = re.sub(r"^\s*[\-\*]\s+", "", formatted, flags=re.MULTILINE)

        # Adicionar pausas entre parágrafos para melhor naturalidade
        formatted = re.sub(r"\n\s*\n", "\n\n", formatted)

        return formatted

    @staticmethod
    def sanitize_filename(text: str) -> str:
        """
        Converte um texto para um nome de arquivo seguro.

        Args:
            text: Texto para converter

        Returns:
            Nome de arquivo seguro
        """
        if not text:
            return "unnamed"

        # Remover caracteres inválidos para nomes de arquivo
        safe_name = re.sub(r'[\\/*?:"<>|]', "", text)

        # Substituir espaços e outros caracteres por underscores
        safe_name = re.sub(r"[\s\-]+", "_", safe_name)

        # Limitar tamanho e remover underscores do início/fim
        safe_name = safe_name[:50].strip("_")

        return safe_name or "unnamed"
