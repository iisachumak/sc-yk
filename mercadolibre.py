from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import streamlit as st
from io import BytesIO

def mercadolibre():
    # Interfaz de Streamlit
    st.title("Productos de Mercadolibre")
    col1, col2, col3 = st.columns(3)
    with col1:
        query = st.text_input("Ingrese el producto a buscar:")
    with col2:
        limit_pages = st.number_input("Número de páginas a buscar:", min_value=1, max_value=10, value=1)
    with col3:
        limit_products = st.number_input("Número de productos a extraer:", min_value=1, value=10)
    
    # Mover la lógica de búsqueda fuera del botón
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.last_query = None
        
    if st.button(label="Buscar", type="primary"):
        if query:  # Solo ejecutar si hay texto ingresado
            if st.session_state.last_query != query:
                st.session_state.df = extraer_info(query, limit_pages, limit_products)
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
            file_name="productos_mercadolibre.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"  # Agregar una key única
        )
        
        # Mostrar las imágenes
        st.subheader("Imágenes de los productos")
        cols = st.columns(4)
        
        for idx, (imagen_url, titulo, url_sitio) in enumerate(zip(st.session_state.df['Imagen_URL'], st.session_state.df['Nombre_del_producto'],  st.session_state.df['URL'])):
            with cols[idx % 4]:
                try:
                    st.image(imagen_url, caption=titulo)
                    st.link_button("Ir a la publicación", url_sitio)
                except Exception as e:
                    st.error(f"Error al cargar la imagen: {str(e)}")
    elif query:
        st.warning("Por favor, presione el botón Buscar para obtener resultados")
    else:
        st.warning("Por favor, ingrese un producto para buscar")

def extraer_url(query, limit_pages, limit_products):
    options = Options()
    options.add_argument("--no-sandbox")  # Desactiva el sandboxing
    options.add_argument("--headless")    # Ejecuta en modo headless
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memoria
    options.add_argument("--disable-gpu")  # Desactiva la GPU
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)

    pages = 1
    links_de_las_paginas = []  # Inicializa la lista fuera del bucle

    url = f"https://listado.mercadolibre.com.ar/{query}"
    driver.get(url)
    
    while pages <= limit_pages and len(links_de_las_paginas) < limit_products:
        
        with st.spinner(f"Buscando productos..."):

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)

            # Cerrar el modal si el límite de páginas es mayor a 1
            if limit_pages > 1:
                try:
                    cookie_banner = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@class='cookie-consent-banner-opt-out__action cookie-consent-banner-opt-out__action--primary cookie-consent-banner-opt-out__action--key-accept']"))
                    )
                    cookie_banner.click()
                except Exception as e:
                    print("No se encontró el banner de cookies o no se pudo cerrar:", e)
            
            for _ in range(4):
                    driver.execute_script("window.scrollBy({ top: 3400, behavior: 'smooth' });")
                    time.sleep(2)

            # Extraer los enlaces de los productos
            links_productos = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@class='poly-component__title']"))
            )

            for tag_a in links_productos:
                if len(links_de_las_paginas) < limit_products:
                    links_de_las_paginas.append(tag_a.get_attribute('href'))
                else:
                    break

            # Hacer clic en el botón de paginación "siguiente" si no es la última página
            if pages < limit_pages and len(links_de_las_paginas) < limit_products:
                try:
                    siguiente_boton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@class='andes-pagination__link']//span[contains(text(), 'Siguiente')]"))
                    )
                    siguiente_boton.click()
                    time.sleep(2)  # Esperar a que la página se cargue
                except Exception as e:
                    print("No se pudo hacer clic en el botón 'Siguiente':", e)
                    break  # Salir del bucle si no se puede hacer clic en "Siguiente"
            
            if pages == limit_pages or len(links_de_las_paginas) >= limit_products:
                driver.quit()
            
            pages += 1
            print(len(links_de_las_paginas))
        
        return links_de_las_paginas

