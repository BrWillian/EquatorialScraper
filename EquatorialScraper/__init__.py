import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display


class EquatorialScraper:
    def __init__(self):
        self.display = None
        self.download_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
        self.url_base = "https://goias.equatorialenergia.com.br/LoginGO.aspx"
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        #self.display = Display(visible=0, size=(1024, 768))
        #self.display.start()

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.download_folder,
            'directory_upgrade': True,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })

        driver_path = "/opt/chromedriver/chromedriver"
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def wait_for_element(self, by, value, timeout=10):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = self.driver.find_element(by, value)
                if element.is_displayed():
                    return element
            except WebDriverException:
                pass
            time.sleep(1)
        raise WebDriverException(f"Element with {by}='{value}' not found within {timeout} seconds.")

    def login(self, unidade_consumidora, cnpj):
        self.driver.get(self.url_base)
        time.sleep(5)

        unidade_input = self.wait_for_element(By.ID, "WEBDOOR_headercorporativogo_txtUC")
        cnpj_input = self.wait_for_element(By.ID, "WEBDOOR_headercorporativogo_txtDocumento")

        unidade_input.send_keys(unidade_consumidora)
        cnpj_input.send_keys(cnpj)

        login_button = self.wait_for_element(By.XPATH, "//button[@onclick='ValidarCamposAreaLogada()']")
        login_button.click()

    def close_modal(self, modal_selector):
        try:
            modal = self.wait_for_element(By.CSS_SELECTOR, modal_selector)
            close_button = modal.find_element(By.CSS_SELECTOR, ".close")
            close_button.click()
            print(f"Modal {modal_selector} fechado com sucesso.")
        except WebDriverException as e:
            print(f"Erro ao tentar fechar o modal {modal_selector}: {e}")

    def access_second_invoice(self):
        try:
            contas_menu = self.wait_for_element(By.XPATH, "//label[normalize-space(text())='Contas']")
            contas_menu.click()
            time.sleep(1)  # Espera o menu expandir

            segunda_via_link = self.wait_for_element(By.ID, "LinkSegundaVia")
            segunda_via_link.click()
            print("Acessou a página de Segunda Via de Fatura com sucesso.")
        except WebDriverException as e:
            print(f"Erro ao tentar acessar a Segunda Via de Fatura: {e}")

    def select_option(self, select_id, value, option_type='value'):
        try:
            select_element = self.wait_for_element(By.ID, select_id)
            select = Select(select_element)
            if option_type == 'value':
                select.select_by_value(value)
            elif option_type == 'text':
                select.select_by_visible_text(value)
            print(f"Opção '{value}' selecionada com sucesso em {select_id}.")
        except WebDriverException as e:
            print(f"Erro ao tentar selecionar a opção '{value}' em {select_id}: {e}")

    def click_button(self, button_id):
        try:
            button = self.wait_for_element(By.ID, button_id)
            button.click()
            print(f"Botão '{button_id}' clicado com sucesso.")
        except WebDriverException as e:
            print(f"Erro ao tentar clicar no botão '{button_id}': {e}")

    def download_invoice(self):
        try:
            download_link = self.wait_for_element(By.XPATH, "//a[contains(text(), 'Download')]")
            download_link.click()
            print("Clique no link de download realizado com sucesso.")
        except WebDriverException as e:
            print(f"Erro ao tentar fazer o download da fatura: {e}")

    def handle_protocol_modal(self):
        try:
            protocol_modal = self.wait_for_element(By.ID, "FaturaCompletaModalProtocolo")
            protocol_text = protocol_modal.find_element(By.ID, "CONTENT_lblModalBody_protocolo").text
            print(f"Número do protocolo: {protocol_text.split(': ')[-1]}")

            ok_button = protocol_modal.find_element(By.ID, "CONTENT_btnModal")
            ok_button.click()
            print("Modal de protocolo fechado com sucesso.")
        except WebDriverException as e:
            print(f"Erro ao tentar lidar com o modal de protocolo: {e}")

    def quit(self):
        if self.driver:
            self.driver.quit()
