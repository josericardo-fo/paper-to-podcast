# 🎧 Paper to Podcast

## 📝 Descrição

Paper to Podcast é uma aplicação que transforma artigos acadêmicos (PDFs) em conteúdo de áudio, permitindo que pesquisadores e estudantes consumam conteúdo científico em formato de podcast. A aplicação utiliza processamento de linguagem natural para extrair e resumir o conteúdo dos artigos, e tecnologia text-to-speech para gerar áudios de alta qualidade.

## ✨ Funcionalidades

- 🔍 Extração inteligente de texto com suporte a formatação acadêmica
- 🤖 Sumarização automática usando LLMs via LangChain
- 🔊 Conversão de texto para áudio com ajustes de velocidade e tom
- 📱 API RESTful para integração com outros sistemas

## 🚀 Começando

### Pré-requisitos

- Docker (para instalação com containers)
- Chave de API da OpenAI

### Instalação com Docker

```bash
# Clone o repositório
git clone https://github.com/josericardo-fo/paper-to-podcast.git
cd paper-to-podcast

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com sua chave da OpenAI

# Execute com Docker Compose
docker-compose build
docker-compose up
```

## 🔧 Configuração

Para utilizar todas as funcionalidades do Paper to Podcast, configure:

1. **Variáveis de ambiente**:
   - `OPENAI_API_KEY`: Sua chave API da OpenAI
   - `OPENAI_MODEL`: Modelo a ser usado (padrão: "gpt-4o-mini")

2. **Diretórios de Trabalho**:
   - `/pdfs`: Armazena os PDFs enviados
   - `/output/summaries`: Armazena os resumos gerados
   - `/output/podcasts`: Armazena os arquivos de áudio

## 🖥️ Uso da API

### Endpoints Principais

- `POST /upload` - Faz upload de um arquivo PDF
- `GET /pdfs` - Lista todos os PDFs disponíveis
- `POST /summarize/{pdf_name}` - Gera um resumo de um PDF específico
  - Parâmetros: `method` (stuff/map_reduce), `remove_references` (true/false)

### Exemplo de Utilização

```python
import requests

# Upload de um PDF
with open('artigo.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    pdf_name = response.json()['filename']

# Geração de resumo
response = requests.post(
    f'http://localhost:8000/summarize/{pdf_name}',
    data={'method': 'map_reduce', 'remove_references': 'true'}
)
print(response.json()['summary'])
```

## 🛠️ Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web para criação de APIs
- [LangChain](https://langchain.ai/) - Framework para aplicações com LLMs
- [PyPDF2](https://github.com/py-pdf/PyPDF2) - Biblioteca para processamento de PDFs
- [OpenAI API](https://openai.com/api/) - Modelos de linguagem para resumos

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.
