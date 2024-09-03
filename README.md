# EquatorialScraper

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.1.0-green?logo=selenium)

O `TransfereGovScraper` é uma ferramenta em Python para automatizar o scraping e download de arquivos de um site específico usando Selenium. Este script é útil para extrair arquivos de uma página da web que contém links de download gerados dinamicamente.

## Pré-requisitos

Certifique-se de ter os seguintes requisitos instalados:

- Python 3.x ![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
- Chrome WebDriver
- Xvfb (instalável via apt)

```bash
sudo apt install xvfb
```

Certifique-se de ter o Chrome WebDriver baixado e configurado. Você pode ajustar o caminho para o driver no código conforme necessário.

## Como Usar

1. **Clone do repositório**
    - Faça o download do repositorio
       ```bash
       git clone https://github.com/brwillian/EquatorialScraper.git
       ```

2. **Configuração do Ambiente**
   - Certifique-se de ter o Chrome WebDriver instalado e configurado.
   - Instale as dependências necessárias:
     ```bash
     pip install -r requirements.txt
     ```

3. **Executar o Script**
   - Navegue até o diretório clonado:
     ```bash
     cd EquatorialScraper
     ```
   - Execute o script Python:
     ```bash
     python main.py
     ```
   - Siga as instruções na linha de comando para inserir o número do convênio desejado.

4. **Resultados**
   - O script irá iniciar o WebDriver do Chrome automaticamente.
   - Ele irá acessar a página correspondente ao convênio fornecido e extrair os links de download.
   - Os arquivos serão baixados automaticamente para a pasta `files` dentro do diretório do script.
   - Os arquivos serão renomeados e organizados por convênio em subpastas dentro da pasta `files`.

## Estrutura do Projeto

- `main.py`: O script principal que contém invoca `EquatorialScraper` para realizar o scraping e download.
- `files/`: Pasta padrão onde os arquivos baixados serão armazenados.
- `README.md`: Este arquivo, fornecendo informações sobre o projeto e como usá-lo.

## Observações

- Certifique-se de ajustar o caminho do Chrome WebDriver (`chrome_driver_path`) conforme necessário no código.
- O script foi projetado para trabalhar com links específicos gerados dinamicamente por um site específico. Adapte conforme necessário para outras finalidades.

---