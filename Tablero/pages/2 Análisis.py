from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import pandas as pd
import wbgapi as wb
import yfinance as yf
import numpy as np
# import folium
from streamlit_folium import folium_static
from datetime import datetime
import re
import nltk
import plotly.graph_objects as go
import plotly.express as px
nltk.download('stopwords')
nltk.download('punkt')


st.markdown("<h1 style='text-align: center; color: orange;'>*¡A n á l i s i s!*</h1>", unsafe_allow_html=True)

#Definimos listas de estados y códigos
state_codes = {'Alabama': 'AL','Alaska': 'AK','Arizona': 'AZ','Arkansas': 'AR','California': 'CA','Colorado': 'CO','Connecticut': 'CT',
    'Delaware': 'DE','Florida': 'FL','Georgia': 'GA','Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL','Indiana': 'IN','Iowa': 'IA',
    'Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA','Maine': 'ME','Maryland': 'MD','Massachusetts': 'MA','Michigan': 'MI',
    'Minnesota': 'MN','Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT','Nebraska': 'NE','Nevada': 'NV','New_Hampshire': 'NH',
    'New_Jersey': 'NJ','New_Mexico': 'NM','New_York': 'NY','North_Carolina': 'NC','North_Dakota': 'ND','Ohio': 'OH','Oklahoma': 'OK',
    'Oregon': 'OR','Pennsylvania': 'PA','Rhode_Island': 'RI','South_Carolina': 'SC','South_Dakota': 'SD','Tennessee': 'TN','Texas': 'TX',
    'Utah': 'UT','Vermont': 'VT','Virginia': 'VA','Washington': 'WA','West_Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY'}

estados = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia',
           'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan',
           'Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New_Hampshire','New_Jersey','New_Mexico','New_York',
           'North_Carolina','North_Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode_Island','South_Carolina','South_Dakota',
           'Tennessee', 'Texas', 'Utah','Vermont', 'Virginia', 'Washington', 'West_Virginia', 'Wisconsin', 'Wyoming', 'Todos']

#Importamos los DF a utilizar. Cuidar que no se excedan de 200 MB porque es el límite de Streamlit
reviews= pd.read_csv('C:/Users/Manuel/Documents/Henry/PG_Google_Yelp/Normalizacion/reviews_filtro.csv',sep=';',escapechar='\\')
restaurants = pd.read_csv('C:/Users/Manuel/Documents/Henry/PG_Google_Yelp/Normalizacion/restaurants_homolog.csv', index_col=0)


#---------------------- Inicio del código para el proceso de filtrado de los DF ----------------------------------
#Funciones de filtro para el DF de restaurantes
@st.cache_data
def filtro_restaurante_estado(data, edo):
    if edo != "Todos":
        data = data[data['Estado'] == edo]
    return data

@st.cache_data
def filtro_restaurante_tipo(data,tipo):
    if tipo != "Todos":
        data = data[data['Tipo'] == tipo]
    return data

@st.cache_data
def filtro_restaurante_nombre(data,nombre):
    if nombre != "Todos":
        data = data[data['Nombre'] == nombre]
    return data

@st.cache_data
def filtro_restaurante_ciudad(data,nombre):
    if nombre != "Todos":
        data = data[data['Ciudad'] == nombre]
    return data

@st.cache_data
def filtro_restaurante_id(data,nombre):
    if nombre != "Todos":
        data = data[data['Id_Restaurant'] == nombre]
    return data

# Definimos los filtros por Estado, por Tipo de Comida y por Restaurante
estado = st.sidebar.selectbox("Seleccione el estado del que está buscando información", estados)
estado_cod = state_codes.get(estado, "Todos")
restaurants_fe = filtro_restaurante_estado(restaurants, estado_cod)

kind_food = np.concatenate((restaurants_fe["Tipo"].unique(),["Todos"]))
slide_tipo= st.sidebar.selectbox("Seleccione el tipo de comida de su interés", kind_food)
restaurants_ft = filtro_restaurante_tipo(restaurants_fe, slide_tipo)

restaur = np.concatenate((["Todos"],restaurants_ft["Nombre"].unique()))
slide_restaurant = st.sidebar.selectbox("Seleccione el nombre del restaurante de su interés", restaur)
restaurants_fn = filtro_restaurante_nombre(restaurants_ft, slide_restaurant)

# restaurants_fn  # línea de control para ver el DF antes de aplicar filtro por colonia y sucursal(id)

restaurant_por_ciudad = np.concatenate((["Todos"],restaurants_fn["Ciudad"].unique()))
slide_ciudad = st.sidebar.selectbox("Seleccione el nombre de la Ciudad", restaurant_por_ciudad)
restaurants_fc = filtro_restaurante_ciudad(restaurants_fn, slide_ciudad)

