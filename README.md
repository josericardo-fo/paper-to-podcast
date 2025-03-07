# Paper to Podcast

## Descrição

Paper to Podcast é uma aplicação que converte artigos acadêmicos (PDFs) em formato de áudio, permitindo que você consuma conteúdo científico em formato de podcast. A aplicação extrai texto de arquivos PDF, gera um resumo utilizando técnicas de IA através do LangChain e converte o resumo em áudio.

## Funcionalidades

- Carregamento e processamento de arquivos PDF
- Extração inteligente de texto de artigos acadêmicos
- Sumarização automática usando LangChain
- Conversão de texto para áudio (TTS)
- Interface gráfica amigável construída com CustomTkinter

## Instalação

- Utilizando Docker (recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/paper-to-podcast.git
cd paper-to-podcast

# Construa a imagem Docker
docker build -t paper-to-podcast .

# Execute a aplicação
docker-compose up
```

## Instalação Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/paper-to-podcast.git
cd paper-to-podcast

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app/main.py
```

## Configuração

Para utilizar todas as funcionalidades do Paper to Podcast, você precisa configurar:

1. Chaves de API para os serviços de IA (definidas em variáveis de ambiente)
2. Preferências de idioma e voz para geração de áudio. As configurações podem ser ajustadas no arquivo `config.py`.
