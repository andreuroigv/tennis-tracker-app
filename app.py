
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Tennis Tracker", layout="wide")
st.title("🎾 Seguimiento de Apuestas de Tenis")

if st.button("🔁 Actualizar datos"):
    st.cache_data.clear()

# Leer datos
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("tracker_resultados.xlsx")
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except:
        st.warning("No se pudo cargar el archivo tracker_resultados.xlsx")
        return pd.DataFrame()

df = cargar_datos()

if df.empty:
    st.stop()

# Filtros
st.sidebar.header("Filtros")
fecha_inicio = st.sidebar.date_input("Desde", value=df["fecha"].min().date())
fecha_fin = st.sidebar.date_input("Hasta", value=df["fecha"].max().date())
jugador = st.sidebar.selectbox("Filtrar por jugador", ["Todos"] + sorted(set(df["jugador_A"]) | set(df["jugador_B"])))

filtro = (df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))
if jugador != "Todos":
    filtro &= (df["jugador_A"] == jugador) | (df["jugador_B"] == jugador)

df_filtrado = df[filtro].copy()

# Excluir apuestas anuladas del análisis
df_filtrado = df_filtrado[df_filtrado["resultado"] != "Anulado"]

# -------------------------
# KPIs
# -------------------------
df_validadas = df_filtrado.dropna(subset=["profit"]).copy()

total_apuestas = df_validadas.shape[0]
total_unidades = df_validadas["profit"].sum()
yield_total = total_unidades / total_apuestas if total_apuestas else 0
ganancias = df_validadas[df_validadas["profit"] > 0]["profit"].sum()
perdidas = -df_validadas[df_validadas["profit"] < 0]["profit"].sum()
profit_factor = ganancias / perdidas if perdidas else float("inf")
aciertos_totales = (df_validadas["resultado"] == "Acierto").sum()
fallos_totales = (df_validadas["resultado"] == "Fallo").sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎯 Apuestas totales", total_apuestas)
col2.metric("✅ Aciertos", aciertos_totales)
col3.metric("💸 Unidades ganadas", round(total_unidades, 2))
col4.metric("📈 Yield", f"{round(100 * yield_total, 2)}%")
col5.metric("📊 Profit Factor", round(profit_factor, 2) if profit_factor != float("inf") else "∞")

# -------------------------
# Tabla mensual con resumen
# -------------------------
df_validadas["mes"] = df_validadas["fecha"].dt.to_period("M").dt.to_timestamp()

resumen_mensual = df_validadas.groupby("mes").agg(
    apuestas=("profit", "count"),
    aciertos=("resultado", lambda x: (x == "Acierto").sum()),
    fallos=("resultado", lambda x: (x == "Fallo").sum()),
    unidades=("profit", "sum")
).reset_index()

# Calcular yield antes de eliminar columnas
resumen_mensual["yield"] = resumen_mensual["unidades"] / resumen_mensual["apuestas"]

# Mapeo manual de meses al español
meses_es = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# Formatear mes como nombre en español
resumen_mensual["Mes"] = resumen_mensual["mes"].dt.strftime("%B").map(meses_es)

# Crear columna de Yield en porcentaje
resumen_mensual["Yield"] = (resumen_mensual["yield"] * 100).round(2).astype(str) + "%"

# Eliminar columna yield numérica y mes original
resumen_mensual = resumen_mensual.drop(columns=["yield", "mes"])

st.subheader("📆 Resumen mensual")
st.dataframe(
    resumen_mensual.rename(columns={
        "Mes": "Mes",
        "apuestas": "Apuestas",
        "aciertos": "Aciertos",
        "fallos": "Fallos",
        "unidades": "Unidades"
    }),
    use_container_width=True
)

# -------------------------
# Gráfico semanal (barras y acumuladas)
# -------------------------
df_validadas["semana"] = df_validadas["fecha"].dt.to_period("W").apply(lambda r: r.start_time)

resumen_semanal = df_validadas.groupby("semana").agg(
    unidades=("profit", "sum")
).reset_index()

resumen_semanal["unidades_acumuladas"] = resumen_semanal["unidades"].cumsum()

fig = go.Figure()

# Barras: unidades por semana
fig.add_trace(go.Bar(
    x=resumen_semanal["semana"],
    y=resumen_semanal["unidades"],
    name="Unidades semanales",
    yaxis="y1"
))

# Línea: unidades acumuladas
fig.add_trace(go.Scatter(
    x=resumen_semanal["semana"],
    y=resumen_semanal["unidades_acumuladas"],
    name="Unidades acumuladas",
    yaxis="y2",
    mode="lines+markers"
))

fig.update_layout(
    title="📈 Evolución semanal de unidades",
    xaxis_title="Semana",
    yaxis=dict(title="Unidades semanales", side="left"),
    yaxis2=dict(title="Unidades acumuladas", overlaying="y", side="right"),
    legend=dict(x=0.01, y=0.99),
    barmode="group",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Tabla de historial detallado
# -------------------------
st.subheader("📋 Historial completo de apuestas")
columnas_a_mostrar = ["fecha", "jugador_A", "jugador_B", "pronostico", "cuota", "resultado", "profit"]
df_ordenado = df_filtrado.sort_values("fecha", ascending=False)[columnas_a_mostrar]
st.dataframe(df_ordenado, use_container_width=True)
