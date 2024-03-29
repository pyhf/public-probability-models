from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

import json

url = "https://twiki.cern.ch/twiki/bin/view/AtlasPublic"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

with webdriver.Chrome(options=options) as driver:
    driver.get(url)

    # it's asynchronous so we force a wait
    WebDriverWait(driver, timeout=60).until(
        lambda d: driver.find_element(
            By.CSS_SELECTOR, 'select[name="publications_length"]'
        )
    )

    # click to expand other keywords
    driver.find_element(By.CSS_SELECTOR, "#row_show_signature span").click()
    # select the likelihood available keyword
    driver.find_element(By.ID, "Analysischaracteristics_Likelihood@available").click()
    # show all publications
    Select(
        driver.find_element(By.CSS_SELECTOR, 'select[name="publications_length"]')
    ).select_by_visible_text("All")
    # get all publications visible / left in the table
    rows = driver.find_elements("css selector", "#publications > tbody > tr")

    data = []
    # iterate and print information
    for row in rows:
        elements = row.find_elements("css selector", "td")
        # elements are following the ordering of the table on the Twiki
        # Currently:
        # Short Title, Group, Journal Reference, Date, \sqrt{s} (TeV), L, Links
        short_title = elements[0]
        physics_group = elements[1]
        date = elements[3]
        com_energy_tev = elements[4]
        luminosity = elements[5]
        links = elements[-1].find_elements("css selector", "a")

        hepdata = [
            link.get_property("href")
            for link in links
            if link.text.lower() == "hepdata"
        ]
        document = [
            link.get_property("href")
            for link in links
            if link.text.lower() == "documents"
        ]

        data.append(
            dict(
                title=short_title.text,
                physicsGroup=physics_group.text,
                date=date.text,
                comEnergyTeV=com_energy_tev.text,
                luminosity=luminosity.text,
                hepdata=hepdata[0] if hepdata else None,
                link=document[0],
            )
        )

    print(json.dumps(data, indent=4, sort_keys=True))