def extraer_info(query, limit_pages, limit_products):
    links_productos = extraer_url(query, limit_pages, limit_products)

    options = Options()
    options.add_argument("--no-sandbox")  # Desactiva el sandboxing
    options.add_argument("--headless")    # Ejecuta en modo headless
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memoria
    options.add_argument("--disable-gpu")  # Desactiva la GPU
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    nombre =  []
    rating = []
    precio_anterior = []
    precio = []
    descuento = []
    vendidos = []
    mismo_precio_en_cuotas = []
    envios = []
    seller = []
    vendido_por = []
    atributos = []
    imagenes = []
    url = []
    producto_full = []

    # Inicializar la barra de progreso
    progress_bar = st.progress(0)
    total_links = len(links_productos)


    # EMPIEZA EL RECORRIDO
    for idx, link in enumerate(links_productos):
        try:
            try:
                driver.get(link)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(3)
            except Exception as e:
                print(e)

            # BARRA DE PROGRESO
            try:
                progress_value = (idx + 1) / total_links
                # Actualizar la barra de progreso
                # Mostrar el mensaje de progreso
                progress_bar.progress(progress_value, f"Procesando productos {idx + 1} de {total_links}")
                
            except Exception as e:
                print(e)
                driver.back()
            # NOMBRE
            try:
                nombre_producto = driver.find_element(By.XPATH, "//h1[@class='ui-pdp-title']")
                nombre_producto = nombre_producto.text
                #st.toast(nombre_producto)
                st.toast(nombre_producto)
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

            # CUOTAS     
            try:
                mismo_precio_cuotas = driver.find_element(By.XPATH, "//div[@class='ui-pdp-price__subtitles']")
                mismo_precio_cuotas = mismo_precio_cuotas.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            except Exception as e:
                mismo_precio_cuotas = 'none'
                print(e)
            mismo_precio_en_cuotas.append(mismo_precio_cuotas)

            # VENDIDOS
            try:
                cantidad_vandidos = driver.find_element(By.XPATH, "//span[@class='ui-pdp-subtitle']")
                cantidad_vandidos = cantidad_vandidos.text
            except:
                print(e)
                cantidad_vandidos = "none"
            
            vendidos.append(cantidad_vandidos)

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
            
            #PRODUCTO FULL
            try:
                full = driver.find_element(By.XPATH, "//div[@class='ui-pdp-media ui-pdp-promotions-pill-label__icon']")
                if full:
                    producto_full.append("Si")
                else:
                    producto_full.append("No")
            except:
                producto_full.append("No")

            # URL IMAGEN
            try:
                url_img = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@class='ui-pdp-image ui-pdp-gallery__figure__image']"))
                )
                img = url_img.get_attribute('src')
                imagenes.append(img)
            except Exception as e:
                print(e)

            # SELLER
            try:
                seller_producto = driver.find_element(By.XPATH, "//span[@class='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--SEMIBOLD ui-seller-data-header__title non-selectable']")
                seller_producto = seller_producto.text
            except Exception as e:
                seller_producto = 'none'
                print(e)
            seller.append(seller_producto)

            # VENDIDO POR
            try:
                producto_vendido_por = driver.find_element(By.XPATH, "//span[@class='ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--REGULAR ui-seller-data-header__title non-selectable']")
                producto_vendido_por = producto_vendido_por.text
            except Exception as e:
                producto_vendido_por = 'none'
            vendido_por.append(producto_vendido_por)
            
            # - - ui-pdp-collapsable__action ui-vpp-highlighted-specs__striped-collapsed__action
            driver.execute_script("window.scrollBy({ top: 2500, behavior: 'smooth' });")
            time.sleep(2)
            # CERRAMOS BANNER DE COOKIES
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

            # CERRAMOS
            driver.back()

        except Exception as e:
            print(e)
            driver.back()

    df = pd.DataFrame({
        'Nombre_del_producto': nombre,
        'Rating': rating,        
        'Precio antes' : precio_anterior,
        'Precio': precio,
        'Descuento': descuento,
        'Cuotas': mismo_precio_en_cuotas,
        'Envios y Garantía': envios,
        'Producto_full': producto_full,
        'Seller': seller,
        'Vendido por': vendido_por,
        'Atributos': atributos,
        'URL': url,
        'Imagen_URL': imagenes,
    })

    return df