import time
from datetime import datetime
import pandas as pd
import pyodbc
import json 
import re
from time import sleep

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
    
    opcion = int(input("Ingrese la opcion deseada para reprocesar Restaurantes: 1: Google, 2: Yelp, 3: Google + Yelp: "))

    if(opcion == 1):
        data_google()
        
    elif(opcion == 2):
        data_yelp()

    elif(opcion == 3):
      data_google_yelp()

    else: 
        print("Ingresa la opcion deseada")


def load_data(datos):
    print("Insertando datos a la DB")

    for index, row in datos.iterrows():
        cursor.execute("INSERT INTO dbo.Restaurantes (Id_Restaurante, Nombre, Ciudad, Estado, Cod_postal, Latitud, Longitud, Tipo, Atributos) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  row.Id_Restaurante, row.Nombre, row.Ciudad, row.Estado, row.Cod_postal, row.Latitud, row.Longitud, row.Tipo, row.Atributos
                   )
    cursor.commit()

    print("Termine de ingresar datos")  



def data_yelp():
    df = pd.read_pickle("./Data/restaurant-yelp.pkl")
    dataframe = pd.DataFrame(df)
    business_yelp = dataframe.where(pd.notnull(dataframe), None)
    business_yelp_filt = business_yelp.iloc[:,:14]                  #Descartamos segundo set de columnas

    #Tomamos solo los que tengan restaurant bajo category. Dropeamos primero entonces las categories nulas
    business_yelp_filt.dropna(subset='categories',inplace=True)

    #Filtramos unicamente los restaurants
    restaurants_yelp = business_yelp_filt[business_yelp_filt['categories'].str.contains('estaura')]

    #Reseteamos el índice y descartamos los valores duplicados de business_id
    restaurants_yelp.drop_duplicates(subset='business_id',inplace=True)
    restaurants_yelp.reset_index(inplace=True,drop=True)

    #Descartamos columnas que no vayamos a utilizar, renombramos y reordenamos
    restaurants_yelp.drop(columns=['address','stars','review_count','is_open','hours'],inplace=True)
    restaurants_yelp.rename(columns={'business_id':'Id_Restaurante','name':'Nombre','city':'Ciudad','state':'Estado','postal_code':'Cod_postal',
                                 'latitude':'Latitud','longitude':'Longitud','attributes':'Atributos','categories':'Tipo'},inplace=True)
    restaurants_yelp = restaurants_yelp[['Id_Restaurante', 'Nombre', 'Ciudad', 'Estado', 'Cod_postal', 'Latitud',
                                    'Longitud','Tipo','Atributos']]
    
    # el campo Tipo y Atributos lo cambio a String
    restaurants_yelp['Tipo'] = restaurants_yelp['Tipo'].astype(str) 
    restaurants_yelp['Atributos'] = restaurants_yelp['Atributos'].astype(str) 
    
    restaurants_yelp
    print(restaurants_yelp.head())

    print("Esperando para ingresar datos")

    sleep(5)

    load_data(restaurants_yelp)


    return restaurants_yelp