restaurant_por_sucursal = np.concatenate((["Todos"],restaurants_fc["Id_Restaurant"].unique()))
slide_sucursal = st.sidebar.selectbox("Seleccione el Id del Restaurante", restaurant_por_sucursal)
restaurants_fs = filtro_restaurante_id(restaurants_fc, slide_sucursal)


# restaurants_fs #línea de control para ver como queda el DF con el if anterior para filtrar por colonia y sucursal


#---------------------- Fin del código para el proceso de filtrado de los DF---------------------------------------

# Hasta esta línea tendriamos los DF filtrados: 
# st.dataframe(restaurants_fs) 
# st.dataframe(resenias) 

#----------------------------------------- Inicio Mapa de ubicaciones -----------------------------------------
st.markdown("<h3 style='text-align: center; color: orange;'>¡Mapa de distribución!</h3>", unsafe_allow_html=True)

#** Este bloque muestra un mapa de ubicaciones, es interesante, pero se satura mucho por la cantidad de restaurantes.
# Crear un mapa centrado en las coordenadas del primer restaurante
# m = folium.Map(location=[restaurants_fs.iloc[0]['Latitud'], restaurants_fs.iloc[0]['Longitud']], zoom_start=12)
# # Agregar un marcador para cada restaurante
# for i, row in restaurants_fs.iterrows():
#     folium.Marker([row['Latitud'], row['Longitud']], popup=row['Nombre']).add_to(m)
# folium_static(m) # Mostrar el mapa en Streamlit

df_map = restaurants_fs.loc[:, ['Latitud', 'Longitud']]
df_map = df_map.rename(columns={'Latitud': 'LAT', 'Longitud': 'LON'})
st.map(df_map)


f"Se encontraron {restaurants_fe.shape[0]} restaurantes en {estado}" #línea de control para ver el filtrado
f"Se encontraron {restaurants_ft.shape[0]} restaurantes de {slide_tipo}" #línea de control para ver el filtrado
f"Sucursales del restaurante {slide_restaurant}: {restaurants_fs.shape[0]}" #línea de control para ver el filtrado

# f"La fecha de inicio es {filtro_fecha[0]}, formato {type(filtro_fecha[0])}" # control para comprobar los datos
# f"La fecha de inicio es {filtro_fecha[1]}, formato {type(filtro_fecha[1])}" # control para comprobar los datos

# f"año{anio_inicio}, tipo {type(anio_inicio)}" Línea de control para conocer el formato de la fecha 

#----------------------------------------- Fin Mapa de ubicaciones -----------------------------------------


#-----------------------------------------Inicio Análisis de Reseñas-----------------------------------------------
st.markdown("<h2 style='text-align: center; color: orange;'>Reseñas</h2>", unsafe_allow_html=True)
# -------Filtro del DF--------

#Para el DF de reseñas, solo se puede filtrar por periodo de tiempo
reviews["Timestamp"] = pd.to_datetime(reviews["Timestamp"]) #Se pone a formato fecha
fecha1=pd.to_datetime(reviews['Timestamp'].min()) #Definimos la fecha menor
fecha2=pd.to_datetime(reviews['Timestamp'].max()) #Definimos la fecha mayor
# Gráfico del filtro de fecha
filtro_fecha = st.slider("Selecciones periodo a revisar", value=(datetime(fecha1.year, fecha1.month,fecha1.day),datetime(fecha2.year, fecha2.month,fecha2.day)))

# Aplicación del Filtro sobre el DF (creación de nueva variable)
resenias = reviews[(reviews["Timestamp"] >= filtro_fecha[0]) & (reviews["Timestamp"] <= filtro_fecha[1])]

anio_inicio = filtro_fecha[0].strftime("%Y")
mes_inicio = filtro_fecha[0].strftime("%m")
dia_inicio = filtro_fecha[0].strftime("%d")
anio_fin = filtro_fecha[1].strftime("%Y")
mes_fin = filtro_fecha[1].strftime("%m")
dia_fin = filtro_fecha[1].strftime("%d")
periodo = f"del {anio_inicio}-{mes_inicio}-{dia_inicio} al {anio_fin}-{mes_fin}-{dia_fin}"
# periodo # línea de control para ver el texto del periodo para los gráficos


# Creamos la función que filtrará las reseñas que tienen que ver con los DF filtrados previamente
# Aquí iría el código de SQL server para definir el nuevo DF

reviews_filtradas = resenias.merge(restaurants_fs[["Id_Restaurant","Nombre","Tipo","Estado","Ciudad"]],on="Id_Restaurant", how="inner")

# reviews_filtradas línea de control para revisar el filtro

#--------- Proceso de reseñas ----------
stopwords = nltk.corpus.stopwords.words('english')

