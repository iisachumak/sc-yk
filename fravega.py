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

#URL semilla
#https://www.fravega.com/l/?keyword=celular+motorola&page=1

def fravega():
    # Interfaz de Streamlit
    st.title("Productos de Fravega")
    col1, col2 = st.columns(2)
    with col1:
        query = st.text_input("Ingrese el producto a buscar:")
    with col2:
        limit_pages = st.number_input("Número de páginas a buscar:", min_value=1, max_value=10, value=1)
    
    # Mover la lógica de búsqueda fuera del botón
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.last_query = None
        
    if st.button(label="Buscar", type="primary"):
        if query:  # Solo ejecutar si hay texto ingresado
            if st.session_state.last_query != query:
                st.session_state.df = extraer_info(query, limit_pages)
                st.session_state.last_query = query
    
    # Mostrar resultados si existen
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True)
        
        # Preparar el archivo Excel para descarga
        csv_buffer = BytesIO()
        st.session_state.df.to_excel(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Botón de descarga
        st.download_button(
            label=" 💾 Descargar XLSX",
            data=csv_buffer,
            file_name="productos_fravega.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"  # Agregar una key única
        )
        
        # Mostrar las imágenes
        st.subheader("Imágenes de los productos")
        cols = st.columns(4)
        
        for idx, (imagen_url, titulo) in enumerate(zip(st.session_state.df['Imagen_URL'], st.session_state.df['Nombre_del_producto'])):
            with cols[idx % 4]:
                try:
                    st.image(imagen_url, caption=titulo)
                except Exception as e:
                    st.error(f"Error al cargar la imagen: {str(e)}")
    elif query:
        st.warning("Por favor, presione el botón Buscar para obtener resultados")
    else:
        st.warning("Por favor, ingrese un producto para buscar")

def extraer_links(query, limit_pages):
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    # Movemos la creación de las listas aquí, fuera del bucle
    links_de_la_pagina = []
    links_de_las_imagenes = []

    pages = 1
    while pages <= limit_pages:
        url = f"https://www.fravega.com/l/?keyword={query}&page={pages}"
        driver.get(url)
        # Esperamos y cerramos el modal si existe
        try:
            modal_close = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='sc-eifrsQ bvPMIe']"))
            )
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)
            if modal_close:
                print("Modal encontrado")
                modal_close.click()
        except:
            pass  # Si no hay modal, continuamos

        # Esperamos que se carguen los productos
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//article[@class='sc-f0dec281-2 cKluyL']")))

        # Hacemos scroll para que se carguen los productos
        driver.execute_script("window.scrollBy({ top: 1200, behavior: 'smooth' });")
        time.sleep(2)
        driver.execute_script("window.scrollBy({ top: 2500, behavior: 'smooth' });")
        time.sleep(2)

        #obtenemos los links de las fichas
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']"))
        )
        links_products = driver.find_elements(By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']")
        
        #obtenemos los links de las imagenes
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//img[@class='sc-1362d5fd-0 kvoSnj']"))
        )
        links_images = driver.find_elements(By.XPATH, "//img[@class='sc-1362d5fd-0 kvoSnj']")

        #recorremos los links de las fichas y los agregamos a la lista
        for tags_a in links_products:
            href = tags_a.get_attribute("href")
            if href:  # Solo agregamos el link si no es None
                links_de_la_pagina.append(href)
                
        #recorremos los links de las imagenes y los agregamos a la lista
        for tags_img in links_images:
            src = tags_img.get_attribute("src")
            if src:  # Solo agregamos el link si no es None
                links_de_las_imagenes.append(src)
            
        #imprimimos la lista de links de las fichas
        print(links_de_la_pagina)
        #imprimimos la lista de links de las imagenes
        print(links_de_las_imagenes)
        #incrementamos la pagina
        pages += 1

    # Cerramos el driver al finalizar
    driver.quit()
    print(f"len(links_de_la_pagina): {len(links_de_la_pagina)}")
    return links_de_la_pagina, links_de_las_imagenes