def data_google():
    df = pd.read_json("./Data/restaurant-google.json", lines=True)
    dataframe = pd.DataFrame(df)
    google_metadata = dataframe.where(pd.notnull(dataframe), None)
    
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

    restaurants_google.rename(columns={'name':'Nombre','gmap_id':'Id_Restaurante','latitude':'Latitud','longitude':'Longitud',
                                   'category':'Tipo','MISC':'Atributos'},inplace=True)              #Cambiamos nombre

    restaurants_google = restaurants_google[['Id_Restaurante','Nombre','Ciudad','Estado','Cod_postal',       #Reordenamos
                                         'Latitud', 'Longitud', 'Tipo', 'Atributos']]

    restaurants_google.dropna(subset=['Cod_postal'],inplace=True)                     #Descartamos valores nulos de cod postal (y por lo tanto de estado y ciudad)
    restaurants_google.reset_index(inplace=True,drop=True)                          #Reseteamos indices

    #Armamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
    duplicados_google = restaurants_google[restaurants_google.duplicated(subset=['Nombre','Cod_postal'],keep=False)].sort_values(by='Nombre')

    duplicados_google.reset_index(inplace=True,drop=True)       #Reseteamos indices

    negocios_duplicados_google = duplicados_google.drop_duplicates(subset=['Nombre','Cod_postal'])      #Armamos dataframe con los negocios duplicados unicos que haya

    #Tomamos los ids a conservar y los que se van a cambiar
    lista_duplicados = []
    for n in negocios_duplicados_google['Id_Restaurante'].values:
        aux = []
        nombre = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurante']==n]['Nombre'].values[0]
        cod_postal = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurante']==n]['Cod_postal'].values[0]
    for d in range(duplicados_google.shape[0]):
        if (duplicados_google['Nombre'][d] == nombre) and (duplicados_google['Cod_postal'][d] == cod_postal) and (duplicados_google['Id_Restaurante'][d] != n):
            aux.append(duplicados_google['Id_Restaurante'][d])
            lista_duplicados.append([n,aux])

        duplicados_google_df = pd.DataFrame(data=lista_duplicados,columns=['Conservar','Cambiar'])  #Armammos dataframe

    #Descartamos los duplicados
    restaurants_google.drop_duplicates(subset=['Nombre','Cod_postal'],inplace=True)
    restaurants_google.reset_index(inplace=True,drop=True)

    # el campo Tipo y Atributos lo cambio a String
    restaurants_google['Tipo'] = restaurants_google['Tipo'].astype(str) 
    restaurants_google['Atributos'] = restaurants_google['Atributos'].astype(str) 

    restaurants_google
    #nuevo = restaurants_google.tail(10)
    print(restaurants_google.head(10))

    #restaurants_google.to_json("./Data/restaurant_cruce_google.json")

    #nuevo = restaurants_google.tail(10)

    print("Esperando para insertar")

    sleep(5)

    load_data(restaurants_google)

    return restaurants_google
 