#Le agregamos algunos adjetivos que no nos van a brindar informacion alguna (se puede ir actualizando)
agregar_a_sw = ['good','bad','awesome','awfull','love','like','well','ok','get','back','never','one','two','three',
                'four','five','go','would','got','said','us','came','ask','told','went','better','worst','always']
for p in agregar_a_sw:
    stopwords.append(p)

#Definimos funcion con todas las operaciones a realizar para cualquier valor de rating
@st.cache_data
def procesamientoResenas (dataframe,rating:int):
    df = dataframe[dataframe['Rating']==rating]
    df.reset_index(inplace=True,drop=True)
    reseñas_procesadas = []
    for i in range(df.shape[0]):
        texto1 = re.sub("[^a-zA-Z]"," ",str(df['Reseña'].values[i]))
        texto2 = nltk.tokenize.word_tokenize(texto1.lower())
        lista = [word for word in texto2 if word not in stopwords]
        reseñas_procesadas += lista
    frec_palabras = nltk.FreqDist(reseñas_procesadas)
    frec_palabras_df = pd.DataFrame(list(frec_palabras.items()), columns = ["Palabra","Frequencia"])
    return frec_palabras_df.sort_values(by='Frequencia',ascending=False)

#-------- Definimos tablas de reseñas---------------
#Hacemos una copia del DF de reseñas filtradas, pero solo extraemos las columnas que interesan para el proceso
reseniasypuntaje= reviews_filtradas[["Rating","Reseña"]].copy()

#Aplicamos la función para obtener reseñas positivas con 5 puntos
res_positivas = procesamientoResenas(reseniasypuntaje,5)
tot_res_pos=res_positivas['Frequencia'].sum() #Identificamos cuántas son

#Aplicamos la función para obtener reseñas negativas con 1, 2 y 3 puntos. 
res_negativas1 = procesamientoResenas(reseniasypuntaje,1)
res_negativas2 = procesamientoResenas(reseniasypuntaje,2)
res_negativas3 = procesamientoResenas(reseniasypuntaje,3)
res_negativas = pd.concat([res_negativas1,res_negativas2,res_negativas3], axis=0, ignore_index=True)
tot_res_neg = res_negativas1['Frequencia'].sum() + res_negativas2['Frequencia'].sum() + res_negativas3['Frequencia'].sum()

#Condicionamos el KPI si no tiene reseñas positivas o negativas, enviar un mensaje. Ya que división entre cero no es posible.
if tot_res_pos == 0 and tot_res_neg ==0:    
    st.warning(f"El restaurante: '{slide_restaurant}'; en el Estado de {estado}, no cuenta con reseñas para evaluar.", icon="ℹ️")
elif tot_res_neg == 0:
    st.warning(f"El restaurante: '{slide_restaurant}'; en el Estado de {estado}, no cuenta con reseñas negativas. Todas son positivas ¡F e l i c i d a d e s!.")
else: #Si hay datos, se procede a elaborar el gráfico para el indicador.
    fig_kpi1 = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = tot_res_pos / tot_res_neg,
        domain = {'x': [1, 0], 'y': [1, 0]},
        title = {'text': f"Indice de Reseñas Positivas <br> {periodo}", 'font': {'size': 24,'color':"orange"}},
        delta = {'reference': 1.5, 'increasing': {'color': "orange"}},
        gauge = {
            'axis': {'range': [None, 3], 'tickwidth': 1, 'tickcolor': "orange"},
            'bar': {'color': "orange"},
            'bgcolor': "yellow",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 1], 'color': '#FD5752'},
                {'range': [1, 1.5], 'color': '#FAFD52'},
                {'range': [1.5, 3], 'color': '#ABD758'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.5}}))
    fig_kpi1.update_layout(width = 420, height = 320, font = {'family': "Arial"})
    col1, col2, col3, col4, col5 = st.columns(5) #Se utiliza este línea para acomodar al centro el gráfico al disminuirlo de tamaño
    with col2:        
        st.plotly_chart(fig_kpi1, config={"displayModeBar": False, "responsive": True})

#*******************Dashboard Reseñas


# f"Cantidad de registros sin filtrar: {resenias.shape[0]}" #Línea de control para ver las reseñas sin filtro
# f"Cantidad de registros filtrados por tipo y estado: {reviews_filtradas.shape[0]}" #Línea de control para ver las reseñas con filtro
# f"Estado de Código: {estado_cod}, tipo: {type(estado_cod)}" #Línea de control para ver el códgio del Estado que esta seleccionado
# st.dataframe(reviews_filtradas) #Prueba para ver el DF reseñas que se carga (este se puede eliminar del dashboard)
# f"Reseñas positivas totales 5: {tot_res_pos}" #Línea de control
# f"Reseñas negativas totales 1: {res_negativas1['Frequencia'].sum()}" #Línea de control
# f"Reseñas negativas totales 2: {res_negativas2['Frequencia'].sum()}" #Línea de control
# f"Reseñas negativas totales3: {res_negativas3['Frequencia'].sum()}" #Línea de control
# f"Total reseñas negativas 1,2,3: {tot_res_neg}" #Línea de control

