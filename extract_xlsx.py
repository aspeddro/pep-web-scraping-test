import sys
import os
import time
import requests
import zipfile
import io
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

TARGET = "http://painel.pep.planejamento.gov.br/QvAJAXZfc/opendoc.htm?document=painelpep.qvw&lang=en-US&host=Local&anonymous=true"

XPATHS = {
    # Cargos e Funções
    "card_home_funcoes": "/html/body/div[5]/div/div[88]",
    # Aba Tabelas
    "tabelas": "/html/body/div[5]/div/div[280]/div[3]/table/tbody/tr/td",
}

SELECTIONS = [
    "Mês Cargos",
    "Natureza Juridica",
    "Orgão Superior",
    "Orgão",
    "Tipo de Função Detalhada",
    "Função",
    "Nível Função",
    "Subnível Função",
    "Região",
    "UF",
    "Nome Cor Origem Etnica",
    "Faixa Etária",
    "Escolaridade do Servidor",
    "Sexo",
    # Métricas
    "DAS e correlatas",
    "CCE & FCE",
]

SELECTIONS_DIMENSIONS = [
    "Mês Cargos",
    "Natureza Juridica",
    "Orgão Superior",
    "Orgão",
    "Tipo de Função Detalhada",
    "Função",
    "Nível Função",
    "Subnível Função",
    "Região",
    "UF",
    "Nome Cor Origem Etnica",
    "Faixa Etária",
    "Escolaridade do Servidor",
    "Sexo",
]

SELECTIONS_METRICS = ["CCE & FCE", "DAS e correlatas"]

CWD = os.path.dirname(os.path.realpath(__file__))

TMP_DIR = os.path.join(CWD, "tmp")
DOWNLOAD_DIR = os.path.join(CWD, "downloads")

CHROME_DRIVER = (
    "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
)


def setup_web_driver() -> None:
    r = requests.get(CHROME_DRIVER, stream=True)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(TMP_DIR)

    os.environ["PATH"] += os.pathsep + TMP_DIR

    path = os.environ["PATH"]

    files = os.listdir(TMP_DIR)

    print(files)

    print(f"Setup Web Driver done: {path}")


def wait_file_download(year, timeout=60 * 6):
    start_time = time.time()
    end_time = start_time + timeout

    file_exists = False

    while not file_exists:
        time.sleep(1.0)
        if len(os.listdir(TMP_DIR)) > 0:
            print(f"Time to download {year}, {time.time() - start_time} seconds")
            break
        if time.time() > end_time:
            raise Exception(f"File not found {year} within time")
        continue

    return True


def move_to_downloads(year: int) -> bool:
    files = os.listdir(TMP_DIR)
    assert len(files) == 1
    src = os.path.join(TMP_DIR, files[0])
    dest_file_name = str(year) + ".xlsx"
    dest = os.path.join(DOWNLOAD_DIR, dest_file_name)
    os.rename(src, dest)
    assert os.path.exists(dest)
    print(f"TMP_DIR: {len(os.listdir(TMP_DIR))}")
    return True


