from EquatorialScraper import EquatorialScraper
import time

if __name__ == "__main__":
    scraper = EquatorialScraper()

    unidade_consumidora = "10031716405"
    cnpj = "27.265.098/0001-65"

    scraper.login(unidade_consumidora, cnpj)
    scraper.close_modal("#popup_promocao")
    scraper.access_second_invoice()
    scraper.select_option("CONTENT_cbTipoEmissao", "completa")
    scraper.select_option("CONTENT_cbMotivo", "ESV05")
    scraper.click_button("CONTENT_btEnviar")
    scraper.download_invoice()
    scraper.handle_protocol_modal()

    time.sleep(25)
    #scraper.quit()