col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"Reseñas negativas: {res_negativas.head(5)['Frequencia'].sum()}")
    st.dataframe(res_negativas.head(5)) #Se muestra sólo las 5 reseñas con más elementos negativos            
with col3:
    st.write(f"Reseñas positivas: {res_positivas.head(5)['Frequencia'].sum()}")
    st.dataframe(res_positivas.head(5)) #Se muestra sólo las 5 reseñas con más elementos positivos


col1,col2,col3 = st.columns(3)
with col1:
    if st.button('Ver reseñas negativas'):
        info_res_neg1= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2])) & (reseniasypuntaje['Reseña'].str.contains(res_negativas["Palabra"][0]))]
        info_res_neg2= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2])) & (reseniasypuntaje['Reseña'].str.contains(res_negativas["Palabra"][1]))]
        info_res_neg3= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2])) & (reseniasypuntaje['Reseña'].str.contains(res_negativas["Palabra"][2]))]
        info_res_neg4= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2])) & (reseniasypuntaje['Reseña'].str.contains(res_negativas["Palabra"][3]))]
        info_res_neg5= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2])) & (reseniasypuntaje['Reseña'].str.contains(res_negativas["Palabra"][4]))]
        informe_negativo = pd.concat([info_res_neg1["Reseña"],info_res_neg2["Reseña"],info_res_neg3["Reseña"],info_res_neg4["Reseña"],info_res_neg5["Reseña"]])
        #Borrar duplicado

        informe_negativo2= reseniasypuntaje.loc[(reseniasypuntaje['Rating'].isin([1, 2,3]))]
        informe_negativo2
with col3:
    if st.button('Ver reseñas positivas'):
        # info_res_pos1 = reseniasypuntaje[(reseniasypuntaje['Reseña'].str.contains(res_positivas["Palabra"][0])) & (reseniasypuntaje['Rating'] == 5)]
        # info_res_pos2 = reseniasypuntaje[(reseniasypuntaje['Reseña'].str.contains(res_positivas["Palabra"][1])) & (reseniasypuntaje['Rating'] == 5)]
        # info_res_pos3 = reseniasypuntaje[(reseniasypuntaje['Reseña'].str.contains(res_positivas["Palabra"][2])) & (reseniasypuntaje['Rating'] == 5)]
        # info_res_pos4 = reseniasypuntaje[(reseniasypuntaje['Reseña'].str.contains(res_positivas["Palabra"][3])) & (reseniasypuntaje['Rating'] == 5)]
        # info_res_pos5 = reseniasypuntaje[(reseniasypuntaje['Reseña'].str.contains(res_positivas["Palabra"][4])) & (reseniasypuntaje['Rating'] == 5)]
        # informe_positivo = pd.concat([info_res_pos1["Reseña"],info_res_pos2["Reseña"],info_res_pos3["Reseña"],info_res_pos4["Reseña"],info_res_pos5["Reseña"]],axis=0,ignore_index=True)
        informe_positivo2 = reseniasypuntaje[(reseniasypuntaje['Rating'] == 5)]
        informe_positivo2
        #informe_positivo

#-----------------------------------------Fin Análisis de Reseñas-----------------------------------------------




#-----------------------------------------Inicio Análisis de Puntuaciones-----------------------------------------------
st.markdown("<h2 style='text-align: center; color: orange;'>Puntuaciones</h2>", unsafe_allow_html=True)
rating = reviews_filtradas.copy() #Generamos una copia para no afectar los demás DF
rating

if rating.empty:    
    st.warning('No existen puntuaciones para los filtros seleccionados.', icon="ℹ️")    
else:
    df_rating = rating.groupby('Rating')["Id_Usuario"].nunique()
    positivo = 0
    negativo = 0
    for i in df_rating.index:
        if i == 5:
            positivo = df_rating[i]
        elif i == 3 or i== 2 or i == 1:
            negativo += df_rating[i]

    promotores = round(positivo / df_rating.sum() * 100,2) #porcentaje de promotores
    detractores = round(negativo / df_rating.sum() * 100,2) #porcentaje de detractores
    nps = promotores - detractores
    
    #Graficamos el resultado. Nota: HAY QUE REVISAR SI SE REQUIERE CONDICIONAR EL GRÁFICO.
    fig_kpi2 = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = nps,
        domain = {'x': [1, 0], 'y': [1, 0]},
        title = {'text': "Porcentaje Red de Promotores", 'font': {'size': 24, 'color':"orange"}},
        delta = {'reference': 30, 'increasing': {'color': "orange"}},
        gauge = {
            'axis': {'range': [-100, 100], 'tickwidth': 3, 'tickcolor': "orange"},
            'bar': {'color': "orange"},
            'bgcolor': "yellow",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-100, 0], 'color': '#FD5752'},
                {'range': [0, 30], 'color': '#FAFD52'},
                {'range': [30, 100], 'color': '#ABD758'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 30}},
        number = {'suffix': '%'}))
    fig_kpi2.update_layout(width = 420, height = 320, font = {'family': "Arial"})
    
