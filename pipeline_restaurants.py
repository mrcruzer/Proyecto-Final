import time
from datetime import datetime
import pandas as pd
import pyodbc
import json 
import re

conn = pyodbc.connect(driver='ODBC Driver 18 for SQL Server;',
                      host='34.170.174.91;',
                      database='grupo7;',
                      uid='henry;',
                      pwd='CERtificado14',
                      TrustServerCertificate='yes;')

'''conn = pyodbc.connect(DRIVER={ODBC Driver 18 for SQL Server};'
                              'SERVER=' + server + ';'
                              'DATABASE=' + db + ';'
                              'UID=' + user + ';'
                              'PWD=' + pwd)'''

cursor = conn.cursor()


#extract tasks
#@task()
def get_data():
    
    opcion = int(input("Ingrese la opcion deseada para reprocesar: 1: Google, 2: Yelp, 3: Ingresar las dos opciones: "))

    if(opcion == 1):
        df = pd.read_json("./Data/restaurant-google.json", lines=True)
        dataframe = pd.DataFrame(df)
        google_metadata = dataframe.where(pd.notnull(dataframe), None)
        transform_data_google(google_metadata)
        #google_metadata.info()
        #return google_metadata


def transform_data_google(google_metadata):
    print("Haciendo transformaciones al datasets")
    google_metadata.drop_duplicates(subset='gmap_id',inplace=True) #Descartamos los duplicados de gmap_id que es el identificador de lugar

    google_metadata.dropna(subset=['category'],inplace=True)      #Descartamos los nulos debajo de 'category'
    google_metadata.reset_index(inplace=True,drop=True)         #Reseteamos indice

    #Hallamos los índices de los restaurants
    restaurant_indexes = []
    for i in range(google_metadata.shape[0]):
        for j in range(len(google_metadata['category'][i])):
            if google_metadata['category'][i][j].find('estaura')!=-1:
                restaurant_indexes.append(i)
            break

    google = google_metadata[google_metadata.index.isin(restaurant_indexes)]    #Filtramos restaurants

    #Quitamos los valores que no tengan el valor de address y los copiamos en otro dataframe
    restaurants_google = google.dropna(subset=['address'])
    restaurants_google.reset_index(inplace=True, drop=True)

    #Separamos y juntamos los datos
    listado_fallas = []
    localizaciones = []
    for i in range(restaurants_google['address'].values.size):
        try:
            int(restaurants_google['address'].values[i][-1])
            if len(restaurants_google['address'].values[i].split(',')[-1].strip()) == 8:
                localizaciones.append([restaurants_google['gmap_id'].values[i],                                     #Id del restaurant
                                restaurants_google['address'].values[i].split(',')[-2].strip(),                 #Ciudad
                                restaurants_google['address'].values[i].split(',')[-1].strip().split()[0],      #Estado
                                restaurants_google['address'].values[i].split(',')[-1].strip().split()[1]])     #Código postal
            else:
                listado_fallas.append(i)                                    #Anoto cuantas direcciones no me dan los datos necesarios
        except:
            listado_fallas.append(i)

    #Tomamos los valores que fallaron y los enviamos a otro dataframe
    restaurants_google_fallas = restaurants_google[restaurants_google.index.isin(listado_fallas)]
    restaurants_google_fallas.reset_index(inplace=True,drop=True)

    #Agregamos otros datos
    listado_fallas = []
    for i in range(restaurants_google_fallas['address'].values.size):
        try:
            lista_address = restaurants_google_fallas['address'].values[i].split(',')[0:4]      #Cortamos el "United States" de los -->
            int(lista_address[-1][-1])                                                          #registros que los tienen.
            if len(lista_address[-1].strip()) == 8:
                localizaciones.append([restaurants_google_fallas['gmap_id'].values[i],          #Id del restaurant
                                   lista_address[-2].strip(),                               #Ciudad
                                   lista_address[-1].strip().split()[0],                    #Estado
                                   lista_address[-1].strip().split()[1]])                   #Codigo postal
            else:
                listado_fallas.append(i)                                    
        except:
            listado_fallas.append(i)

    #Creamos un nuevo dataframe
    restaurants_google_fallas2 = restaurants_google_fallas[restaurants_google_fallas.index.isin(listado_fallas)]
    restaurants_google_fallas2.reset_index(inplace=True,drop=True)

    #Primero cambiamos los nombres de los estados por sus códigos
    state_codes = {'Alabama': 'AL','Alaska': 'AK','Arizona': 'AZ','Arkansas': 'AR','California': 'CA','Colorado': 'CO','Connecticut': 'CT',
    'Delaware': 'DE','Florida': 'FL','Georgia': 'GA','Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL','Indiana': 'IN','Iowa': 'IA',
    'Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA','Maine': 'ME','Maryland': 'MD','Massachusetts': 'MA','Michigan': 'MI',
    'Minnesota': 'MN','Mississippi': 'MS','Missouri': 'MO','Montana': 'MT','Nebraska': 'NE','Nevada': 'NV','New Hampshire': 'NH',
    'New Jersey': 'NJ','New Mexico': 'NM','New York': 'NY','North Carolina': 'NC','North Dakota': 'ND','Ohio': 'OH','Oklahoma': 'OK',
    'Oregon': 'OR','Pennsylvania': 'PA','Rhode Island': 'RI','South Carolina': 'SC','South Dakota': 'SD','Tennessee': 'TN','Texas': 'TX',
    'Utah': 'UT','Vermont': 'VT','Virginia': 'VA','Washington': 'WA','West Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY'}

    for state, code in state_codes.items():
        restaurants_google_fallas2['address'] = restaurants_google_fallas2['address'].str.replace(state,code)

    #Quitamos los caracteres extraños
    for i in range(restaurants_google_fallas2.shape[0]):
        restaurants_google_fallas2['address'][i] = re.sub(r'[^a-zA-Z0-9,\s]', '', restaurants_google_fallas2['address'][i])

    #Agregamos los últimos datos
    listado_fallas = []
    for i in range(restaurants_google_fallas2['address'].values.size):
        try:
            int(restaurants_google_fallas2.iloc[i]['address'][0])         #Si esto sucede entonces el primer digito es un numero
            localizaciones.append([restaurants_google_fallas2['gmap_id'].values[i],                                     #Id del restaurant
                            restaurants_google_fallas2['address'].values[i].split(',')[1].strip(),                 #Ciudad
                            restaurants_google_fallas2['address'].values[i].split(',')[0].strip().split()[1],      #Estado
                            restaurants_google_fallas2['address'].values[i].split(',')[0].strip().split()[0]])     #Código postal
        except:
            listado_fallas.append(i)                                        #Anoto cuantas direcciones no me dan los datos necesarios

    localizacion = pd.DataFrame(columns=['gmap_id','Ciudad','Estado','Cod_postal'],data=localizaciones) #Armamos dataframe con estos datos

    restaurants_google = pd.merge(google,localizacion,how='left',on='gmap_id')      #Juntamos con el dataframe de restaurants de google

    restaurants_google.drop(columns=['description','avg_rating','num_of_reviews','price',                   #Descartamos columnas
                                 'hours','state','relative_results','url','address'], inplace=True)

    restaurants_google.rename(columns={'name':'Nombre','gmap_id':'Id_Restaurant','latitude':'Latitud','longitude':'Longitud',
                                   'category':'Tipo','MISC':'Atributos'},inplace=True)              #Cambiamos nombre

    restaurants_google = restaurants_google[['Id_Restaurant','Nombre','Ciudad','Estado','Cod_postal',       #Reordenamos
                                         'Latitud', 'Longitud', 'Tipo', 'Atributos']]

    restaurants_google.dropna(subset=['Cod_postal'],inplace=True)                     #Descartamos valores nulos de cod postal (y por lo tanto de estado y ciudad)
    restaurants_google.reset_index(inplace=True,drop=True)                          #Reseteamos indices

    #Armamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
    duplicados_google = restaurants_google[restaurants_google.duplicated(subset=['Nombre','Cod_postal'],keep=False)].sort_values(by='Nombre')

    duplicados_google.reset_index(inplace=True,drop=True)       #Reseteamos indices

    negocios_duplicados_google = duplicados_google.drop_duplicates(subset=['Nombre','Cod_postal'])      #Armamos dataframe con los negocios duplicados unicos que haya

    #Tomamos los ids a conservar y los que se van a cambiar
    lista_duplicados = []
    for n in negocios_duplicados_google['Id_Restaurant'].values:
        aux = []
        nombre = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurant']==n]['Nombre'].values[0]
        cod_postal = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurant']==n]['Cod_postal'].values[0]
    for d in range(duplicados_google.shape[0]):
        if (duplicados_google['Nombre'][d] == nombre) and (duplicados_google['Cod_postal'][d] == cod_postal) and (duplicados_google['Id_Restaurant'][d] != n):
            aux.append(duplicados_google['Id_Restaurant'][d])
            lista_duplicados.append([n,aux])

    duplicados_google_df = pd.DataFrame(data=lista_duplicados,columns=['Conservar','Cambiar'])  #Armammos dataframe

