import time
from datetime import datetime
from airflow.models.dag import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
#from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
#from airflow.hooks.base_hook import BaseHook
import pandas as pd
import pyodbc

conn = pyodbc.connect(driver='SQL Server;',
                      host='34.170.174.91;',
                      database='grupo7;',
                      uid='henry;',
                      pwd='CERtificado14')

cursor = conn.cursor()


#extract tasks
#@task()
def get_data():
    
    

    url = input("Ingrese la url de google drive con el archivo a reprocesar: ")
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    #df = pd.read_csv(url, sep=";")
    df = pd.read_json(url, lines=True)
    #datos = pd.DataFrame(df.tail[100])
    datos = df.where(pd.notnull(df), None)
    #datos.info()
    return datos


def transform_data(datos2):
    print("Haciendo transformaciones al datasets")
    datos2.drop(columns=['pics','resp'],inplace=True)
    datos2.dropna(subset='text')[datos2.dropna(subset='text')['text'].str.contains('\n')]  #Quitamos el caracter antes de transformar a csv y vemos que haya quedado todo bien
    datos2['text'] = datos2['text'].replace('\n','')
    datos2.info()

    
#@task 
def load_data(datos3):
    
    print("Insertando datos a la DB")
    #cursor.executemany("INSERT INTO dbo.Arizona (Id_usuario, Id_Restaurant, Fecha, Rating, Resena) VALUES (?,?,?,?,?)", datos3.values.tolist())
    #conn.commit()  
    print(datos3)
    #print("Termine de ingresar datos")   
    
    
def main():
    principal = get_data()
    transform_data(principal) 
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




    