#---Gráfico de líneas para presentar el comportamiento de las reseñas a través del tiempo
    gr_res_tiempo = rating[["Rating","Timestamp"]] #Seleccionamos solo las columnas que nos interesan
    gr_res_tiempo["Timestamp"]= pd.to_datetime(gr_res_tiempo["Timestamp"]) #Cambiamos el formato de fecha
    gr_res_tiempo = gr_res_tiempo.sort_values("Timestamp") #Ordenamos de manera ascendente
    gr_res_tiempo = gr_res_tiempo.groupby(pd.Grouper(key='Timestamp', freq='M'))["Rating"].mean().reset_index() #agrupamos promedio puntaje por mes
    
#---Definir diccionario de correspondencia
    meses_ingles = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    meses_espanol = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    correspondencia_meses = dict(zip(meses_ingles, meses_espanol))
    gr_res_tiempo["Mes"] = gr_res_tiempo["Timestamp"].dt.strftime("%B") # Definimos que sea por mes
    gr_res_tiempo["Mes"] = gr_res_tiempo["Mes"].map(correspondencia_meses) #Cambiamos el idioma del mes
    fig_res = px.line(gr_res_tiempo, x="Mes", y="Rating")
#---Línea para dar formato a la gráfica.
    fig_res.update_layout(
    title={
        'text': f"Promedio de puntuaciones <br> {periodo}",
        'x':0.5, # Centrar el título
        'xanchor': 'center' # Centrar el título
            }, #'font': {'color': 'gray'}},
       
    xaxis_title="Mes",
    yaxis_title="Puntuación",
    font=dict(
        family="Arial",
        size=20,
        color="black"),
    plot_bgcolor='rgba(0,0,0,0)',width = 350, height=300)
#Para poner subtitulo
    # fig_res.add_annotation(  
    # text=f"Periodo del {}",
    # xref="paper",
    # yref="paper",
    # x=0,
    # y=1.08,
    # showarrow=False,
    # font=dict(family="Arial", size=14, color="white"))
    fig_res.update_traces(line_color='orange')
    
#---Gráfico de barras para mostrar la distribución
    gr_puntuaciones = rating.groupby("Rating").size().reset_index(name='counts')    
    gr_puntuaciones = gr_puntuaciones.sort_values(by='Rating', ascending=False) # Ordenar los valores de mayor a menor
    fig_bar_puntuaciones = px.bar(gr_puntuaciones, x="counts", y="Rating", orientation='h', color_discrete_sequence=['#FFA500'])     # Crear el gráfico de barras
    fig_bar_puntuaciones.update_layout( # Establecer el título y los títulos de los ejes
        title={
            'text': "Cantidad de puntuaciones por valor",
            #'font': {'color': 'white'} ,
            'x':0.5, # Centrar el título
            'xanchor': 'center' # Centrar el título
            },
        xaxis_title="Cantidad de puntuaciones",
        yaxis_title="Valor de puntuación",
        font=dict(family="Arial", size=20, color="white"),
        plot_bgcolor='rgba(0,0,0,0)', width = 300, height=350)

#********** Dashboard Puntuaciones
    
    # st.dataframe(rating) #Línea de control para identificar el DF filtrado
    # f"Porcentaje de promotores: {promotores}" #Línea de control
    # f"Porcentaje de detractores: {detractores}" #Línea de control
    # f"NPS es de {nps}" #Línea de control
    col1, col2, col3, col4, col5 = st.columns(5) #Se utiliza este línea para acomodar al centro el gráfico al disminuirlo de tamaño
    with col2:        
        st.plotly_chart(fig_kpi2, config={"displayModeBar": False, "responsive": True})

    col1, col2, col3 = st.columns(3)
    with col1:
        # st.markdown(f"<h6 style='text-align: center;'>Promedio mensual de puntuaciones <br> {periodo}</h6>", unsafe_allow_html=True)
        st.plotly_chart(fig_res) #Se muestra sólo las 5 reseñas con más elementos negativos            
    with col3:
        #st.write(f"Reseñas positivas: {res_positivas.head(5)['Frequencia'].sum()}")
        st.plotly_chart(fig_bar_puntuaciones) #Se muestra sólo las 5 reseñas con más elementos positivos    