def main(headless: bool = True):
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    options = webdriver.ChromeOptions()

    # https://github.com/SeleniumHQ/selenium/issues/11637
    prefs = {
        "download.default_directory": TMP_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option(
        "prefs",
        prefs,
    )

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1420,1080")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--crash-dumps-dir=/tmp")
    # options.add_argument("--user-data-dir=~/.config/google-chrome")
    options.add_argument("--remote-debugging-port=9222")

    # executable_path = f"{TMP_DIR}/chromedriver"

    # mv /tmp/chromedriver /usr/local/bin/chromedriver

    # os.system(f'mv {executable_path} /usr/bin/chromedriver')
    # os.system('chmod +x /usr/bin/chromedriver')


    # os.system(f"sudo chmod +x {executable_path}")
    # os.system(f'cp {TMP_DIR}/chromedriver /usr/bin')

    # print(f"{executable_path=}")

    # service = Service(executable_path="/usr/bin/chromedriver")

    driver = webdriver.Chrome(options=options)
    driver.get(TARGET)

    # TODO(improve)
    time.sleep(10)

    print("Done")
    exit(0)

    home_element = driver.find_element(By.XPATH, XPATHS["card_home_funcoes"])

    assert home_element.is_displayed()

    home_element.click()

    time.sleep(15.0)

    tab_tabelas_element = driver.find_element(By.XPATH, XPATHS["tabelas"])

    assert tab_tabelas_element.is_displayed()

    tab_tabelas_element.click()

    time.sleep(4)

    # Campos da "seção" que não estão secionados
    assert len(driver.find_elements(By.CLASS_NAME, "QvExcluded_LED_CHECK_363636")) == 18

    # Cargos e Funções por padrão esta selecionado
    assert len(driver.find_elements(By.CLASS_NAME, "QvSelected_LED_CHECK_363636")) == 2

    # Estão duplicados pq tem duas div com a mesma classe
    selectables = driver.find_elements(By.CLASS_NAME, "QvOptional_LED_CHECK_363636")
    assert len(selectables) == 50

    valid_selections = [
        selection
        for selection in selectables
        if selection.get_attribute("title")
        in [*SELECTIONS_DIMENSIONS, *SELECTIONS_METRICS]
    ]
    assert len(valid_selections) == len(SELECTIONS)

    # NOTE: nem sempre mes e cargos esta selecionado
    first_selection_title = valid_selections[0].get_attribute("title")
    valid_selections[0].click()
    print(f"{first_selection_title=}")

    # TODO(improve): DOM changes
    time.sleep(5)

    # NOTE: Em cada seleção o DOM sofre alterações. Para cada click é
    # preciso buscar os mesmo elementos e filtrar.
    # Embora a classe seja a mesma as referências são diferentes
    _, *rest_dimensions_selections = SELECTIONS_DIMENSIONS
    dimensions_selected: list[str] = []

    for _ in range(0, len(rest_dimensions_selections)):
        # DOM changes
        time.sleep(5.0)
        elements = driver.find_elements(By.CLASS_NAME, "QvExcluded_LED_CHECK_363636")
        head, *_ = [
            selection
            for selection in elements
            if selection.get_attribute("title") in rest_dimensions_selections
            and selection.get_attribute("title") not in dimensions_selected
        ]

        year_title = head.get_attribute("title")
        assert isinstance(year_title, str)

        head.click()
        dimensions_selected.append(year_title)
        # print(f"Click for {year_title=}")

    print(f"Selections for dimensions, {dimensions_selected=}")

    time.sleep(5.0)

    metrics_selection = [
        selection
        for selection in driver.find_elements(
            By.CLASS_NAME, "QvOptional_LED_CHECK_363636"
        )
        if selection.get_attribute("title") == "CCE & FCE"
    ]
    print(f"{metrics_selection}")
    metrics_selection[0].click()
    print("CCE &  FCE clicked")

    time.sleep(3.0)

    _, *rest_metrics_selections = SELECTIONS_METRICS
    metrics_selected: list[str] = []

    for _ in range(0, len(rest_metrics_selections)):
        # DOM changes
        time.sleep(5.0)
        elements = driver.find_elements(By.CLASS_NAME, "QvExcluded_LED_CHECK_363636")
        head, *_ = [
            selection
            for selection in elements
            if selection.get_attribute("title") in rest_metrics_selections
            and selection.get_attribute("title") not in metrics_selected
        ]

        metric_title = head.get_attribute("title")
        assert isinstance(metric_title, str)

        head.click()
        metrics_selected.append(metric_title)
        # print(f"Click for {year_title=}")

    print(f"Selections for metrics, {metrics_selected=}")

    time.sleep(3.0)

    def open_menu_years():
        years_elements = [
            selection
            for selection in driver.find_elements(By.TAG_NAME, "div")
            if selection.get_attribute("title") == "Ano (total)"
        ]
        assert len(years_elements) > 0
        years_elements[0].click()

    def element_select_year(year: int):
        elements = [
            element
            for element in driver.find_elements(By.CLASS_NAME, "QvOptional")
            if element.get_attribute("title") is not None
        ]

        for e in elements:
            title = e.get_attribute("title")
            if title is not None and int(title) == year:
                return e

        raise Exception(f"Failed to select year {year}. Found {elements=}")

    def wait_hide_popup_element():
        popup_element_visible = True

        while popup_element_visible:
            elements_visible = [
                e
                for e in driver.find_elements(By.CLASS_NAME, "popupMask")
                if e.get_attribute("style") is not None
                and "display: block" in e.get_attribute("style")
            ]
            if len(elements_visible) == 0:
                break

        return True

    year_star = 2022
    year_end = 2023

    years = range(year_star, year_end + 1)

    for year in years:
        time.sleep(3.0)

        open_menu_years()

        time.sleep(3.0)

        element_year = element_select_year(year)

        element_year.click()

        time.sleep(10)

        download = [
            element
            for element in driver.find_elements(By.CLASS_NAME, "QvCaptionIcon")
            if element.get_attribute("title") == "Send to Excel"
        ]

        download[0].click()

        if wait_file_download(year):
            move_to_downloads(year)
            print(f"Download done for {year}")
            modal = driver.find_element(By.CLASS_NAME, "ModalDialog")
            modal.click()
            print("Modal Clicked")
            wait_hide_popup_element()
            remove_selected_year = [
                e
                for e in driver.find_elements(By.CLASS_NAME, "QvSelected")
                if e.get_attribute("title") is not None
                and e.get_attribute("title") == str(year)
            ]
            remove_selected_year[0].click()

            continue
        else:
            raise Exception(f"Failed to download xlsx for {year}")

    time.sleep(2.0)
    print("Done")

    print(f"Files: {os.listdir(DOWNLOAD_DIR)}")
    driver.close()


if __name__ == "__main__":
    _, *args = sys.argv
    headless = "--headless" in args

    setup_web_driver()

    main(headless=headless)
