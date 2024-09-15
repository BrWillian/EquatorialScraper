# :scroll: EquatorialScraper

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.1.0-green?logo=selenium)

O `TransfereGovScraper` é uma ferramenta em Python para automatizar o scraping e download de arquivos de um site específico usando Selenium. Este script é útil para extrair arquivos de uma página da web que contém links de download gerados dinamicamente.

## Pré-requisitos

Certifique-se de ter os seguintes requisitos instalados:

- Docker
- Docker Compose

## :clipboard: Como Usar

1. **Clone do repositório**
    - Faça o download do repositorio
       ```bash
       git clone https://github.com/brwillian/EquatorialScraper.git
       ```

2. **Configuração do Ambiente**
   - Certifique-se de ter o Chrome WebDriver instalado e configurado.
   - Instale as dependências necessárias:
     ```bash
     docker-compose up --build --recreate-force
     ```

3. **Executar o Script**
   - Navegue o kafka-ui:
   - E produza as mensagens no formato:
       ```json
       {"id": 1,"unidade_consumidora": "00000000000","doc": "00.000.000/0001-00"}
       ```
   - O resultado gerado será no topico configurado no seguinte formato para erro:
       ```json
       {"id": 1, "status": 2,"downloaded_files": [], "error_message": "Message error!"}
       ```
   - Ou para sucesso:
       ```json
       {"id": 1, "status": 1,"downloaded_files": ["file.pdf", "file_1_2024.pdf"], "error_message": null}
       ```
   
## :rocket: Observações

- Certifique-se de ajustar o caminho do volume presente no docker-compose.yaml ```$HOME/equatorial-scraper/:/app/files```
- O script foi projetado para trabalhar com links específicos gerados dinamicamente por um site específico. Adapte conforme necessário para outras finalidades.
---