#---------------------------------------------Fin Análisis de Puntuaciones-----------------------------------------------


#---------------------------------------------Inicio Análisis de Atributos------------------------------------------
st.markdown("<h2 style='text-align: center; color: orange;'>Atributos</h2>", unsafe_allow_html=True)
# Para el análisis de atributos utilizaremos una copia del DF hasta el filtro de Tipo de comida.
atributos_tipo = restaurants_ft.copy() 
atributos_tipo = atributos_tipo.drop(['Id_Restaurant', 'Nombre', 'Ciudad', 'Estado', 'Cod_postal', 'Latitud','Longitud', 'Tipo','Cant_reviews'], axis=1) #eliminamos columnas dejando los atributos y puntuaciones

#Se va requerir atributos del restaurante específico:
atributos_restaurant = restaurants_fs.copy()
atributos_restaurant = atributos_restaurant.drop(['Id_Restaurant', 'Nombre', 'Ciudad', 'Estado', 'Cod_postal', 'Latitud','Longitud', 'Tipo','Cant_reviews'], axis=1) #eliminamos columnas dejando los atributos y puntuaciones
# atributos_restaurant #Control de atributos filtrados

#Creación de la matriz de correlación
correlacion = atributos_tipo.corr() 
correlacion = correlacion.dropna(axis=1, how="all") #Eliminamos las columnas vacías.
correlacion = correlacion.dropna(how="all") #Eliminamos las filas vacías.

#Creamos la tabla de top 6 (3 más positivas y 3 más negativas.)

corr_puntaje = correlacion["Rating_promedio"].sort_values(ascending=False)
top_3_positive = corr_puntaje.nlargest(4)[1:] # El primer valor será el de Rating consigo mismo, lo eliminamos
top_3_negative = corr_puntaje.nsmallest(3)
top_atributos = pd.concat([top_3_positive, top_3_negative]) #Creación del DF
top_atributos = top_atributos.to_frame()
top_atributos.columns = ['Correlación con Puntaje']
top_atributos.index.name = 'Atributo'

#Eliminamos los atributos con valor de 0 en todas sus filas que indican que no se cuenta con el atributo
atributos_restaurant = atributos_restaurant.drop(atributos_restaurant.columns[atributos_restaurant.eq(0).all()],axis=1)
mejorar_atributos = []
for e in top_atributos.index:
    if e not in atributos_restaurant.columns:
        mejorar_atributos.append(e)
mejorar_atributos = pd.DataFrame(mejorar_atributos, columns=["Atributos"])

#Diseño de grafico indicador
kpi_atrib= (6 - len(mejorar_atributos)) / 6 * 100

fig_kpi3 = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = kpi_atrib,
    domain = {'x': [1, 0], 'y': [1, 0]},
    title = {'text': "Porcentaje de Atributos Clave", 'font': {'size': 24,'color':"orange"}},
    delta = {'reference': 100, 'increasing': {'color': "orange"}},
    gauge = {
        'axis': {'range': [0, 100], 'tickwidth': 3, 'tickcolor': "orange"},
        'bar': {'color': "orange"},
        'bgcolor': "yellow",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 60], 'color': '#FD5752'},
            {'range': [60, 80], 'color': '#FAFD52'},
            {'range': [80, 100], 'color': '#ABD758'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 100}},
    number = {'suffix': '%'}))
fig_kpi3.update_layout(width = 420, height = 320, font = {'family': "Arial"})

#Otra opción para gráfico de barras:

matriz_corr_barras = corr_puntaje[1:]
fig_corr_barra = go.Figure(go.Bar(
            x=matriz_corr_barras.index,
            y=matriz_corr_barras.values,
            orientation='v',
            marker=dict(color='orange')
        ))

# Configurar el título y diseño del gráfico
fig_corr_barra.update_layout(
    title="Correlación entre el puntaje y los atributos",            
    xaxis_title="Atributo",
    yaxis_title="Coeficiente de correlación",
    font=dict(family="Arial", size=20),    
    margin=dict(l=200, r=0, t=50, b=50), # Espacio alrededor del gráfico
    width=550 ,height=400,) # Tamaño del gráfico



#***************** Dashboard Análisis de Atributos:

# st.markdown("<h2 style='text-align: center; color: orange;'>Atributos</h2>", unsafe_allow_html=True)
# st.write(atributos_restaurant.columns) #Control dashboard permite ver las columnas filtradas
# st.dataframe(atributos_restaurant) #Control dashboard permite ver el DF de los atributos


##Definir diccionario de atributos para boton

