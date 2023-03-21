#Importamos las librerías necesarias
import pandas as pd
import numpy as np
import re

#Importamos datos crudos de los negocios de google
for i in range(1,12):
    if i == 1:
        google_metadata = pd.read_json('metadata-sitios/'+str(i)+'.json',lines=True)
    else:
        google_metadata = pd.concat([google_metadata,pd.read_json('metadata-sitios/'+str(i)+'.json',lines=True)])

google_metadata.drop_duplicates(subset='gmap_id',inplace=True) #Descartamos los duplicados de gmap_id que es el identificador de lugar

google_metadata.dropna(subset='category',inplace=True)      #Descartamos los nulos debajo de 'category'
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
restaurants_google = google.dropna(subset='address')
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

restaurants_google.dropna(subset='Cod_postal',inplace=True)                     #Descartamos valores nulos de cod postal (y por lo tanto de estado y ciudad)
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

#Importamos todos los datasets de reviews de los estados y filtramos con los gmaps de los restaurants
estados = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Columbia','Georgia',
           'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan',
           'Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New_Hampshire','New_Jersey','New_Mexico','New_York',
           'North_Carolina','North_Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode_Island','South_Carolina','South_Dakota',
           'Tennessee', 'Texas', 'Utah','Vermont', 'Virginia', 'Washington', 'West_Virginia', 'Wisconsin', 'Wyoming']
for e in estados:
    for i in range(1,50):
        if i == 1:
            estado = pd.read_json('reviews-estados/review-'+e+'/1.json',lines=True)
        else:
            try:
                estado = pd.concat([estado,pd.read_json('reviews-estados/review-'+e+'/'+str(i)+'.json',lines=True)])
            except:
                break
    estado_filtrado = estado[estado['gmap_id'].isin(google['gmap_id'].values)]
    if e == 'Alabama':
        estados_df = estado_filtrado
    else:
        estados_df = pd.concat([estados_df,estado_filtrado],ignore_index=True)
    
#Definimos la función para realizar el reemplazo de los ids de los usuarios
def cambioDeIndices (reviews_df,duplicados_df):
    for f in range(duplicados_df.shape[0]):
        reemplazador = duplicados_df['Conservar'][f]
        for c in duplicados_df['Cambiar'][f]:
            if reviews_df[reviews_df['Id_Restaurant']== c].index.size>0:
                for i in reviews_df[reviews_df['Id_Restaurant']== c].index:
                    reviews_df.at[i,'Id_Restaurant'] = reemplazador
    return reviews_df

estados_df.drop(columns=['name','pics','resp'],inplace=True)                            #Descartamos columnas que no se usan
estados_df.rename(columns={'user_id':'Id_Usuario','time':'Timestamp',                   #Renombramos columnas
                        'text':'Reseña','gmap_id':'Id_Restaurant','rating':'Rating'},inplace=True)
estados_df = estado[['Id_Usuario','Id_Restaurant','Rating','Reseña','Timestamp']]       #Reordenamos
estados_df.drop_duplicates(inplace=True)                                                #Descartamos duplicados
estados_df = cambioDeIndices(estados_df,duplicados_google_df)                           #Cambiamos los ids de restaurant

#Filtramos restaurants con reviews del dataframe de restaurants
restaurants_google_con_reviews = restaurants_google[restaurants_google['Id_Restaurant'].isin(estados_df['Id_Restaurant'].unique())]
restaurants_google = restaurants_google_con_reviews.reset_index(drop=True)

#Filtramos el dataframe de reviews con los restaurants que estan en el dataframe de restaurants
reviews_google = estados_df[estados_df['Id_Restaurant'].isin(restaurants_google['Id_Restaurant'].values)]
reviews_google.reset_index(inplace=True,drop=True)



#Arrancamos con la transformación del dataset de yelp
#Importamos listado de negocios de yelp
business_yelp = pd.read_pickle('yelp/business.pkl')
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
restaurants_yelp.rename(columns={'business_id':'Id_Restaurant','name':'Nombre','city':'Ciudad','state':'Estado','postal_code':'Cod_postal',
                                 'latitude':'Latitud','longitude':'Longitud','attributes':'Atributos','categories':'Tipo'},inplace=True)
restaurants_yelp = restaurants_yelp[['Id_Restaurant', 'Nombre', 'Ciudad', 'Estado', 'Cod_postal', 'Latitud',
                                    'Longitud','Tipo','Atributos']]

#Importamos los datasets de las reviews de yelp (ya hicimos la división del archivo grande)
for i in range(1,15):
    if i == 1:
        review = pd.read_json('yelp/'+str(i)+'.json',lines=True)                                            #Importamos
        review_filtro = review[review['business_id'].isin(restaurants_yelp['Id_Restaurant'].values)]        #Filtramos
        reviews_yelp = review_filtro
    else:
        review = pd.read_json('yelp/'+str(i)+'.json',lines=True)                                            #Importamos
        review_filtro = review[review['business_id'].isin(restaurants_yelp['Id_Restaurant'].values)]        #Filtramos
        reviews_yelp = pd.concat([reviews_yelp,review_filtro],ignore_index=True)                            #Concatenamos

