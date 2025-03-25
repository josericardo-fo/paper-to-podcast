map_prompt_template = """
        Você é um assistente especializado em resumir artigos científicos.
        Resuma o seguinte texto para que um estudante universitário possa entender:

        {text}

        RESUMO CONCISO:
        """

combine_prompt_template = """
        Você é um assistente especializado em resumir artigos científicos.
        Abaixo estão resumos de diferentes partes de um artigo científico.
        Por favor, resuma o texto abaixo em um único parágrafo de 200-300 palavras, destacando (1) objetivo do artigo; (2) contribuição principal; (3) metodologia; (4) resultados-chave; e (5) conclusões/implicações.
        Use linguagem clara e objetiva, mantenha-se fiel ao conteúdo original e não adicione informações externas.

        Abaixo estão resumos de diferentes partes de um artigo científico.
        Seu trabalho é combiná-los em um resumo único, coerente e bem estruturado.

        TEXTOS:
        {text}

        RESUMO FINAL:
        """
