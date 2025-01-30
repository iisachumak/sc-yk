from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st
from io import BytesIO


#https://www.fravega.com/l/?keyword=celular+motorola&page=1

def prueba(query):
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    pages = 1

    while pages <= 6:
        url = f"https://www.fravega.com/l/?keyword={query}&page={pages}"
        driver.get(url)
        
        # Esperamos y cerramos el modal si existe
        try:
            modal_close = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='sc-eifrsQ bvPMIe']"))
            )
            if modal_close:
                print("Modal encontrado")
                modal_close.click()
        except:
            pass  # Si no hay modal, continuamos
            
        # Esperamos que se carguen los productos
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']")))

        # Hacemos scroll para que se carguen los productos
        driver.execute_script("window.scrollBy({ top: 100000, behavior: 'smooth' });")

        #obtenemos los links de las fichas
        links_products = driver.find_elements(By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']")
        #obtenemos los links de las imagenes
        links_images = driver.find_elements(By.XPATH, "//img[@class='sc-1362d5fd-0 kvoSnj']")

        #creamos una lista para almacenar los links de las fichas
        links_de_la_pagina = []
        links_de_las_imagenes = []

        #recorremos los links de las fichas y los agregamos a la lista
        for tags_a in links_products:
            links_de_la_pagina.append(tags_a.get_attribute("href"))
        #recorremos los links de las imagenes y los agregamos a la lista
        for tags_img in links_images:
            links_de_las_imagenes.append(tags_img.get_attribute("src"))
            
        #imprimimos la lista de links de las fichas
        print(links_de_la_pagina)
        #imprimimos la lista de links de las imagenes
        print(links_de_las_imagenes)
        #incrementamos la pagina
        pages += 1

    # Cerramos el driver al finalizar
    driver.quit()
    return links_de_la_pagina, links_de_las_imagenes

link = prueba("celular motorola")
print(link)
