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
    
    opcion = int(input("Ingrese la opcion deseada para reprocesar Reviews: 1: Google, 2: Yelp, 3: Google + Yelp: "))

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
        cursor.execute("INSERT INTO dbo.Resenas (Id_Usuario, Id_Restaurante, Fecha, Rating, Resena) values(?, ?, ?, ?, ?)", 
                  row.Id_Usuario, row.Id_Restaurante, row.Fecha, row.Rating, row.Resena
                   )
    cursor.commit()

    print("Termine de ingresar datos")



def data_yelp():
    # Cargamos las review de google
    df = pd.read_json("./Data/review-yelp.json", lines=True)
    dataframe = pd.DataFrame(df)
    yelp_review = dataframe.where(pd.notnull(dataframe), None)

    # Llamamos los restaurantes de la DB
    sql = "Select * From dbo.Restaurantes"
    restaurants_yelp = pd.read_sql(sql,conn) 

    #Probamos filtrar
    yelp_review_filtro = yelp_review[yelp_review['business_id'].isin(restaurants_yelp['Id_Restaurante'].values)]

    #Descartamos los campos que no se utilizan
    yelp_review_filtro.drop(columns=['review_id','useful','funny','cool'],inplace=True)

    #Cambiamos el nombre
    yelp_review_filtro.rename(columns={'user_id':'Id_Usuario','business_id':'Id_Restaurante','stars':'Rating','text':'Resena', 'date':'Fecha'}, inplace=True)
    yelp_review_filtro.info()

     #Reordenamos
    yelp_review_filtro = yelp_review_filtro[['Id_Usuario', 'Id_Restaurante', 'Fecha', 'Rating', 'Resena']]
    yelp_review_filtro.drop_duplicates(inplace=True)
    #yelp_review_final = pd.DataFrame(yelp_review_filtro)

    yelp_review_filtro

    print("Estoy insertando data a la DB")

    sleep(5)

    load_data(yelp_review_filtro)

    return yelp_review_filtro


def data_google():
    # Cargamos las review de google
    df = pd.read_json("./Data/review-google.json", lines=True)
    dataframe = pd.DataFrame(df)
    google_review = dataframe.where(pd.notnull(dataframe), None)

    # Llamamos los restaurantes de la DB
    sql = "Select * From dbo.Restaurantes"
    restaurants_google = pd.read_sql(sql,conn) 


    #Armamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
    duplicados_google = restaurants_google[restaurants_google.duplicated(subset=['Nombre','Cod_Postal'],keep=False)].sort_values(by='Nombre')

    duplicados_google.reset_index(inplace=True,drop=True)       #Reseteamos indices

    negocios_duplicados_google = duplicados_google.drop_duplicates(subset=['Nombre','Cod_Postal'])      #Armamos dataframe con los negocios duplicados unicos que haya

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
    restaurants_google.drop_duplicates(subset=['Nombre','Cod_Postal'],inplace=True)
    restaurants_google.reset_index(inplace=True,drop=True)

    # filtramos 
    review_filtrado = google_review[google_review['gmap_id'].isin(restaurants_google['Id_Restaurante'].values)]

    #Definimos la función para realizar el reemplazo de los ids de los usuarios
    def cambioDeIndices (reviews_df,duplicados_df):
        for f in range(duplicados_df.shape[0]):
            reemplazador = duplicados_df['Conservar'][f]
        for c in duplicados_df['Cambiar'][f]:
            if reviews_df[reviews_df['Id_Restaurante']== c].index.size>0:
                for i in reviews_df[reviews_df['Id_Restaurante']== c].index:
                    reviews_df.at[i,'Id_Restaurante'] = reemplazador
        return reviews_df

    review_filtrado.drop(columns=['name','pics','resp'],inplace=True)                            #Descartamos columnas que no se usan
    review_filtrado.rename(columns={'user_id':'Id_Usuario','time':'Fecha',                   #Renombramos columnas
                        'text':'Resena','gmap_id':'Id_Restaurante','rating':'Rating'},inplace=True)
    
    review_filtrado['Fecha'] = review_filtrado['Fecha'].values.astype(dtype='datetime64[ms]')

    #print(review_filtrado.head(10))
    review_filtrado = review_filtrado[['Id_Usuario','Id_Restaurante','Fecha','Rating','Resena']] #Reordenamos     
    review_filtrado.drop_duplicates(inplace=True)                                                #Descartamos duplicados
    #review_filtrado = cambioDeIndices(review_filtrado,duplicados_google_df)                           #Cambiamos los ids de restaurant

    #Filtramos restaurants con reviews del dataframe de restaurants
    restaurants_google_con_reviews = restaurants_google[restaurants_google['Id_Restaurante'].isin(review_filtrado['Id_Restaurante'].unique())]
    restaurants_google = restaurants_google_con_reviews.reset_index(drop=True)

    #Filtramos el dataframe de reviews con los restaurants que estan en el dataframe de restaurants
    reviews_google = review_filtrado[review_filtrado['Id_Restaurante'].isin(restaurants_google['Id_Restaurante'].values)]
    reviews_google.reset_index(inplace=True,drop=True)

    print(reviews_google.head(10))

    #nuevo = reviews_google.tail(10)

    print("Estoy insertando la data a la DB")

    sleep(5)

    load_data(reviews_google)


    return reviews_google

 


