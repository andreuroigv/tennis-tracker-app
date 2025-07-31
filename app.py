
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Tracker de Apuestas de Tenis", layout="wide")

st.title("🎾 Tracker de Apuestas de Tenis")
st.markdown("Visualización semanal de rendimiento")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("tracker_resultados.xlsx")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Semana"] = df["Fecha"].dt.to_period("W").apply(lambda r: r.start_time)
    return df

df = cargar_datos()

# Filtros
jugadores = sorted(set(df["Partido"].str.split(" vs ").explode()))
jugador = st.sidebar.selectbox("Filtrar por jugador", ["Todos"] + jugadores)
semanas = df["Semana"].drop_duplicates().sort_values()
semana_ini, semana_fin = st.sidebar.select_slider(
    "Selecciona rango de semanas",
    options=semanas,
    value=(semanas.min(), semanas.max())
)

df_filtrado = df[(df["Semana"] >= semana_ini) & (df["Semana"] <= semana_fin)]
if jugador != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Partido"].str.contains(jugador)]

# KPIs
total_picks = len(df_filtrado)
aciertos = df_filtrado[df_filtrado["Resultado"] == "Acierto"].shape[0]
fallo = df_filtrado[df_filtrado["Resultado"] == "Fallo"].shape[0]
profit_total = df_filtrado["Profit"].sum()
yield_total = profit_total / total_picks * 100 if total_picks > 0 else 0
tasa_acierto = aciertos / total_picks * 100 if total_picks > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Total de picks", total_picks)
col2.metric("✅ % de acierto", f"{tasa_acierto:.1f}%")
col3.metric("💵 Profit total", f"{profit_total:.2f} unidades")
col4.metric("📈 Yield acumulado", f"{yield_total:.2f}%")

# Tabla
st.subheader("📋 Detalle de picks")
st.dataframe(df_filtrado.sort_values("Fecha", ascending=False), use_container_width=True)

# Gráficos
st.subheader("📊 Evolución semanal")

resumen = df_filtrado.groupby("Semana").agg({
    "Profit": "sum"
}).rename(columns={"Profit": "Unidades ganadas"})

resumen["Yield semanal (%)"] = (
    df_filtrado.groupby("Semana")["Profit"].sum() / 
    df_filtrado.groupby("Semana").size()
) * 100

fig, ax1 = plt.subplots(figsize=(10, 5))

color1 = "tab:blue"
ax1.set_xlabel("Semana")
ax1.set_ylabel("Unidades ganadas", color=color1)
ax1.bar(resumen.index, resumen["Unidades ganadas"], color=color1, alpha=0.6)
ax1.tick_params(axis="y", labelcolor=color1)

ax2 = ax1.twinx()
color2 = "tab:green"
ax2.set_ylabel("Yield semanal (%)", color=color2)
ax2.plot(resumen.index, resumen["Yield semanal (%)"], color=color2, marker="o")
ax2.tick_params(axis="y", labelcolor=color2)

fig.tight_layout()
st.pyplot(fig)
