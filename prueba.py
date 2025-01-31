from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

url = "https://www.fravega.com/p/tv-led-32-kodak-we-32mt005hg-502627/"

options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

# Inicializar el navegador
driver = webdriver.Chrome(options=options)

# Cargar la página
driver.get(url)

descripcion = []
try:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[@class='specName']")))
    descripcion_texto = driver.find_elements(By.XPATH, "//span[@class='specName']")
    if descripcion_texto:
        for elemento in descripcion_texto:
            descripcion.append(elemento.text.strip())
except:
    print("No se encontraron elementos con la clase especificada")

print(descripcion)
driver.quit()  # Importante cerrar el navegador