def data_google_yelp():
    # Cargamos las review de google
    df = pd.read_json("./Data/review-google.json", lines=True)
    dataframe = pd.DataFrame(df)
    google_review = dataframe.where(pd.notnull(dataframe), None)

    # Llamamos los restaurantes de la DB
    sql = "Select * From dbo.Restaurantes"
    restaurants_google = pd.read_sql(sql,conn) 


    #Armamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
    duplicados_google = restaurants_google[restaurants_google.duplicated(subset=['Nombre','Cod_Postal'],keep=False)].sort_values(by='Nombre')

    duplicados_google.reset_index(inplace=True,drop=True)       #Reseteamos indices

    negocios_duplicados_google = duplicados_google.drop_duplicates(subset=['Nombre','Cod_Postal'])      #Armamos dataframe con los negocios duplicados unicos que haya

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
    restaurants_google.drop_duplicates(subset=['Nombre','Cod_Postal'],inplace=True)
    restaurants_google.reset_index(inplace=True,drop=True)

    # filtramos 
    review_filtrado = google_review[google_review['gmap_id'].isin(restaurants_google['Id_Restaurante'].values)]

    #Definimos la función para realizar el reemplazo de los ids de los usuarios
    def cambioDeIndices (reviews_df,duplicados_df):
        for f in range(duplicados_df.shape[0]):
            reemplazador = duplicados_df['Conservar'][f]
        for c in duplicados_df['Cambiar'][f]:
            if reviews_df[reviews_df['Id_Restaurante']== c].index.size>0:
                for i in reviews_df[reviews_df['Id_Restaurante']== c].index:
                    reviews_df.at[i,'Id_Restaurante'] = reemplazador
        return reviews_df

    review_filtrado.drop(columns=['name','pics','resp'],inplace=True)                            #Descartamos columnas que no se usan
    review_filtrado.rename(columns={'user_id':'Id_Usuario','time':'Fecha',                   #Renombramos columnas
                        'text':'Resena','gmap_id':'Id_Restaurante','rating':'Rating'},inplace=True)
    
    review_filtrado['Fecha'] = review_filtrado['Fecha'].values.astype(dtype='datetime64[ms]')

    #print(review_filtrado.head(10))
    review_filtrado = review_filtrado[['Id_Usuario','Id_Restaurante','Fecha','Rating','Resena']] #Reordenamos     
    review_filtrado.drop_duplicates(inplace=True)                                                #Descartamos duplicados
    #review_filtrado = cambioDeIndices(review_filtrado,duplicados_google_df)                           #Cambiamos los ids de restaurant

    #Filtramos restaurants con reviews del dataframe de restaurants
    restaurants_google_con_reviews = restaurants_google[restaurants_google['Id_Restaurante'].isin(review_filtrado['Id_Restaurante'].unique())]
    restaurants_google = restaurants_google_con_reviews.reset_index(drop=True)

    #Filtramos el dataframe de reviews con los restaurants que estan en el dataframe de restaurants
    reviews_google = review_filtrado[review_filtrado['Id_Restaurante'].isin(restaurants_google['Id_Restaurante'].values)]
    reviews_google.reset_index(inplace=True,drop=True)

    # Cargamos las review de google
    df1 = pd.read_json("./Data/review-yelp.json", lines=True)
    dataframe1 = pd.DataFrame(df1)
    yelp_review = dataframe1.where(pd.notnull(dataframe1), None)

    # Llamamos los restaurantes de la DB
    sql = "Select * From dbo.Restaurantes"
    restaurants_yelp = pd.read_sql(sql,conn) 

    #Probamos filtrar
    yelp_review_filtro = yelp_review[yelp_review['business_id'].isin(restaurants_yelp['Id_Restaurante'].values)]

    #Descartamos los campos que no se utilizan
    yelp_review_filtro.drop(columns=['review_id','useful','funny','cool'],inplace=True)

    #Cambiamos el nombre
    yelp_review_filtro.rename(columns={'user_id':'Id_Usuario','business_id':'Id_Restaurante','stars':'Rating','text':'Resena', 'date':'Fecha'}, inplace=True)
    yelp_review_filtro.info()

     #Reordenamos
    yelp_review_filtro = yelp_review_filtro[['Id_Usuario', 'Id_Restaurante', 'Fecha', 'Rating', 'Resena']]
    yelp_review_filtro.drop_duplicates(inplace=True)
   
    reviews_finales = pd.concat([reviews_google,yelp_review_filtro],ignore_index=True)        #Armamos un único dataframe de reviews

    print(reviews_finales.head(10))

    #reviews_finales.tail(10)

    print("Insertando datos a la DB")

    sleep(5)

    load_data(reviews_finales)

    return reviews_finales
    
    
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




    


