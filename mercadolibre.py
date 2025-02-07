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
import time

def extraer_links(query, limit_pages):
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-images')  # Deshabilita la carga de imágenes para mayor velocidad

    driver = webdriver.Chrome(options=options)
    
    links_de_la_pagina = []
    pages = 1
    
    while pages <= limit_pages:
        try:
            # URL base para la primera página, URL con offset para páginas posteriores
            url = f"https://listado.mercadolibre.com.ar/{query}" if limit_pages == 1 else f"https://listado.mercadolibre.com.ar/{query}_Desde_{(pages-1)*50+1}"
            driver.get(url)
            
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)
            
            card_product = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='poly-component__title']"))
            )
            

            # Scroll primero hasta la mitad y luego hasta el final
            altura_total = driver.execute_script("return document.body.scrollHeight")
            # Scroll hasta la mitad
            for _ in range(4):
                driver.execute_script("window.scrollBy({ top: 3400, behavior: 'smooth' });")
                time.sleep(2)
            
            for product in card_product:
                links_de_la_pagina.append(product.get_attribute("href"))
            
            pages += 1
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break
    
    driver.quit()
    print(len(links_de_la_pagina))
    return links_de_la_pagina

        
def extraer_info(query, limit_pages):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    links_productos = extraer_links(query, limit_pages)
    #
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-images')  # Deshabilita la carga de imágenes para mayor velocidad
    driver = webdriver.Chrome(options=options)
    #
    nombre_producto = []
    precio_producto = []
    precio_antes_producto = []
    descuento_producto = []
    seller_producto = []
    urls = []
    mismo_precio_en_cuotas_producto = []
    cuotas_producto = []
    puntaje_producto = []
    producto_full = []
    tipo_de_envio_producto = []
    producto_vendido_por = []
    #
    for link in links_productos:
        try:

            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            driver.get(link)
            
            # Esperar a que el cuerpo de la página cargue
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)
            # Realizar scroll de manera más eficiente
            '''
            for _ in range(3):
                driver.execute_script("window.scrollBy({ top: 3000, behavior: 'smooth' });")
                time.sleep(2)
            
            # Esperar explícitamente a que los elementos principales estén presentes
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'ui-pdp-title'))
            )
            # Actualizar el soup después del scroll y la carga dinámica
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            '''
            
            #PUNTAJE
            try:
                puntaje = soup.find('a', class_='ui-pdp-review__label ui-pdp-review__label--link')
                puntaje_producto.append(puntaje.text if puntaje else "No tiene")
            except:
                puntaje_producto.append("No se encontró puntaje")

            #NOMBRE
            try:
                nombre = soup.find('h1', class_='ui-pdp-title')
                nombre_producto.append(nombre.text if nombre else "No se encontró nombre")
            except:
                nombre_producto.append("No se encontró nombre")

            #PRECIO ANTES
            try:
                precio_antes = soup.find('s', class_='andes-money-amount ui-pdp-price__part ui-pdp-price__original-value andes-money-amount--previous andes-money-amount--cents-superscript andes-money-amount--compact')
                precio_antes_producto.append(precio_antes.text if precio_antes else "No tiene")
            except:
                precio_antes_producto.append("No se encontró precio anterior")

            #PRECIO
            try:
                precio = soup.find('span', class_='andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact')
                precio_producto.append(precio.text if precio else "No se encontró precio")
            except:
                precio_producto.append("No se encontró precio")
            time.sleep(2)
            #DESCUENTO
            try:
                descuento = soup.find('span', class_='ui-pdp-price__second-line__label ui-pdp-color--GREEN ui-pdp-size--MEDIUM ui-pdp-family--REGULAR')
                if descuento:
                    descuento_producto.append(descuento.text if descuento else "No tiene")
                else:
                    descuento_producto.append("No tiene")
            except:
                descuento_producto.append("No se encontró descuento")

            #MISMO PRECIO EN CUOTAS
            try:
                mismo_precio_en_cuotas = soup.find('p', class_='ui-pdp-color--GREEN ui-pdp-size--MEDIUM ui-pdp-family--REGULAR')
                mismo_precio_en_cuotas_producto.append(mismo_precio_en_cuotas.text if mismo_precio_en_cuotas else "No tiene")
            except:
                mismo_precio_en_cuotas_producto.append("No se encontró mismo precio en cuotas")

            #CUOTAS
            try:
                cuotas = soup.find('p', class_='ui-pdp-color--BLACK ui-pdp-size--MEDIUM ui-pdp-family--REGULAR')
                cuotas_producto.append(cuotas.text if cuotas else "No tiene")
            except:
                cuotas_producto.append("No se encontró cuotas")

            for _ in range(3):
                driver.execute_script("window.scrollBy({ top: 2000, behavior: 'smooth' });")
                time.sleep(2)

            #TIPO DE ENVIO
            try:
                # Esperar a que los elementos de envío se carguen
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-pdp-media__title"))
                )
                
                
                tipos_de_envio = soup.find_all('p', class_='ui-pdp-color--BLACK ui-pdp-family--REGULAR ui-pdp-media__title')
                if tipos_de_envio:
                    tipos_envio_texto = " | ".join([tipo.text.strip() for tipo in tipos_de_envio])
                    tipo_de_envio_producto.append(tipos_envio_texto)
                else:
                    tipo_de_envio_producto.append("No tiene")
            except Exception as e:
                print(f"Error en tipo de envío: {str(e)}")
                tipo_de_envio_producto.append("No se encontró tipo de envio")

            #PRODUCTO FULL
            try:
                full = soup.find('div', class_='ui-pdp-media ui-pdp-promotions-pill-label__icon')
                producto_full.append("Si es producto full" if full else "No tiene")
            except:
                producto_full.append("No se encontró producto full")

            #SELLER
            try:
                seller = soup.find('span', class_='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--SEMIBOLD ui-seller-data-header__title non-selectable')
                seller_producto.append(seller.text if seller else "No se encontró seller")
            except:
                seller_producto.append("No se encontró seller")

            #PRODUCTO VENDIDO POR
            try:
                producto_vendido = soup.find('span', class_='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--REGULAR ui-seller-data-header__title non-selectable')
                producto_vendido_por.append(producto_vendido.text if producto_vendido else "No tiene")
            except:
                producto_vendido_por.append("No se encontró producto vendido por")


            urls.append(link)

            print(nombre_producto, precio_producto, precio_antes_producto, descuento_producto, mismo_precio_en_cuotas_producto, cuotas_producto, puntaje_producto, producto_full, tipo_de_envio_producto, producto_vendido_por)
            

        except Exception as e:
            # Si hay un error, agregar valores vacíos para mantener la consistencia
            nombre_producto.append("Error")
            precio_producto.append("Error")
            precio_antes_producto.append("Error")
            descuento_producto.append("Error")
            seller_producto.append("Error")
            mismo_precio_en_cuotas_producto.append("Error")
            cuotas_producto.append("Error")
            puntaje_producto.append("Error")
            producto_full.append("Error")
            tipo_de_envio_producto.append("Error")
            producto_vendido_por.append("Error")
            urls.append(link)
            print(f"Error procesando link {link}: {str(e)}")
            continue
            

    driver.quit()
    
    df = pd.DataFrame({
        'Nombre': nombre_producto,
        'Precio': precio_producto,
        'Precio Anterior': precio_antes_producto,
        'Descuento': descuento_producto,
        'Mismo precio en cuotas': mismo_precio_en_cuotas_producto,
        'Cuotas': cuotas_producto,
        'Seller': seller_producto,
        'Producto vendido por': producto_vendido_por,
        'Puntaje': puntaje_producto,
        'Producto full': producto_full, 
        'Tipo de envio': tipo_de_envio_producto,
        'URL': urls


    })
    
    df.to_excel('mercadolibre.xlsx', index=False)

    return df
        

prueba = extraer_info("celular", 1)
print(prueba)
