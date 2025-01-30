import streamlit as st
import fravega
import info
import prueba_paginacion

st.set_page_config(page_title="Abyss Dirver v1.0", page_icon=":shopping_cart:", layout="wide")

def main():
    st.sidebar.title("Abyss Dirver v1.0", help="Abyss Dirver v1.0 es una app que permite buscar productos en E-Commerces, descargar su información en formato Excel y mostrar las imágenes de los productos.")
    paginas = st.sidebar.selectbox("Selecciona una página", ["Seleccionar", "prueba", "Fravega", "Musimundo"])
    #Seleccionar
    if paginas == "Seleccionar":
        info.info()
    #Fravega
    elif paginas == "Fravega":
        fravega.fravega()
    elif paginas == "prueba":
        prueba_paginacion.prueba()

if __name__ == "__main__":
    main()
