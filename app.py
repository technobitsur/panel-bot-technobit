import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Panel de Control - Bot TECHNOBIT", page_icon="📱", layout="wide")

# ==========================================
# CONFIGURACIÓN SUPABASE (Usando secrets por seguridad)
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📱 Panel de Monitoreo - Bot TECHNOBIT")

# Función para obtener los mensajes (con caché de 5 segundos para no saturar)
@st.cache_data(ttl=5)
def obtener_mensajes():
    # Traemos los 1000 MÁS NUEVOS de la base de datos general
    respuesta = supabase.table("historial_mensajes").select("*").order("created_at", desc=True).limit(1000).execute()
    return respuesta.data

# Obtenemos los datos
datos = obtener_mensajes()

if not datos:
    st.info("Todavía no hay mensajes registrados. ¡Escribile al bot para probar!")
else:
    df = pd.DataFrame(datos)
    
    # Damos vuelta el DataFrame para que el chat se lea de arriba hacia abajo (cronológico)
    df = df.iloc[::-1]
    
    # Obtener números de teléfono únicos para armar el menú lateral
    numeros_unicos = df["numero_cliente"].unique()
    
    st.sidebar.header("Conversaciones Activas")
    numero_seleccionado = st.sidebar.selectbox("Seleccionar Cliente:", numeros_unicos)
    
    # Control para elegir cuántos mensajes querés ver en pantalla
    limite_mensajes = st.sidebar.slider("Mostrar últimos N mensajes:", min_value=5, max_value=100, value=20)
    
    st.subheader(f"Chat con: {numero_seleccionado}")
    
    # Filtramos solo los mensajes del número que tocaste en el menú
    chat_cliente = df[df["numero_cliente"] == numero_seleccionado]
    
    # Nos quedamos SOLAMENTE con los últimos mensajes (corta los viejos)
    chat_cliente = chat_cliente.tail(limite_mensajes)
    
    # Dibujamos el chat usando la interfaz nativa de Streamlit
    for index, fila in chat_cliente.iterrows():
        if fila["tipo"] == "entrante":
            # Mensaje del cliente
            st.chat_message("user").write(fila["mensaje"])
        else:
            # Mensaje del bot (usando un avatar sofisticado para proyectar mayor confianza)
            st.chat_message("assistant", avatar="🧑‍💻").write(fila["mensaje"])
            
    # Botón manual por si querés forzar la actualización rápido
    if st.sidebar.button("🔄 Actualizar Chat"):
        obtener_mensajes.clear() # Limpia la memoria caché
        st.rerun() # Recarga la pantalla
