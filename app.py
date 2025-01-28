import streamlit as st
import cv2
import numpy as np
import mahotas
from PIL import Image

html_content = """
<div style="width: 100%; clear: both; display: flex; align-items: center; justify-content: space-between;">
    <div style="width: 50%; display: flex; justify-content: flex-start;">
        <img src="https://www.ucc.edu.co/institucional/acerca-de-la-universidad/Documents/logo_ucc_2018(CURVAS)-01.png" style="width: 100%; max-width: 00px; height: auto;">
    </div>
    <div style="width: 50%; text-align: right; padding-left: 0px;">
        <p style="margin: 0px; font-weight: bold;">Laboratorio de Tecnologías Emergentes</p>
        <p style="margin: 0px;">Universidad Cooperativa de Colombia, Campus Ibagué-Espinal</p>
        <p style="margin: 0px;">Facultad de Ingeniería</p>
        <p style="margin: 0px;">Programa de Ingeniería de Sistemas</p>
        <p style="margin: 0px;">2025</p>
    </div>
</div>
"""



def contar_colonias(imagen):
    """
    Cuenta y clasifica colonias bacterianas en una imagen, incluyendo variantes de azul y rojo.
    """
    # Convertir a espacio de color HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir rangos de colores ampliados
    lower_blue1 = np.array([90, 50, 50])
    upper_blue1 = np.array([100, 255, 255])
    lower_blue2 = np.array([101, 50, 50])
    upper_blue2 = np.array([130, 255, 255])
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([179, 255, 255])

    # Crear máscaras
    mask_blue = cv2.add(cv2.inRange(hsv, lower_blue1, upper_blue1), cv2.inRange(hsv, lower_blue2, upper_blue2))
    mask_red = cv2.add(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))

    # Operaciones morfológicas para limpiar ruido
    kernel = np.ones((3, 3), np.uint8)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

    # Detectar contornos
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Crear copia de la imagen para resaltar resultados
    imagen_resaltada = imagen.copy()

    for contour in contours_blue:
        if cv2.contourArea(contour) > 0.0001:
            cv2.drawContours(imagen_resaltada, [contour], -1, (255, 0, 0), 2)  # Azul

    for contour in contours_red:
        if cv2.contourArea(contour) > 0.0001:
            cv2.drawContours(imagen_resaltada, [contour], -1, (0, 0, 255), 2)  # Rojo

    # Contar colonias detectadas
    num_colonias_azules = len([c for c in contours_blue if cv2.contourArea(c) > 0.0001])
    num_colonias_rojas = len([c for c in contours_red if cv2.contourArea(c) > 0.0001])

    return num_colonias_azules, num_colonias_rojas, imagen_resaltada

# Configuración de la página
st.set_page_config(page_title="Contador de Colonias Bacterianas", layout="wide")

# Descripción del proyecto
st.markdown(html_content, unsafe_allow_html=True)
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
st.title("Contador de Colonias Bacterianas en Agua")
st.markdown("""
Esta aplicación permite contar colonias bacterianas presentes en el agua para consumo humano, utilizando visión por computadora. 
El análisis está basado en la detección de colores específicos (azul y rojo), que corresponden a distintos tipos de bacterias en cultivos microbiológicos.
Sube una imagen para procesarla y obtener un conteo visual de las colonias detectadas.

**Investigadores:**
- Oscar Augusto Diaz Triana
- Fernando Gutierrez Portela
- Oscar Efren Ospina
""")

# Recomendaciones sobre la imagen
st.subheader("Recomendaciones para la Imagen")
st.markdown("""
- Asegúrate de que la imagen esté bien iluminada y enfocada. Esto es fundamental para mejorar la precisión del conteo.
- Las imágenes con alto contraste entre las colonias bacterianas y el fondo tienen mejores resultados.
- Evita imágenes borrosas o con resolución muy baja, ya que pueden dificultar la identificación de las colonias.
- El contenedor donde se encuentran las bacterias debe ser visible claramente, sin distorsiones en la imagen.
""")

# Ejemplo de imagen de muestra
st.subheader("Ejemplo de Imagen de Muestra")
st.markdown("""
A continuación, se presenta un ejemplo de imagen que debe ser subida. Esta imagen muestra un contenedor donde se están estudiando las bacterias.
""")
#st.image("prueba_2_1.jpeg", caption="Imagen de ejemplo: Imagen de Prueba", width=100, use_container_width=True)



# Subir imagen
imagen_subida = st.file_uploader("Sube una imagen de las colonias bacterianas", type=["jpg", "jpeg", "png"])

if imagen_subida is not None:
    # Leer imagen
    imagen = Image.open(imagen_subida)
    imagen = np.array(imagen)
    imagen_bgr = cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR)

    # Procesar imagen
    num_colonias_azules, num_colonias_rojas, imagen_resaltada = contar_colonias(imagen_bgr)

    # Mostrar resultados
    col1, col2 = st.columns(2)
    with col1:
        st.header("Imagen Original")
        st.image(imagen, caption="Imagen original cargada", use_container_width=True)
    with col2:
        st.header("Colonias Detectadas")
        st.image(cv2.cvtColor(imagen_resaltada, cv2.COLOR_BGR2RGB), caption="Colonias resaltadas", use_container_width=True)

    # Mostrar conteo
    st.subheader("Resultados del Conteo")
    st.markdown(f"**Colonias Azules (y variantes):** {num_colonias_azules}")
    st.markdown(f"**Colonias Rojas (y variantes):** {num_colonias_rojas}")

st.info("Nota: Asegúrate de que las imágenes estén bien iluminadas y enfocadas para obtener mejores resultados.")

st.markdown("""
<hr>
<p style="text-align: center; font-size: 14px;">
    Universidad Cooperativa de Colombia - Campus Ibagué-Espinal <br>
    Facultad de Ingeniería 2025
</p>
""", unsafe_allow_html=True)
