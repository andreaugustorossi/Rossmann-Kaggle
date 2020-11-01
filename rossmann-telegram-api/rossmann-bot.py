import os
import requests
import json
import pandas   as pd
from flask      import Flask, request, Response

# loading test dataset
df_store_raw = pd.read_csv( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\store.csv', sep=',', low_memory = False )
df10 = pd.read_csv( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\test.csv' )

# merge test dataset + store
df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

# choose store for prediction
df_test = df_test[df_test['Store'].isin( [20, 23, 22] )]

# remove closed days
df_test = df_test[df_test['Open'] != 0]
df_test = df_test[~df_test['Open'].isnull()]
df_test = df_test.drop( 'Id', axis=1 )

# convert Dataframe to json
data = json.dumps( df_test.to_dict( orient='records' ) )

# API Call
url = 'https://rossmann-prediction.herokuapp.com/rossmann/predict'
header = {'Content-type': 'application/json' } 
data = data

r = requests.post( url, data = data, headers = header )
print( 'Status Code {}'.format( r.status_code ) )

# Json to dataframe
d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys() )

# Predictions by store
d2 = d1[['store', 'prediction']].groupby( 'store' ).sum().reset_index()

for i in range( len( d2 ) ):
    print( 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format( 
            d2.loc[i, 'store'], 
            d2.loc[i, 'prediction'] ) )