import sys
import os
import time
from selenium import webdriver

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

TARGET = "http://painel.pep.planejamento.gov.br/QvAJAXZfc/opendoc.htm?document=painelpep.qvw&lang=en-US&host=Local&anonymous=true"

XPATHS = {
    # Cargos e Funções
    "card_home_funcoes": "/html/body/div[5]/div/div[88]",
    # Aba Tabelas
    "tabelas": "/html/body/div[5]/div/div[280]/div[3]/table/tbody/tr/td",
    "faca_voce_mesmo": "/html/body/div[6]/div/div[532]/div[2]/table/tbody/tr/td",
}

# SELECTIONS = [
#     # Seção
#     {
#         # "xpath": "/html/body/div[6]/div/div[259]/div[2]/div/div[1]/div[5]/div[2]/div[2]",
#         "xpath": "/html/body/div[6]/div/div[259]/div[2]/div/div[1]/div[5]",
#         "title": "Cargos e Funções",
#     }
# ]


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

SELECTIONS_METRICS = [
    "DAS e correlatas",
    "CCE & FCE",
]

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "download")

def exists_crdownload_file() -> bool:
   files = os.listdir(DOWNLOAD_DIR)
   some_crdownload = [file for file in files if file.endswith('.crdownload')]
   return len(some_crdownload) > 0

def main(headless: bool = True):

    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    options = webdriver.ChromeOptions()

    # https://github.com/SeleniumHQ/selenium/issues/11637
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
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

    driver = webdriver.Chrome(options=options)
    driver.get(TARGET)

    # TODO(improve)
    time.sleep(10)
    # WebDriverWait(driver, TIMEOUT).until(
    #     expected_conditions.presence_of_element_located((By.XPATH, XPATHS["card_home_funcoes"]))
    # )

    home_element = driver.find_element(By.XPATH, XPATHS["card_home_funcoes"])

    assert home_element.is_displayed()

    home_element.click()

    time.sleep(15.0)
    # WebDriverWait(driver, TIMEOUT).until(
    #     expected_conditions.presence_of_element_located((By.XPATH, XPATHS["tabelas"]))
    # )

    tab_tabelas_element = driver.find_element(By.XPATH, XPATHS["tabelas"])

    assert tab_tabelas_element.is_displayed()

    tab_tabelas_element.click()

    # time.sleep(3)
    # WebDriverWait(driver, TIMEOUT + 20).until(
    #     expected_conditions.presence_of_element_located((By.XPATH, XPATHS["faca_voce_mesmo"]))
    # )

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

    # TODO: nem sempre mes e cargos e selecionado
    # Mês e Cargos
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

    # for _ in range(0, 2):
    #     # DOM changes
    #     time.sleep(5.0)
    #     elements = driver.find_elements(By.CLASS_NAME, "QvExcluded_LED_CHECK_363636")
    #     head, *_ = [
    #         selection
    #         for selection in elements
    #         if selection.get_attribute("title") in rest_dimensions_selections
    #         and selection.get_attribute("title") not in dimensions_selected
    #     ]

    #     title = head.get_attribute("title")
    #     assert isinstance(title, str)

    #     head.click()
    #     dimensions_selected.append(title)
    #     print(f"Click for {title=}")

    # print(
    #     f"Selections for dimensions, {len(dimensions_selected)}, {dimensions_selected=}"
    # )

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

    time.sleep(10)

    # WebDriverWait(driver, 30).until(
    #     expected_conditions.presence_of_element_located(
    #         (By.CLASS_NAME, "QvFrame Document_CH339")
    #     )
    # )

    # time.sleep(10.0)

    # das_elements = driver.find_elements(
    #         By.CLASS_NAME, "QvExcluded_LED_CHECK_363636"
    # )
    # das = [
    #     selection
    #     for selection in das_elements
    #     if selection.get_attribute("title") == "DAS e correlatas"
    # ]

    # print(f"{das=}, {das_elements=}")

    # for i in das_elements:
    #     try:
    #         title = i.get_attribute("title")
    #         print(f"{title}")
    #     except:
    #         print("Invalid")

    # das[0].click()

    # time.sleep(5)

    menu_ano = [
        selection
        for selection in driver.find_elements(By.TAG_NAME, "div")
        if selection.get_attribute("title") == "Ano (total)"
    ]
    print(f"{menu_ano}")

    menu_ano[0].click()

    # WebDriverWait(driver, 30).until(
    #     expected_conditions.presence_of_element_located(
    #         (By.CLASS_NAME, "QvFrame Document_CH339")
    #     )
    # )

    time.sleep(3.0)
    anos = [
        element
        for element in driver.find_elements(By.CLASS_NAME, "QvOptional")
        if element.get_attribute("title") in ["2023"]
    ]

    print(f"{len(anos)=}")

    anos[0].click()

    time.sleep(10)

    download = [
        element
        for element in driver.find_elements(By.CLASS_NAME, "QvCaptionIcon")
        if element.get_attribute("title") == "Send to Excel"
    ]

    download[0].click()

    # wait_for_download = True

    # while wait_for_download:
    #     if exists_crdownload_file():
    #         continue
    #     else:
    #         break

    time.sleep(10)

    print("Done")
    driver.close()


if __name__ == "__main__":
    _, *args = sys.argv
    headless = "--headless" in args
    main(headless=headless)
