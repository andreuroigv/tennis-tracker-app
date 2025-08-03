
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

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

# Métricas agregadas por semana
df_filtrado["semana"] = df_filtrado["fecha"].dt.to_period("W").dt.start_time
resumen = df_filtrado.dropna(subset=["profit"]).groupby("semana").agg(
    apuestas=("profit", "count"),
    aciertos=("resultado", lambda x: (x == "Acierto").sum()),
    fallos=("resultado", lambda x: (x == "Fallo").sum()),
    unidades=("profit", "sum")
).reset_index()
resumen["yield"] = resumen["unidades"] / resumen["apuestas"]

# KPIs
total_apuestas = resumen["apuestas"].sum()
total_unidades = resumen["unidades"].sum()
yield_total = total_unidades / total_apuestas if total_apuestas else 0
ganancias = df_filtrado[df_filtrado["profit"] > 0]["profit"].sum()
perdidas = -df_filtrado[df_filtrado["profit"] < 0]["profit"].sum()
profit_factor = ganancias / perdidas if perdidas else float("inf")
aciertos_totales = resumen["aciertos"].sum()
fallos_totales = resumen["fallos"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎯 Apuestas totales", total_apuestas)
col2.metric("✅ Aciertos", aciertos_totales)
col3.metric("💸 Unidades ganadas", round(total_unidades, 2))
col4.metric("📈 Yield acumulado", f"{round(100 * yield_total, 2)}%")
col5.metric("📊 Profit Factor", round(profit_factor, 2) if profit_factor != float("inf") else "∞")

# Gráfico
import plotly.graph_objects as go

# Agrupación por semana
df_filtrado["semana"] = pd.to_datetime(df_filtrado["fecha"]).dt.to_period("W").apply(lambda r: r.start_time)
resumen_semanal = df_filtrado.groupby("semana").agg({
    "profit": "sum",
    "cuota": "count"
}).reset_index()

resumen_semanal["yield"] = resumen_semanal["profit"] / resumen_semanal["cuota"]
resumen_semanal["unidades"] = resumen_semanal["profit"]
resumen_semanal["yield_acumulado"] = resumen_semanal["yield"].cumsum() * 100  # en porcentaje

# Gráfico combinado
fig = go.Figure()

# Unidades ganadas (barras)
fig.add_trace(go.Bar(
    x=resumen_semanal["semana"],
    y=resumen_semanal["unidades"],
    name="Unidades ganadas",
    yaxis="y1"
))

# Yield acumulado (línea)
fig.add_trace(go.Scatter(
    x=resumen_semanal["semana"],
    y=resumen_semanal["yield_acumulado"],
    name="Yield acumulado (%)",
    yaxis="y2",
    mode="lines+markers"
))

# Layout
fig.update_layout(
    title="📈 Evolución semanal",
    xaxis_title="Semana",
    yaxis=dict(
        title="Unidades",
        side="left",
        showgrid=False,
        zeroline=True
    ),
    yaxis2=dict(
        title="Yield acumulado (%)",
        side="right",
        overlaying="y",
        showgrid=False,
        zeroline=True
    ),
    legend=dict(x=0.01, y=0.99),
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