def data_google_yelp():
    df = pd.read_json("./Data/restaurant-google.json", lines=True)
    dataframe = pd.DataFrame(df)
    google_metadata = dataframe.where(pd.notnull(dataframe), None)
    
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

    restaurants_google.rename(columns={'name':'Nombre','gmap_id':'Id_Restaurante','latitude':'Latitud','longitude':'Longitud',
                                   'category':'Tipo','MISC':'Atributos'},inplace=True)              #Cambiamos nombre

    restaurants_google = restaurants_google[['Id_Restaurante','Nombre','Ciudad','Estado','Cod_postal',       #Reordenamos
                                         'Latitud', 'Longitud', 'Tipo', 'Atributos']]

    restaurants_google.dropna(subset=['Cod_postal'],inplace=True)                     #Descartamos valores nulos de cod postal (y por lo tanto de estado y ciudad)
    restaurants_google.reset_index(inplace=True,drop=True)                          #Reseteamos indices

    #Armamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
    duplicados_google = restaurants_google[restaurants_google.duplicated(subset=['Nombre','Cod_postal'],keep=False)].sort_values(by='Nombre')

    duplicados_google.reset_index(inplace=True,drop=True)       #Reseteamos indices

    negocios_duplicados_google = duplicados_google.drop_duplicates(subset=['Nombre','Cod_postal'])      #Armamos dataframe con los negocios duplicados unicos que haya

    #Tomamos los ids a conservar y los que se van a cambiar
    lista_duplicados = []
    for n in negocios_duplicados_google['Id_Restaurante'].values:
        aux = []
        nombre = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurante']==n]['Nombre'].values[0]
        cod_postal = negocios_duplicados_google[negocios_duplicados_google['Id_Restaurante']==n]['Cod_postal'].values[0]
    for d in range(duplicados_google.shape[0]):
        if (duplicados_google['Nombre'][d] == nombre) and (duplicados_google['Cod_postal'][d] == cod_postal) and (duplicados_google['Id_Restaurante'][d] != n):
            aux.append(duplicados_google['Id_Restaurante'][d])
            lista_duplicados.append([n,aux])

        duplicados_google_df = pd.DataFrame(data=lista_duplicados,columns=['Conservar','Cambiar'])  #Armammos dataframe

    #Descartamos los duplicados
    restaurants_google.drop_duplicates(subset=['Nombre','Cod_postal'],inplace=True)
    restaurants_google.reset_index(inplace=True,drop=True)

    # el campo Tipo y Atributos lo cambio a String
    restaurants_google['Tipo'] = restaurants_google['Tipo'].astype(str) 
    restaurants_google['Atributos'] = restaurants_google['Atributos'].astype(str) 

    restaurants_google
    #nuevo = restaurants_google.tail(10)
    print(restaurants_google.head(10))

    #return restaurants_google

    df1 = pd.read_pickle("./Data/restaurant-yelp.pkl")
    dataframe = pd.DataFrame(df1)
    business_yelp = dataframe.where(pd.notnull(dataframe), None)
    business_yelp_filt = business_yelp.iloc[:,:14]                  #Descartamos segundo set de columnas

    #Tomamos solo los que tengan restaurant bajo category. Dropeamos primero entonces las categories nulas
    business_yelp_filt.dropna(subset='categories',inplace=True)

    #Filtramos unicamente los restaurants
    restaurants_yelp = business_yelp_filt[business_yelp_filt['categories'].str.contains('estaura')]

    #Reseteamos el índice y descartamos los valores duplicados de business_id
    restaurants_yelp.drop_duplicates(subset='business_id',inplace=True)
    restaurants_yelp.reset_index(inplace=True,drop=True)

    #Descartamos columnas que no vayamos a utilizar, renombramos y reordenamos
    restaurants_yelp.drop(columns=['address','stars','review_count','is_open','hours'],inplace=True)
    restaurants_yelp.rename(columns={'business_id':'Id_Restaurante','name':'Nombre','city':'Ciudad','state':'Estado','postal_code':'Cod_postal',
                                 'latitude':'Latitud','longitude':'Longitud','attributes':'Atributos','categories':'Tipo'},inplace=True)
    restaurants_yelp = restaurants_yelp[['Id_Restaurante', 'Nombre', 'Ciudad', 'Estado', 'Cod_postal', 'Latitud',
                                    'Longitud','Tipo','Atributos']]
    
    # el campo Tipo y Atributos lo cambio a String
    restaurants_yelp['Tipo'] = restaurants_yelp['Tipo'].astype(str) 
    restaurants_yelp['Atributos'] = restaurants_yelp['Atributos'].astype(str) 
    
    restaurants_yelp
    print(restaurants_yelp.head())


    #Ahora cruzamos los datos de google y yelp
    #Reducimos los dataframes así es más liviano el trabajo
    google_id_nombre_postal = restaurants_google[['Id_Restaurante','Nombre','Cod_postal']]
    yelp_id_nombre_postal = restaurants_yelp[['Id_Restaurante','Nombre','Cod_postal']]

    #Juntamos los dataframes
    merge = pd.merge(google_id_nombre_postal,yelp_id_nombre_postal,on=['Nombre','Cod_postal'])

    #Descartamos los registros del dataset de yelp
    indices_descarte = restaurants_yelp[restaurants_yelp['Id_Restaurante'].isin(merge['Id_Restaurante_y'].values)].index
    restaurants_yelp.drop(index=indices_descarte,inplace=True)
    restaurants_yelp.reset_index(inplace=True,drop=True)

    #Armamos un solo dataframe de negocios
    restaurants = pd.concat([restaurants_google,restaurants_yelp],ignore_index=True)

    print(restaurants.head(10))

    #nuevo = restaurants.tail(10)

    print("Estoy insertado la data")

    sleep(5)

    load_data(restaurants)

    return restaurants 

    
    
def main():
    principal = get_data()
    
    
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




    


