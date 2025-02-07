from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

def extraer_url(query, limit_pages):
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)

    url = f"https://listado.mercadolibre.com.ar/{query}"
    driver.get(url)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(2)

    links_productos = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[@class='poly-component__title']"))
    )
    links_de_las_paginas = []

    for tag_a in links_productos:
        links_de_las_paginas.append(tag_a.get_attribute('href'))
    
    nombre =  []
    rating = []
    precio_anterior = []
    precio = []
    descuento = []
    mismo_precio_en_cuotas = []
    envios = []
    seller = []
    vendido_por = []
    atributos = []
    url = []

    productos = 0
    for link in links_de_las_paginas:
        try:
            try:
                driver.get(link)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(3)
            except Exception as e:
                print(e)
            
            # NOMBRE
            # NOMBRE
            try:
                nombre_producto = driver.find_element(By.XPATH, "//h1[@class='ui-pdp-title']")
                nombre_producto = nombre_producto.text
            except Exception as e:
                nombre_producto = "none"
                print(e)
            nombre.append(nombre_producto)

            # RATING
            try:
                rating_producto = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='ui-pdp-header__info']"))  # ¡Aquí hay una tupla!
                )
                rating_producto = rating_producto.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            except Exception as e:
                rating_producto = "none"
                print(e)
            rating.append(rating_producto)
            
            # PRECIO ANTES
            try:
                precio_antes = driver.find_element(By.XPATH, "//s[@class='andes-money-amount ui-pdp-price__part ui-pdp-price__original-value andes-money-amount--previous andes-money-amount--cents-superscript andes-money-amount--compact']")
                precio_antes = precio_antes.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            except Exception as e:
                precio_antes = "none"
                print(e)
            precio_anterior.append(precio_antes)

            # PRECIO
            try:
                precio_producto = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@class='andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact']"))
                )
                precio_producto = precio_producto.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            except Exception as e:
                precio_producto = "none"
                print(e)
            precio.append(precio_producto)

            # DESCUENTO
            try:
                descuento_producto = driver.find_element(By.XPATH, "//span[@class='andes-money-amount__discount ui-pdp-family--REGULAR']")
                descuento_producto = descuento_producto.text
            except Exception as e:
                descuento_producto = 'none'
                print(e)
            descuento.append(descuento_producto)
                
            try:
                mismo_precio_cuotas = driver.find_element(By.XPATH, "//div[@class='ui-pdp-price__subtitles']")
                mismo_precio_cuotas = mismo_precio_cuotas.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            except Exception as e:
                mismo_precio_cuotas = 'none'
                print(e)
            mismo_precio_en_cuotas.append(mismo_precio_cuotas)

            # ENVIO
            try:
                # Usar find_elements para obtener una lista de elementos
                tipo_envio = driver.find_elements(By.XPATH, "//div[@class='ui-pdp-media__body']")
                
                # Extraer el texto de cada elemento y limpiarlo
                envio_texts = [tipo.text.replace('\n', '').replace('\r', '').replace('\t', '').strip() for tipo in tipo_envio]
                
                # Unir los textos en una sola cadena
                envios.append(", ".join(envio_texts))
                
            except Exception as e:
                envios.append("none")
                print(f"Error: {e}")

            # SELLER
            try:
                seller_producto = driver.find_element(By.XPATH, "//span[@class='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--SEMIBOLD ui-seller-data-header__title non-selectable']")
                seller_producto = seller_producto.text
            except Exception as e:
                seller_producto = 'none'
                print(e)
            seller.append(seller_producto)

            try:
                producto_vendido_por = driver.find_element(By.XPATH, "//span[@class='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--REGULAR ui-seller-data-header__title non-selectable']")
                producto_vendido_por = producto_vendido_por.text
            except Exception as e:
                producto_vendido_por = 'none'
            vendido_por.append(producto_vendido_por)
            
            # - - ui-pdp-collapsable__action ui-vpp-highlighted-specs__striped-collapsed__action
            driver.execute_script("window.scrollBy({ top: 2500, behavior: 'smooth' });")
            time.sleep(2)
            
            try:
                cookie_banner = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='cookie-consent-banner-opt-out__action cookie-consent-banner-opt-out__action--primary cookie-consent-banner-opt-out__action--key-accept']"))
                )
                cookie_banner.click()
            except Exception as e:
                print("No se encontró el banner de cookies o no se pudo cerrar:", e)

            # Ahora intenta hacer clic en el botón deseado
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ui-pdp-collapsable__action"))
                )
                button.click()
            except Exception as e:
                print("No se pudo hacer clic en el botón:", e)
            # - - 

            # ATRIBUTOS
            try:
                # Usamos find_elements para obtener una lista de elementos
                lista_atributos = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@class='ui-vpp-highlighted-specs__striped-specs']"))
                )
                
                # Limpiamos el texto y lo añadimos a la lista atributos
                texto_limpio = [lista.text.replace('\n', '').replace('\r', '').replace('\t', '').strip() for lista in lista_atributos]
                atributos.append(", ".join(texto_limpio))  # Join the list into a single string

            except Exception as e:
                # Si ocurre una excepción, asignamos 'none' a atributos
                atributos.append('none')
                print(f"Ocurrió un error: {e}")
            
            # URL
            url.append(link)

            productos += 1

            print(atributos)
            print(productos)
            driver.back()

        except Exception as e:
            print(e)
            driver.back()

    df = pd.DataFrame({
        'Nombre': nombre,
        'Rating': rating,        
        'Precio antes' : precio_anterior,
        'Precio': precio,
        'Descuento': descuento,
        'Cuotas': mismo_precio_en_cuotas,
        'Envios y Garantía': envios,
        'Seller': seller,
        'Atributos': atributos,
        'Vendido por': vendido_por,
        'URL': url
    })

    df.to_excel('mercadolibre.xlsx', index=False)

    return df

prueba = extraer_url("celular", 1)
print(prueba)