dicc_atrib = {
    "Ambiente": ["Ambience","GoodForDancing","Music","Atmosphere","NoiseLevel"], 
    "Para grupos": ["RestaurantsGoodForGroups","Crowd", "AgesAllowed"], 
    "Promociones": ["HappyHour","Offerings"], 
    "Estacionamiento":["BikeParking","BusinessParking"],    
    "Mejores noches": ["BestNights"],
    "Inclusivo":["WheelchairAccessible","DogsAllowed","Accessibility"], 
    "Amenidades":["HasTV","GoodForKids","WiFi","Amenities"],     
    "Exteriores":["OutdoorSeating"],
    "Alcohol":["BYOB","Corkage","BYOBCorkage","Alcohol"], 
    "Restricciones en dieta":["DietaryRestrictions"],
    "Reservaciones":["ByAppointmentOnly","RestaurantsReservations","Planning"],    
    "Tipo de servicio":["DriveThru","RestaurantsDelivery","RestaurantsTakeOut","RestaurantsTableService","RestaurantsCounterService","Caters","Service options"],    #  
    "Guardaropa":["CoatCheck"],    
    "24 horas":["Open24Hours"],
    "Tipos de pago":["BusinessAcceptsCreditCards","BusinessAcceptsBitcoin","Payments"], 
    "Opciones (Des,Com,Cena)":["Dining options","GoodForMeal","Popular for"], 
    "Tipo director":["From the business","Filosofia","Historia","Prácticas"],
    "Vestimenta":["RestaurantsAttire"],
    "Salud y Seguridad": ["Health and safety"],    
    "Rango de precios":["RestaurantsPriceRange2","Escala del 1 al 4"],
    "Aspectos destacados":["Highlights","Hechas por usuarios"], 
    "Fumar":["Smoking"],
}




col1, col2, col3, col4, col5 = st.columns(5) #Se utiliza este línea para acomodar al centro el gráfico al disminuirlo de tamaño
with col2: #KPI
    st.plotly_chart(fig_kpi3, config={"displayModeBar": False, "responsive": True})

# col1,col2,col3 = st.columns(3) #Colocamos en columnas del Dashboard
# with col1: #Top6 atributos
#     st.markdown(f"<h6 style='text-align: center;'>Top 6 Atributos influyentes<br>{slide_tipo}</h6>", unsafe_allow_html=True)    
#     st.write(top_atributos)
# with col2:#Atributos del restaurante
#     st.markdown(f"<h6 style='text-align: center;'>Atributos de:<br> {slide_restaurant}</h6>", unsafe_allow_html=True)
#     df_atrib_rest=pd.DataFrame(atributos_restaurant.columns,columns=["Atributos"])
#     st.write(df_atrib_rest)
# with col3: #Atributos pendientes
#     if len(mejorar_atributos) == 0:
#         st.markdown(f"<h6 style='text-align: center;'>Se tienen cubierto los 6 atributos más relevantes</h6>", unsafe_allow_html=True)        
#     else:
#         st.markdown(f"<h6 style='text-align: center;'>Atributos a considerar</h6>", unsafe_allow_html=True)        
#         st.table(mejorar_atributos)
#         if st.button('Ver características'):
#             mejorar_atributos["Características"] = mejorar_atributos["Atributos"].map(dicc_atrib)
#             mejorar_atributos

tab1, tab2, tab3 = st.tabs(["Top 6", "Actuales", "A considerar"])

with tab1:
   st.header(f"Top 6 Atributos influyentes de {slide_tipo}")
   st.table(top_atributos)

with tab2:
   st.header(f"Atributos de {slide_restaurant}")
   df_atrib_rest=pd.DataFrame(atributos_restaurant.columns,columns=["Atributos"])
   st.table(df_atrib_rest)

with tab3:
    st.header(f"Atributos a considerar")
    st.table(mejorar_atributos)
    if st.button('Ver características'):
        mejorar_atributos["Características"] = mejorar_atributos["Atributos"].map(dicc_atrib)
        mejorar_atributos

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig_corr_barra)
#----------------------------------------------Fin Análisis de Atributos---------------------------------------------


#-------------------------------------------- Inicio Métricas Macroeconómicas-----------------------------------------------
#---Tasa de Interés

tasa_interes = yf.Ticker("^TNX")
tasa_hist= tasa_interes.history(period="8y")
tasa_hist= tasa_hist["Close"]
media = round(tasa_hist.mean(),2)
tasa = round(tasa_hist.iloc[-1],2)
var_tasa = tasa - media

#Grafico de líneas tasa FED
fig_tasa = go.Figure()
fig_tasa.add_trace(go.Scatter(x=tasa_hist.index, y=tasa_hist.values,
                    mode='lines',
                    name='Tasa de interés',
                    line=dict(color='orange', width=2)))
fig_tasa.update_layout(
    font=dict(family="Arial",size=12,color='orange' ),
    xaxis_title="Fecha",
    yaxis_title="Tasa de interés",
    plot_bgcolor='rgba(0,0,0,0)',
    autosize=True,
    margin=dict(l=50, r=0, t=0, b=0),
    width = 650, height=300)

