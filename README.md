# 🎾 Tennis Tracker App

Esta es una aplicación web construida con [Streamlit](https://streamlit.io/) que permite visualizar de forma clara y visual el rendimiento semanal de las apuestas de tenis generadas por un modelo de predicción automático.

## 🔍 ¿Qué muestra la app?

- **Profit total** acumulado
- **Yield (%)** semanal y acumulado
- **Porcentaje de acierto**
- **Unidades ganadas por semana**
- Filtros por jugador y rango de semanas
- Tabla detallada de cada pick

## 📅 Datos

Los datos provienen del archivo `tracker_resultados.xlsx`, que se actualiza automáticamente desde el repositorio privado [`tennis-prediction`](https://github.com/andreuroigv/tennis-prediction) con cada ejecución de validación.

## 🌐 Acceso

Puedes acceder a la app desde el siguiente enlace:

👉 **[Abrir la app Streamlit](https://tennis-tracker-app.streamlit.app)**

> Este enlace puede fijarse en tu canal de Telegram para que cualquier usuario consulte el rendimiento en tiempo real.

## 🚀 Tecnologías utilizadas

- Python
- Streamlit
- pandas
- matplotlib
- GitHub Actions (para actualizar los datos automáticamente)

## 📁 Estructura del repositorio

```
tennis-tracker-app/
├── app.py                    # App de Streamlit
├── tracker_resultados.xlsx   # Tracker actualizado automáticamente
├── requirements.txt          # Dependencias
└── README.md
```

## 🧠 Autor

Desarrollado por [Andreu Roig](https://github.com/andreuroigv) con asistencia de ChatGPT.