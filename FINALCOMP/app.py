import streamlit as st
import pandas as pd
import numpy as np  
import plotly.express as px

st.title("Puerto Rico Crime Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("https://cdat.uprh.edu/~eramos/data/crime_processed.csv")

df = load_data()

df.columns = ["Fecha",
              "Horario",
              "CrimeCode",
              "Delito",
              "Lat",
              "Lon",
              "Area",
              "Año",
              "Mes",
              "NombreMes",
              "Dia",
              "DiaSemana",
              "NombreDiaSemana",
              "DiaAño",
              "Hora",
              "Min"]

def dameIndice(delito):
  if delito == "Asesinato":
    return 10
  elif delito == "Violacion":
    return 9.5
  elif delito == "Trata Humana":
    return 9
  elif delito == "Incendio Malicioso":
    return 8.5
  elif delito == "Agresion Agravada":
    return 8
  elif delito == "Robo":
    return 7
  elif delito == "Escalamiento":
    return 6
  elif delito == "Vehiculo Hurtado":
    return 5.5
  elif delito == "Apropiacion Ilegal":
    return 5
  else:
    return 4

df["Indice de Gravedad"] = pd.Series(map(dameIndice,df["Delito"]))

def cambia_leng(nombreDiaSemana):
  if nombreDiaSemana == "Monday":
    return "Lunes"
  elif nombreDiaSemana == "Tuesday":
    return "Martes"
  elif nombreDiaSemana == "Wednesday":
    return "Miércoles"
  elif nombreDiaSemana == "Thursday":
    return "Jueves"
  elif nombreDiaSemana == "Friday":
    return "Viernes"
  elif nombreDiaSemana == "Saturday":
    return "Sábado"
  elif nombreDiaSemana == "Sunday":
    return "Domingo"
  
df["NombreDiaSemana"] = pd.Series(map(cambia_leng, df["NombreDiaSemana"]))

df["Periodo"] = df["Hora"].apply(
    lambda x: "AM" if int(x) < 12 else "PM"
)

@st.cache_data
def image():
    return "https://cdat.uprh.edu/~eramos/data/crimeapp_logo.png"

st.sidebar.image(
    image(),
    width=200
)

areas = np.insert(df["Area"].unique(), 0, "Todas las Áreas")

selected_area = st.sidebar.selectbox("Seleccione un área", areas)

if selected_area == "Todas las Áreas":
    selected_area = df["Area"].unique()
else:
    selected_area = [selected_area]

delito = df["Delito"].unique()

selected_delitos = st.sidebar.multiselect("Seleccione delitos", delito, default=delito)

dias = df["NombreDiaSemana"].unique()
selected_dias = st.sidebar.multiselect(
    "Seleccione Dias",
    dias,
    default=dias
)

selected_period = st.sidebar.selectbox(
    "AM / PM",
    ["AM", "PM","Ambos"]
)

if selected_period == "Ambos":
    selected_period = ["AM", "PM"]
else:
    selected_period = [selected_period]

filtered_df = df[
    (df["Area"].isin(selected_area)) &
    (df["Delito"].isin(selected_delitos)) &
    (df["NombreDiaSemana"].isin(selected_dias)) &
    (df["Periodo"].isin(selected_period))
]

st.dataframe(filtered_df.head())
st.dataframe(filtered_df.tail())


total_incidents = len(filtered_df)

most_common_crime = (
    filtered_df["Delito"]
    .value_counts()
    .idxmax()
)

most_common_area = (
    filtered_df["Area"]
    .value_counts()
    .idxmax() 
)

st.metric("Cantidad de Incidentes", total_incidents)
st.metric("Delito más frecuente", most_common_crime)
st.metric("Área con más incidentes", most_common_area)

fig = px.histogram(
    filtered_df,
    x="Delito",
    category_orders={
      "Delito": filtered_df["Delito"].value_counts().index.tolist()
    },
    title="Histograma de Delitos"
)

st.plotly_chart(fig)

#######TEST######
st.write()
#######TEST######


if str(selected_area) != "Todas las Áreas":
    centro_zoom = dict(lat=filtered_df["Lat"].mean(), lon=filtered_df["Lon"].mean())
else:
    centro_zoom = dict(lat=18.25178,lon=-66.254513)

mapa_puntos = px.scatter_map(filtered_df,
                             lat="Lat",
                             lon="Lon",
                             color="Indice de Gravedad",
                             size="Indice de Gravedad",
                             size_max=5,
                             opacity=0.5,
                             height=800,
                             zoom=8.9,
                             color_continuous_scale=px.colors.sequential.Hot_r,
                             map_style="carto-darkmatter-nolabels",
                             center=centro_zoom
                             )


st.plotly_chart(mapa_puntos)

st.sidebar.markdown("""
Aplicación desarrollada por:

Ediel J. Ramos De Jesús

Proyecto Final Comp3082 – Mayo 2026

Ciencia de Datos

Universidad de Puerto Rico en Humacao
""")