#ETF TIP como valor del posible comportamiento de la inflación
inflacion_yahoo = yf.Ticker("TIP")
infla_y= inflacion_yahoo.history(period="5y")
infla_y= infla_y["Close"]
infla_media = round(infla_y.mean(),2)
inflacion = round(infla_y.iloc[-1],2)
var_infl = inflacion - infla_media

#Grafico de líneas ETF TIP
fig_tip = go.Figure()
fig_tip.add_trace(go.Scatter(x=infla_y.index, y=infla_y.values,
                    mode='lines',
                    name='Tasa de interés',
                    line=dict(color='orange', width=2)))
fig_tip.update_layout(
    font=dict(family="Arial",size=12,color='orange' ),
    xaxis_title="Año",
    yaxis_title="Tasa de interés",
    plot_bgcolor='rgba(0,0,0,0)',
    width = 350, height=300)

# Extraer los datos del IPC de USA del Banco Mundial
data = wb.data.DataFrame("FP.CPI.TOTL.ZG", "USA", range(2000,2024), index="time", numericTimeKeys=True, labels=True)
df = pd.DataFrame(data)
df = df.rename(columns={"USA": "IPC", "Time": "Año"}) # Renombrar las columnas
df.set_index("Año", inplace=True) # Convertir la columna de "Año" en un índice de fecha
df = df.sort_values(by="Año",ascending=True)

# Gráfica IPC USA, del Banco Mundial
fig_ipc = go.Figure()
fig_ipc.add_trace(go.Scatter(x=df.index, y=df.IPC,
                    mode='lines',
                    name='IPC',
                    line=dict(color='orange', width=2)))
# Personalizar el diseño de la gráfica
fig_ipc.update_layout(    
    xaxis_title="Año",
    yaxis_title="Variación porcentual",
    font=dict(family="Arial", size=12, color='black'),
    plot_bgcolor='rgba(0,0,0,0)',
    width = 350, height=300)


#************* Dashboard Macroeconómicos

st.markdown("<h2 style='text-align: center; color: orange;'>Indicadores Macroeconómicos</h2>", unsafe_allow_html=True)
# f"El valor medio de ETF (TIP) es: {infla_media}" #Control para diseño
# f"El último valor de ETF (TIP) es: {inflacion}" #Control para diseño
# f"media de la tasa es {media}" #Control para diseño
# f"la tasa es {tasa}" #Control para diseño

col1,col2,col3,col4,col5 = st.columns(5) #Colocamos en columnas del Dashboard
with col2:
    st.metric(label="Tasa de Interés", value=tasa, delta=round(var_tasa,2),delta_color="inverse")
with col4:
    st.metric(label="ETF (TIP)", value=inflacion, delta=round(var_infl,2),delta_color="inverse")

titulo_tasafed = "<h4 style='text-align:center; color:white;'>Tasa de interés de la FED</h4>"
st.markdown(titulo_tasafed, unsafe_allow_html=True)
if st.button('Saber más sobre la tasa de interés'):
    st.write('''
        Es la tasa a la que los bancos prestan dinero.
        Si la tasa de interés aumenta, los préstamos y líneas de crédito se vuelven más costosos.
        Puede afectar el poder adquisitivo de los consumidores.
        Se utiliza para controlar la inflación.''')
st.plotly_chart(fig_tasa)

col1,col2 =st.columns(2)    
with col1:
    titulo_etf = "<h4 style='text-align:center; color:white;'>ETF (TIP)</h4>"
    st.markdown(titulo_etf, unsafe_allow_html=True)
    if st.button('Saber más sobre ETF(TIP)'):
        st.write('''
            Es un fondo cotizado en bolsa que invierte en bonos del Tesoro protegidos contra la inflación de EE. UU.
            Ajusta su valor principal según el índice de precios al consumidor (IPC).
            ''')
    st.plotly_chart(fig_tip)
with col2:
    titulo_ipc = "<h4 style='text-align:center; color:white;'>IPC Banco Mundial</h4>"
    st.markdown(titulo_ipc, unsafe_allow_html=True)
    if st.button('Saber más sobre el IPC'):
        st.write('''
            Es un indicador económico que mide el cambio promedio de los precios de un conjunto de bienes y servicios representativos del consumo de los hogares.
            Se utiliza para medir el poder adquisitivo de una moneda.
            Si el IPC aumenta significativamente, los costos de los ingredientes y los suministros pueden aumentar, lo que a su vez puede llevar a que los precios de los alimentos y las bebidas aumenten.
            ''')
    st.plotly_chart(fig_ipc) # Mostrar la gráfica en Streamlit

