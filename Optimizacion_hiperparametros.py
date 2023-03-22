from surprise import Dataset, Reader, SVD
from surprise.model_selection.search import RandomizedSearchCV
import pandas as pd
import numpy as np

#Importamos los datasets
df = pd.concat([pd.read_csv('https://drive.google.com/uc?id=1i01lRA5-qE_TuHddX9R8p_Ep8Kh_LRg0',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1BqYKyadkyhsn--XqDIhAmNtr_ler_Xs-',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1uYFcpQicu2mulLOqeqNzXI-ACNvTfUg7',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1HAapXHu9H7iPTuzqdha156amGSCffg9V',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1_haWCUFpcOVAa9X2rQMNKbT9fKfFDEIq',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1lAEp526h2hb_gXBmMIRRnpm1HnH96eZO',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1ZpCswmdhDRfdVmnxzJ74_LEjTQiwPXZN',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1OI07OXwtbwOX9DFOmUA_s8x3dW8JYYw_',sep=';'),
                pd.read_csv('https://drive.google.com/uc?id=1wQzrlGIUMu7KW1q4KmTSgD0QDOadXZuS',sep=';')],ignore_index=True)

#Crea un objeto Reader y Dataset de Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[["Id_Usuario", "Id_Restaurant", "Rating"]], reader)

#Optimizamos hiperparámetros. Primero vamos a hacerlo con el SVD.
parametros = {'n_factors':np.arange(10,1000),
             'n_epochs':np.arange(5,50),
             'lr_all':np.arange(0.001,0.05,0.001),
             'reg_all':np.arange(0.005,0.1,0.005)}

rs = RandomizedSearchCV(SVD,param_distributions=parametros,cv=3,n_iter=30,n_jobs=-1,random_state =42)
rs.fit(data)

#Pasamos a dataframe
results_df = pd.DataFrame(rs.cv_results)

#Tomamos solo las columnas que nos interesan.
resultados = results_df[['param_n_factors','param_n_epochs','param_lr_all',
                         'param_reg_all','mean_test_rmse']].sort_values(by='mean_test_rmse')

#Exportamos
resultados.to_csv('optimizacion_hiperparametros.csv',index=False)