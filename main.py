import sys
import requests
from selenium import webdriver

def main(headless=True):
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://informacoes.anatel.gov.br/paineis/acessos")
    
    __cf_bm = driver.get_cookie("__cf_bm")["value"]
    _cfuvid = driver.get_cookie("_cfuvid")["value"]

    print(__cf_bm, _cfuvid)
    
    r = requests.head(
        "https://www.anatel.gov.br/dadosabertos/paineis_de_dados/acessos/acessos_banda_larga_fixa.zip",
        cookies={"__cf_bm": __cf_bm, "_cfuvid": _cfuvid},
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        },
    )
    
    print(r.status_code)
    print(r.headers)
    print(r)

if __name__ == "__main__":
    _, *args = sys.argv
    headless = "--headless" in args
    main(headless)
