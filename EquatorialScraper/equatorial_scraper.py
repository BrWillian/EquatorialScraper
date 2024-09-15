import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from pyvirtualdisplay import Display
import threading


class WebDriverFactory:
    """Factory for creating a Selenium WebDriver instance."""

    @staticmethod
    def create_driver(download_folder: str) -> webdriver.Firefox:
        """Creates and returns a Firefox WebDriver instance with custom options."""
        display = Display(visible=False, size=(1024, 768))
        display.start()

        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-gpu')
        firefox_options.add_argument('--disable-dev-shm-usage')
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", download_folder)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        firefox_options.set_preference("pdfjs.disabled", True)

        driver_path = "/opt/geckodriver/geckodriver"
        service = FirefoxService(executable_path=driver_path)
        return webdriver.Firefox(service=service, options=firefox_options)

class EquatorialScraper:
    """Class to handle scraping of the Equatorial energy website."""
    def __init__(self):
        self.url_base = "https://goias.equatorialenergia.com.br/LoginGO.aspx"
        self.download_thread = None
        self.downloaded_files = []
        self.protocol_number = []
        self.download_folder = "/app/files"
        self.driver = None
        self.download_exception = None
        self.status = 1
        self.error_message = None
        self.setup_driver()


    def __dict__(self):
        """Return attributes the class with a dictionary."""
        return {
            'status': self.status,
            'downloaded_files': self.downloaded_files,
            'error_message': self.error_message
        }

    def setup_driver(self):
        """Initializes the web driver."""
        self.driver = WebDriverFactory.create_driver(self.download_folder)

    def wait_for_page_load(self, timeout=10):
        """Waits for the page to fully load."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            raise WebDriverException(f"Page did not load within {timeout} seconds.")

    def wait_for_element(self, by, value, timeout=10):
        """Waits for a specific element to appear on the page."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            wait.until(EC.visibility_of(element))
            return element
        except TimeoutException:
            raise WebDriverException(f"Element with {by}='{value}' not found within {timeout} seconds.")

    def login(self, unidade_consumidora, cnpj):
        """Handles the login process."""
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
        """Closes modal windows."""
        try:
            time.sleep(2)
            modal = self.wait_for_element(By.CSS_SELECTOR, modal_selector)
            close_button = modal.find_element(By.CSS_SELECTOR, ".close")
            close_button.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar fechar o modal {modal_selector}: {e.msg}")

    def access_menu_invoices(self, select_id):
        """Accesses the menu for invoices."""
        try:
            time.sleep(2)
            contas_menu = self.wait_for_element(By.XPATH, "//label[normalize-space(text())='Contas']")
            contas_menu.click()

            time.sleep(2)
            segunda_via_link = self.wait_for_element(By.ID, select_id)
            segunda_via_link.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar acessar o menu: {e.msg}")


    def select_option(self, select_id, value, option_type='value'):
        """Selects an option from a dropdown menu."""
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
        """Click and navigate in buttons."""
        try:
            time.sleep(2)
            button = self.wait_for_element(By.ID, button_id)
            button.click()
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar clicar no botão '{button_id}': {e.msg}")

    def download_invoice(self):
        """Downloads the current invoice."""
        try:
            time.sleep(2)
            download_link = self.wait_for_element(By.XPATH, "//a[contains(text(), 'Download')]")
            download_link.click()

            self.download_thread = threading.Thread(target=self.wait_for_download)
            self.download_thread.start()

        except WebDriverException as e:
            print(f"Erro ao tentar fazer o download da fatura: {e.msg}")

    def handle_protocol_modal(self, select_id, protocol_id):
        """Handles the modal that shows protocol information."""
        try:
            time.sleep(2)
            protocol_modal = self.wait_for_element(By.ID, select_id)
            protocol_text = protocol_modal.find_element(By.ID, protocol_id).text
            ok_button = protocol_modal.find_element(By.CLASS_NAME, "btn")
            ok_button.click()

            self.protocol_number.append(protocol_text.split(': ')[-1].replace(".", ""))
        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar lidar com o modal de protocolo: {e.msg}")

    def wait_for_download(self, timeout=30):
        """Waits for the file download to complete."""
        download_folder = self.download_folder
        start_time = time.time()
        downloaded_file_name = None

        try:
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
                            self.downloaded_files.append(pdf_files[0])
                            break

                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    raise TimeoutException("O download não foi concluído dentro do tempo limite.")
        except TimeoutException as e:
            self.download_exception = e

    def switch_to_new_window(self):
        """switch the new windows."""
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[-1])

    def close_new_window(self):
        """Close the new windows."""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def rename_downloaded_file(self, suffix):
        """Renames the downloaded file to include a custom suffix."""
        try:
            if self.downloaded_files[-1]:
                old_path = os.path.join(self.download_folder, self.downloaded_files[-1])
                new_file_name = f"{self.downloaded_files[0].split('.')[0]}_{suffix}.pdf"
                new_path = os.path.join(self.download_folder, new_file_name)
                os.rename(old_path, new_path)
                self.downloaded_files[-1] = new_file_name
        except Exception as e:
            print(f"Erro ao renomear o arquivo: {e}")

    def download_invoice_history(self):
        """Downloads the history invoices."""
        time.sleep(2)
        try:

            history_table = self.wait_for_element(By.ID, "CONTENT_gridHistoricoFatura")
            rows = history_table.find_elements(By.CSS_SELECTOR, "tr.GridRow")

            for index, row in enumerate(rows):
                mes_ano = row.find_element(By.ID, f"CONTENT_gridHistoricoFatura_gridLblMesReferencia_{index}").text
                download_link = row.find_element(By.XPATH,
                                                 f"//a[contains(@onclick, 'mostrarEspelhoFatura.aspx?invoice={index}')]")
                download_link.click()

                time.sleep(5)

                self.switch_to_new_window()
                self.download_thread = threading.Thread(target=self.wait_for_download)
                self.download_thread.start()
                self.handle_protocol_modal("mostrarEspelhoFaturaModalProtocolo", "CONTENT_lblModalBody_protocolo")
                self.wait_for_finish_download()

                self.rename_downloaded_file(mes_ano.replace("/", "_"))
                self.close_new_window()

        except WebDriverException as e:
            raise WebDriverException(f"Erro ao tentar baixar o histórico de faturas: {e.msg}")

    def wait_for_finish_download(self):
        """Waits for the download thread to finish."""
        try:
            if self.download_thread:
                self.download_thread.join()
                if self.download_exception:
                    raise self.download_exception
        except TimeoutException:
            raise

    def quit(self):
        """Closes the WebDriver and the display."""
        if self.driver:
            self.driver.quit()

    def process(self,unidade_consumidora, cnpj):
        """Main process to scrape invoices."""
        try:
            # Limpando listas
            self.downloaded_files = []
            self.protocol_number = []

            # Processando o scraper
            self.login(unidade_consumidora, cnpj)
            self.close_modal("#popup_promocao")
            self.access_menu_invoices("LinkSegundaVia")
            self.select_option("CONTENT_cbTipoEmissao", "completa")
            self.select_option("CONTENT_cbMotivo", "ESV05")
            self.click_button("CONTENT_btEnviar")
            self.download_invoice()
            self.handle_protocol_modal("FaturaCompletaModalProtocolo", "CONTENT_lblModalBody_protocolo")
            self.wait_for_finish_download()
            self.access_menu_invoices("LinkhistoricoFaturas")
            self.click_button("CONTENT_btEnviar")
            self.handle_protocol_modal("historicoFaturaModal", "CONTENT_lblModalBody")
            self.download_invoice_history()

        except Exception as e:
            self.error_message = str(e)
            self.status = 2