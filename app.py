
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Tennis Tracker", layout="wide")
st.title("🎾 Seguimiento de Apuestas de Tenis")

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

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Apuestas totales", total_apuestas)
col2.metric("✅ Aciertos", aciertos_totales)
col3.metric("💸 Unidades ganadas", round(total_unidades, 2))
col4.metric("📈 Yield acumulado", f"{round(100 * yield_total, 2)}%")
col5 = st.columns(5)[4]
col5.metric("📊 Profit Factor", round(profit_factor, 2) if profit_factor != float("inf") else "∞")

# Gráfico
fig = px.bar(resumen, x="semana", y=["unidades", "yield"], barmode="group",
             labels={"value": "Métrica", "variable": "Indicador"}, title="📊 Resultados semanales")
fig.update_layout(xaxis_title="Semana", yaxis_title="Valor")
st.plotly_chart(fig, use_container_width=True)

# Mostrar tabla
st.subheader("📋 Historial de apuestas")
st.dataframe(df_filtrado.drop(columns=["event_id"]).sort_values("fecha", ascending=False), use_container_width=True)
