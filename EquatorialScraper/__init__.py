import os
import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from pyvirtualdisplay import Display
import threading


class EquatorialScraper:
    def __init__(self):
        self.download_thread = None
        self.downloaded_file_name = None
        self.protocol_number = None
        self.display = None
        self.download_folder = "/app/files"
        self.url_base = "https://goias.equatorialenergia.com.br/LoginGO.aspx"
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()

        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-gpu')
        firefox_options.add_argument('--disable-dev-shm-usage')
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", self.download_folder)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        firefox_options.set_preference("pdfjs.disabled", True)

        driver_path = "/opt/geckodriver/geckodriver"
        service = FirefoxService(executable_path=driver_path)
        self.driver = webdriver.Firefox(service=service, options=firefox_options)

    def wait_for_page_load(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            raise WebDriverException(f"Page did not load within {timeout} seconds.")

    def wait_for_element(self, by, value, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            wait.until(EC.visibility_of(element))
            return element
        except TimeoutException:
            raise WebDriverException(f"Element with {by}='{value}' not found within {timeout} seconds.")

    def login(self, unidade_consumidora, cnpj):
        try:
            self.driver.get(self.url_base)
            self.wait_for_page_load(timeout=15)
            time.sleep(2)

            unidade_input = self.wait_for_element(By.ID, "WEBDOOR_headercorporativogo_txtUC")
            cnpj_input = self.wait_for_element(By.ID, "WEBDOOR_headercorporativogo_txtDocumento")

            unidade_input.send_keys(unidade_consumidora)
            cnpj_input.send_keys(cnpj)

            time.sleep(2)
            login_button = self.wait_for_element(By.XPATH, "//button[@onclick='ValidarCamposAreaLogada()']")
            login_button.click()
        except WebDriverException as e:
            raise WebDriverException(f"Falha ao realizar login: {e.msg}")

    def close_modal(self, modal_selector):
        try:
            time.sleep(2)
            modal = self.wait_for_element(By.CSS_SELECTOR, modal_selector)
            close_button = modal.find_element(By.CSS_SELECTOR, ".close")
            close_button.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar fechar o modal {modal_selector}: {e.msg}")

    def access_second_invoice(self):
        try:
            time.sleep(2)
            contas_menu = self.wait_for_element(By.XPATH, "//label[normalize-space(text())='Contas']")
            contas_menu.click()

            time.sleep(2)
            segunda_via_link = self.wait_for_element(By.ID, "LinkSegundaVia")
            segunda_via_link.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar acessar a Segunda Via de Fatura: {e.msg}")

    def select_option(self, select_id, value, option_type='value'):
        try:
            time.sleep(2)
            select_element = self.wait_for_element(By.ID, select_id)
            select = Select(select_element)
            if option_type == 'value':
                select.select_by_value(value)
            elif option_type == 'text':
                select.select_by_visible_text(value)
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar selecionar a opção '{value}' em {select_id}: {e.msg}")

    def click_button(self, button_id):
        try:
            time.sleep(2)
            button = self.wait_for_element(By.ID, button_id)
            button.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar clicar no botão '{button_id}': {e.msg}")

    def download_invoice(self):
        try:
            time.sleep(2)
            download_link = self.wait_for_element(By.XPATH, "//a[contains(text(), 'Download')]")
            download_link.click()

            self.download_thread = threading.Thread(target=self.wait_for_download)
            self.download_thread.start()

        except WebDriverException as e:
            print(f"Erro ao tentar fazer o download da fatura: {e}")

    def handle_protocol_modal(self):
        try:
            time.sleep(2)
            protocol_modal = self.wait_for_element(By.ID, "FaturaCompletaModalProtocolo")
            protocol_text = protocol_modal.find_element(By.ID, "CONTENT_lblModalBody_protocolo").text
            ok_button = protocol_modal.find_element(By.ID, "CONTENT_btnModal")
            ok_button.click()

            self.protocol_number = protocol_text.split(': ')[-1].replace(".", "")
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar lidar com o modal de protocolo: {e.msg}")

    def wait_for_download(self, timeout=30):
        download_folder = self.download_folder
        start_time = time.time()
        downloaded_file_name = None

        while True:
            files = os.listdir(download_folder)

            part_files = [file for file in files if file.endswith(".part")]

            if part_files:
                part_file = part_files[0]
                downloaded_file_name = part_file.split(".")[0]
            else:
                if downloaded_file_name:
                    pdf_files = [file for file in files if
                                 file.endswith(".pdf") and file.startswith(downloaded_file_name)]
                    if pdf_files:
                        self.downloaded_file_name = pdf_files[0]
                        break

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise TimeoutException("O download não foi concluído dentro do tempo limite.")


    def wait_for_finish_download(self):
        if self.download_thread: self.download_thread.join()

    def quit(self):
        if self.driver:
            self.driver.quit()

    def process(self, unidade_consumidora, cnpj):
        try:
            self.login(unidade_consumidora, cnpj)
            self.close_modal("#popup_promocao")
            self.access_second_invoice()
            self.select_option("CONTENT_cbTipoEmissao", "completa")
            self.select_option("CONTENT_cbMotivo", "ESV05")
            self.click_button("CONTENT_btEnviar")
            self.download_invoice()
            self.handle_protocol_modal()
            self.wait_for_finish_download()

            return json.dumps({"status": 1, "protocol": self.protocol_number, "pathEnergia": self.downloaded_file_name, "traceback": None})

        except WebDriverException as e:
            return json.dumps({"status": 2, "protocol": None, "pathEnergia": None, "traceback": str(e.msg)})