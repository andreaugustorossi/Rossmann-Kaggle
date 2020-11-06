import requests
import json
import pandas as pd
from flask import Flask, request, Response

# Constants
TOKEN = "1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4"

# Bot Info
https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/getMe

# Get Updates
https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/getUpdates

# Send Message
https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/sendMessage?chat_id=1269100792&text=Hi André, I am fine!

def send_message ( chat_id, text ): 
    url = 'https://api.telegram.org/bot{}/'.format( TOKEN )
    url = url + 'sendMessage?chat_id={}'.format( chat_id )

    r = requests.post( url, json={'text':text } ) 
    print( 'Status Code {}'.format( r.status_code ) )

    return None


def load_dataset( store_id ):
    # loading test dataset
    df_store_raw = pd.read_csv( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\store.csv', sep=',', low_memory = False )
    df10 = pd.read_csv( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\test.csv' )

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id ]

    # remove closed days
    df_test = df_test[df_test['Open'] != 0]
    df_test = df_test[~df_test['Open'].isnull()]
    df_test = df_test.drop( 'Id', axis=1 )

    # convert Dataframe to json
    data = json.dumps( df_test.to_dict( orient='records' ) )

    return data

def predict( data ):

    # API Call
    url = 'https://rossmann-prediction.herokuapp.com/rossmann/predict'
    header = {'Content-type': 'application/json' } 
    data = data

    r = requests.post( url, data = data, headers = header )
    print( 'Status Code {}'.format( r.status_code ) )

    # Json to dataframe
    d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys() )

    return d1


def parse_message( message ):
    chat_id = message['message']['chat']['id']    
    store_id = message['message']['text']    

    return chat_id, store_id



# API Initialize
app = Flask( __name__ ) 

@app.route( '/', methods = [ 'GET', 'POST' ]
def index():
    if request.method == 'POST': 
       message = requests.get_json() 
           
       chat_id, store_id = parse_message( message ) 


    else:
       return '<h1> Rossmann Telegram BOT <h1>' 



if __name__ == "__main__':
    app.run( host = '0.0.0.0', port = 5000 )

# Predictions by store
#d2 = d1[['store', 'prediction']].groupby( 'store' ).sum().reset_index()

#for i in range( len( d2 ) ):
#    print( 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format( 
#            d2.loc[i, 'store'], 
#            d2.loc[i, 'prediction'] ) )