def extraer_info(query, limit_pages):
    # Obtener tanto los links de productos como de imágenes
    links_productos, links_imagenes = extraer_links(query, limit_pages)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    #Selenium
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)


    # Crear listas separadas para cada columna
    titulos = []
    seller = []
    precios_antes = []
    descuentos = []
    precios = []
    urls = []
    imagenes = []
    atributos = []

    # Crear barra de progreso
    progress_bar = st.progress(0)
    total_links = len(links_productos)

    for i, (link, imagen) in enumerate(zip(links_productos, links_imagenes)):
        try:
            # Actualizar barra de progreso
            progress = (i + 1) / total_links
            progress_bar.progress(progress, f"Procesando producto {i + 1} de {total_links}")
            
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar elementos
            titulo = soup.find('h1', class_='sc-2628e4d4-8 kMpaAN')
            precio = soup.find('span', class_='sc-1d9b1d9e-0 sc-2628e4d4-3 OZgQ jLjuuY')
            precio_antes = soup.find('span', class_='sc-66d25270-0 sc-2628e4d4-4 eiLwiO kGdyWX')
            vendido_por = soup.find('p', class_='sc-4f63cfa5-6 ebPHuJ')
            descuento = soup.find('span', class_='sc-e2aca368-0 sc-2628e4d4-5 juwGno ehTQUi')

            # Verificar y extraer datos
            titulo_texto = titulo.text.strip() if titulo else "Sin título"
            precio_texto = precio.text.strip() if precio else "Sin precio"
            precio_antes_texto = precio_antes.text.strip() if precio_antes else "Sin precio"
            vendido_por_texto = vendido_por.text.strip() if vendido_por else "Otro seller"
            descuento_texto = descuento.text.strip() if descuento else "Sin descuento"

            atributos_texto = ""  # Inicializamos como string vacío
            # Atributos con selenium
            try:
                driver.get(link)
                modal_close = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@class='sc-eifrsQ bvPMIe']"))
                )
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(1)
                if modal_close:
                    print("Modal encontrado")
                    modal_close.click()
                
                # Hacemos scroll para que se carguen los productos
                driver.execute_script("window.scrollBy({ top: 1500, behavior: 'smooth' });")
                time.sleep(1)

                atributos_producto = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//ul[@class='sc-24cb27c0-3 dlgfHc']"))
                )
                if atributos_producto:
                    atributos_lista = atributos_producto.find_elements(By.XPATH, "//span[@class='specName']")
                    atributos_valores = atributos_producto.find_elements(By.XPATH, "//span[@class='specValue']")
                    for atributo, valor in zip(atributos_lista, atributos_valores):
                        atributos_texto += f"{atributo.text.strip()}: {valor.text.strip()} | "
                    
                    if not atributos_texto:  # Si no se encontraron atributos
                        atributos_texto = "Sin atributos"
                else:
                    atributos_texto = "Sin atributos"

                print(atributos_texto)
                
            except Exception as e:
                print(f"Error al cargar {link}: {str(e)}")

            # Agregar datos a las listas
            titulos.append(titulo_texto)    
            seller.append(vendido_por_texto)
            precios.append(precio_texto)
            precios_antes.append(precio_antes_texto)
            descuentos.append(descuento_texto)
            urls.append(link)
            imagenes.append(imagen)  # Agregar la URL de la imagen
            atributos.append(atributos_texto)

            print(f"Producto agregado: {titulo_texto} - {precio_texto}")
            
        except Exception as e:
            print(f"Error al procesar {link}: {str(e)}")
            titulos.append("Error al cargar")
            precios.append("Error al cargar")
            precios_antes.append("Error al cargar")
            seller.append("Error al cargar")
            urls.append(link)
            imagenes.append("Sin imagen")
            descuentos.append("Sin descuento")
            atributos.append("Sin atributos")

    # Crear el DataFrame con las listas, incluyendo las imágenes
    df = pd.DataFrame({
        'Nombre_del_producto': titulos,
        'Seller': seller,
        'Precio_antes': precios_antes,
        'Descuento': descuentos,
        'Precio': precios,
        'Atributos': atributos,
        'URL': urls,
        'Imagen_URL': imagenes,  # Nueva columna para las imágenes
    })

    return df