#Descartamos los duplicados
    restaurants_google.drop_duplicates(subset=['Nombre','Cod_postal'],inplace=True)
    restaurants_google.reset_index(inplace=True,drop=True)

    
#@task 
def load_data(datos3):
    
    print("Insertando datos a la DB")
    #cursor.executemany("INSERT INTO dbo.Arizona (Id_usuario, Id_Restaurant, Fecha, Rating, Resena) VALUES (?,?,?,?,?)", datos3.values.tolist())
    #conn.commit()  
    print(datos3)
    #print("Termine de ingresar datos")   
    
    
def main():
    principal = get_data()
    #transform_data(principal) 
    #load_data(principal)
    
    
main()
    
# [START how_to_task_group]
'''with DAG(dag_id="reviews_etl_dag",schedule_interval="0 9 * * *", start_date=datetime(2022, 3, 5),catchup=False,  tags=["reviews"]) as dag:

    with TaskGroup("extract_reviews_load", tooltip="Extract and load source data") as extract_load_src:
        get_data_full = get_data()
        load_data_full = load_data(get_data_full)
        #define order
        get_data_full >> load_data_full'''

    # [START howto_task_group_section_2]
'''with TaskGroup("transform_src_product", tooltip="Transform and stage data") as transform_src_product:
        transform_srcProduct = transform_srcProduct()
        transform_srcProductSubcategory = transform_srcProductSubcategory()
        transform_srcProductCategory = transform_srcProductCategory()
        #define task order
        [transform_srcProduct, transform_srcProductSubcategory, transform_srcProductCategory]

    with TaskGroup("load_product_model", tooltip="Final Product model") as load_product_model:
        prd_Product_model = prdProduct_model()
        #define order
        prd_Product_model

    extract_load_src >> transform_src_product >> load_product_model'''




    


