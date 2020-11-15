import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import telegram
import os
from io import BytesIO
from flask import Flask, request, Response

# Constants
TOKEN = '1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4'
bot = telegram.Bot(token=TOKEN)

# Bot Info
#https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/getMe

# Get Updates
#https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/getUpdates

# Webhook
#https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/setWebhook?url=https://arros-33d824ec.localhost.run

# Send Message
#https://api.telegram.org/bot1389763704:AAELP5r6P2S8AH410pYZOZZKw_hdIoQq5M4/sendMessage?chat_id=1269100792&text=Hi André, I am fine!

def send_message ( chat_id, text ): 
    url = 'https://api.telegram.org/bot{}/'.format( TOKEN )
    url = url + 'sendMessage?chat_id={}'.format( chat_id )

    r = requests.post( url, json={'text':text } ) 
    print( 'Status Code {}'.format( r.status_code ) )

    return None


def load_dataset( store_id ):
    # loading test dataset
    df_store_raw = pd.read_csv( 'store.csv', sep=',', low_memory = False )
    df10 = pd.read_csv( 'test.csv' )

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id ]

    if not df_test.empty:
        # remove closed days
        df_test = df_test[df_test['Open'] != 0]
        df_test = df_test[~df_test['Open'].isnull()]
        df_test = df_test.drop( 'Id', axis=1 )

        # convert Dataframe to json
        data = json.dumps( df_test.to_dict( orient='records' ) )

    else:
        data = 'error'

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

    store_id.replace( '/', '' )

    try:
        store_id = int( store_id )

    except ValueError: 
        store_id = 'error'

    return chat_id, store_id



# API Initialize
app = Flask( __name__ ) 

@app.route( '/', methods=['GET', 'POST'] )
def index():
    if request.method == 'POST':
        message = request.get_json()

        chat_id, store_id = parse_message( message )

        if store_id != 'error':
            # loading data
            data = load_dataset( store_id )

            if data != 'error':
                # prediction
                d1 = predict( data )

                # calculation
                d2 = d1[['store', 'prediction']].groupby( 'store' ).sum().reset_index()
                
                # Send Lineplot
                fig = plt.figure()
                sns.lineplot(x = 'week_of_year', y = 'prediction', data = d1)
                sns.set_style('whitegrid')
                plt.title('Weekly Sales Forecast for Store {}'.format(d2['store'].values[0]))
                plt.xlabel('Week of Year (starting from week 31 - July 19th)')
                plt.ylabel('Sales Prediction (US$)')
                buffer = BytesIO()
                fig.savefig(buffer, format='png')
                buffer.seek(0)
                bot.send_photo(chat_id=chat_id, photo=buffer)

                # send message
                msg = 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format(
                            d2['store'].values[0],
                            d2['prediction'].values[0] ) 

                send_message(chat_id, msg)
                return Response('OK', status=200)

            else:
                send_message(chat_id, 'Store number is not available')
                return Response('OK', status=200)

        else:
            send_message(chat_id, 'This is not a store number')
            return Response('OK', status=200)

    else:
        return '<h1>Rossmann Telegram BOT</h1>'

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)