#Descartamos los campos que no se utilizan, cambiamos nombre, dropeamos duplicados, reseteamos el indice 
reviews_yelp.drop(columns=['review_id','useful','funny','cool'],inplace=True)
reviews_yelp.rename(columns={'user_id':'Id_Usuario','business_id':'Id_Restaurant','stars':'Rating','text':'Reseña', 'date':'Fecha'},
               inplace=True)
reviews_yelp.drop_duplicates(subset=['Id_Usuario','Id_Restaurant','Rating','Reseña'],inplace=True)
reviews_yelp.reset_index(inplace=True,drop=True)

#Creamos dataframe con negocios que se encuentren duplicados. Es decir que tengan distinto Id (ya se descartó antes los de igual Id) pero coincidan nombre y ubicación.
duplicados_yelp = restaurants_yelp[restaurants_yelp.duplicated(subset=['Nombre','Cod_postal'],keep=False)].sort_values(by='Nombre')
duplicados_yelp.reset_index(inplace=True)

#Creamos dataframe con los negocios que son
negocios_duplicados_yelp = duplicados_yelp.drop_duplicates(subset=['Nombre','Cod_postal'])

#Tomamos los ids a conservar y los que se van a cambiar
lista_duplicados = []
for n in negocios_duplicados_yelp['Id_Restaurant'].values:
    aux = []
    nombre = negocios_duplicados_yelp[negocios_duplicados_yelp['Id_Restaurant']==n]['Nombre'].values[0]
    cod_postal = negocios_duplicados_yelp[negocios_duplicados_yelp['Id_Restaurant']==n]['Cod_postal'].values[0]
    for d in range(duplicados_yelp.shape[0]):
        if (duplicados_yelp['Nombre'][d] == nombre) and (duplicados_yelp['Cod_postal'][d] == cod_postal) and (duplicados_yelp['Id_Restaurant'][d] != n):
            aux.append(duplicados_yelp['Id_Restaurant'][d])
    lista_duplicados.append([n,aux])

duplicados_yelp_df = pd.DataFrame(data=lista_duplicados,columns=['Conservar','Cambiar'])        #Armamos dataframe

#Juntamos todos los ids que hay que modificar
ids_modificar = []
for i in range(duplicados_yelp_df.shape[0]):
    ids_modificar+=duplicados_yelp_df['Cambiar'][i]
ids_modificar

#Descartamos los duplicados en el dataframe de restaurants
restaurants_yelp.drop(index=restaurants_yelp[restaurants_yelp['Id_Restaurant'].isin(ids_modificar)].index,inplace=True)
restaurants_yelp.reset_index(inplace=True,drop=True)

reviews_yelp = cambioDeIndices(reviews_yelp,duplicados_yelp_df)         #Cambiamos ids en el dataframe de reviews


#Ahora cruzamos los datos de google y yelp
#Reducimos los dataframes así es más liviano el trabajo
google_id_nombre_postal = restaurants_google[['Id_Restaurant','Nombre','Cod_postal']]
yelp_id_nombre_postal = restaurants_yelp[['Id_Restaurant','Nombre','Cod_postal']]

#Juntamos los dataframes
merge = pd.merge(google_id_nombre_postal,yelp_id_nombre_postal,on=['Nombre','Cod_postal'])

#Descartamos los registros del dataset de yelp
indices_descarte = restaurants_yelp[restaurants_yelp['Id_Restaurant'].isin(merge['Id_Restaurant_y'].values)].index
restaurants_yelp.drop(index=indices_descarte,inplace=True)
restaurants_yelp.reset_index(inplace=True,drop=True)

#Armamos un solo dataframe de negocios
restaurants = pd.concat([restaurants_google,restaurants_yelp],ignore_index=True)

#Exportamos
restaurants.to_pickle('restaurants.pkl')

#Le quitamos las columnas de Nombre y código postal a merge para que sea mas liviano
merge.drop(columns=['Nombre','Cod_postal'],inplace=True)

#Hacemos el cambio de ids
reviews_yelp_merge = pd.merge(reviews_yelp,merge,how='left',left_on='Id_Restaurant',right_on='Id_Restaurant_y')
reviews_yelp_merge.rename(columns={'Id_Restaurant':'Id_Restaurant_orig'},inplace=True)
reviews_yelp_merge.rename(columns={'Id_Restaurant_x':'Id_Restaurant'},inplace=True)
reviews_yelp_merge.fillna(reviews_yelp,inplace=True)
reviews_yelp = reviews_yelp_merge[['Id_Usuario','Id_Restaurant','Rating','Reseña','Fecha']]

#Cambiamos el formato de la fecha a timestamp así coincide con el de las reviews de google
reviews_yelp['Timestamp'] = pd.to_datetime(reviews_yelp['Fecha']).astype(np.int64)
reviews_yelp.drop(columns='Fecha',inplace=True)

reviews = pd.concat([reviews_google,reviews_yelp],ignore_index=True)        #Armamos un único dataframe de reviews

#Exportamos en 8 datasets
N = 2000000
total_exp = 0
parte = 1
while total_exp < reviews.shape[0]:
    try:
        reviews.iloc[total_exp:total_exp+N].to_csv('reviews_finales/reviews_'+str(parte)+'.csv',index=False,sep=';',escapechar='\\')
        parte += 1
        total_exp += N
    except:
        reviews.iloc[total_exp:].to_csv('reviews_finales/reviews_'+str(parte)+'.csv',index=False,sep=';',escapechar='\\')
        total_exp += N
