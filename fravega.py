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


def fravega():
    opts = Options()
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def get_products_links(query):
        driver = webdriver.Chrome(options=opts)
        try:
            driver.get(f"https://www.fravega.com/l/?keyword={query}")

            # Asegurarse de que los productos se han cargado
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']"))
            )

            links_products = driver.find_elements(By.XPATH, "//a[@class='sc-f0dec281-0 kYvfPh']")
            links_de_la_pagina = []
            #
            links_images = driver.find_elements(By.XPATH, "//img[@class='sc-1362d5fd-0 kvoSnj']")
            links_de_las_imagenes = []

            for tags_a in links_products:
                href = tags_a.get_attribute("href")
                if href:
                    links_de_la_pagina.append(href)

            for tags_img in links_images:
                src = tags_img.get_attribute("src")
                if src:
                    links_de_las_imagenes.append(src)

            print(f"Total de enlaces válidos encontrados: {len(links_de_la_pagina)}")
            return links_de_la_pagina, links_de_las_imagenes
        finally:
            driver.quit()

    def scrapper_urls(query):
        # Obtener tanto los links de productos como de imágenes
        links_productos, links_imagenes = get_products_links(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Crear listas separadas para cada columna
        titulos = []
        seller = []
        precios_antes = []
        descuentos = []
        precios = []
        urls = []
        imagenes = []  # Nueva lista para las imágenes
        
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
                vendido_por_texto = vendido_por.text.strip() if vendido_por else "Sin vendedor"
                descuento_texto = descuento.text.strip() if descuento else "Sin descuento"

                # Agregar datos a las listas
                titulos.append(titulo_texto)    
                seller.append(vendido_por_texto)
                precios.append(precio_texto)
                precios_antes.append(precio_antes_texto)
                descuentos.append(descuento_texto)
                urls.append(link)
                imagenes.append(imagen)  # Agregar la URL de la imagen

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

        # Crear el DataFrame con las listas, incluyendo las imágenes
        df = pd.DataFrame({
            'Nombre_del_producto': titulos,
            'Vendedor': seller,
            'Precio_antes': precios_antes,
            'Descuento': descuentos,
            'Precio': precios,
            'URL': urls,
            'Imagen_URL': imagenes,  # Nueva columna para las imágenes
        })
        
        return df

    # Interfaz de Streamlit
    st.title("Productos de Fravega")
    query = st.text_input("Ingrese el producto a buscar:")

    if query:  # Solo ejecutar si hay texto ingresado
        # Usar session_state para almacenar el DataFrame
        if 'df' not in st.session_state or st.session_state.last_query != query:
            st.session_state.df = scrapper_urls(query)
            st.session_state.last_query = query
        
        df = st.session_state.df
        st.dataframe(df, use_container_width=True)

        # Guardar en CSV
        csv_buffer = BytesIO()
        df.to_excel(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(
            label=" 💾 Descargar XLSX", 
            data=csv_buffer, 
            file_name="productos_fravega.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Mostrar las imágenes
        st.subheader("Imágenes de los productos")
        cols = st.columns(4)  # Crear 3 columnas para mostrar las imágenes
        
        for idx, (imagen_url, titulo) in enumerate(zip(df['Imagen_URL'], df['Nombre_del_producto'])):
            with cols[idx % 4]:  # Distribuir las imágenes en las columnas
                try:
                    st.image(imagen_url, caption=titulo)
                except Exception as e:
                    st.error(f"Error al cargar la imagen: {str(e)}")
        
        # Guardar en Excel
        #df.to_excel('productos_fravega.xlsx', index=False)
        st.success("¡Búsqueda completada! Los resultados se han guardado en 'productos_fravega.xlsx'")
