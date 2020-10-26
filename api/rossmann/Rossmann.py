import pickle
import inflection
import pandas as pd
import numpy as np
import math
import datetime


class Rossmann ( object ):
    def __init__( self ):
        self.rescaling_competition_distance      = pickle.load( open( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\parameters\rescaling_competition_distance.pkl', 'rb' ) )
        self.rescaling_competition_time_month    = pickle.load( open( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\parameters\rescaling_competition_time_month.pkl', 'rb' ) )
        self.rescaling_promo_time_week           = pickle.load( open( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\parameters\rescaling_promo_time_week.pkl', 'rb' ) )
        self.rescaling_year                      = pickle.load( open( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\parameters\rescaling_year.pkl', 'rb' ) )
        self.encoding_store_type                 = pickle.load( open( r'C:\Users\arros\OneDrive\ciencia_de_dados\data_science_em_producao\Rossmann-Kaggle\parameters\encoding_store_type.pkl', 'rb' ) )

        
    def data_cleaning( self, df1 ):

        # Rename columns into Snake Case
        cols_old = [ 'Store', 'DayOfWeek', 'Date', 'Open', 'Promo', 'StateHoliday', 
                     'SchoolHoliday', 'StoreType', 'Assortment', 'CompetitionDistance','CompetitionOpenSinceMonth',
                     'CompetitionOpenSinceYear', 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval' ]
    
        snakecase = lambda x: inflection.underscore (x)
        cols_new = list( map( snakecase, cols_old ) )
    
        # Rename
        df1.columns = cols_new
    
        # Date column to date format
        df1 ['date'] = pd.to_datetime(df1['date'])
        df1.dtypes
     
        # Fill out NA´s
        # Assuming NA´s in competition_distance are stores too far away (200.000,00) - Business Question
        df1['competition_distance'] = df1['competition_distance'].apply(lambda x: 200000.0 if math.isnan(x) else x)
        
        # Assuming NA´s in competition_open_since_month can be the same as the date of the date column (future review CRISP-DS)    
        df1['competition_open_since_month'] = df1.apply(lambda x: x['date'].month if math.isnan(x['competition_open_since_month']) else x['competition_open_since_month'], axis = 1)
        
        # Assuming NA´s in competition_open_since_year can be the same as the date of the date column and higher than 2000 (future review CRISP-DS)
        df1['competition_open_since_year'] = df1.apply(lambda x: x['date'].year if math.isnan(x['competition_open_since_year']) else x['competition_open_since_year'], axis = 1)
        df1['competition_open_since_year'] = df1['competition_open_since_year'].apply(lambda x: 2000.0 if x < 2000.0 else x)
        
        # Assuming NA´s in promo2_since_week can be the same as the date of the date column (future review CRISP-DS)
        df1['promo2_since_week'] = df1.apply(lambda x: x['date'].week if math.isnan(x['promo2_since_week']) else x['promo2_since_week'], axis = 1)
        
        # Assuming NA´s in promo2_since_year can be the same as the date of the date column (future review CRISP-DS)                
        df1['promo2_since_year'] = df1.apply(lambda x: x['date'].year if math.isnan(x['promo2_since_year']) else x['promo2_since_year'], axis = 1)
        
        # Assuming NA´s in promo_interval can be compared to a list and then substitute them for 0 or 1
        # List to compare
        month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec' }
        
        # Fill NA´s with 0
        df1['promo_interval'].fillna(0, inplace=True)
        
        # Creating a new column month_map maping with date column and the list month_map (numbers will be subtitute for strings)                         
        df1['month_map'] = df1['date'].dt.month.map(month_map)
                                            
        # Creating a new column is_promo comparing promo_interval with month_map and returnig 0 or 1    
        df1['is_promo'] = df1[['promo_interval', 'month_map']].apply(lambda x: 0 if x['promo_interval'] == 0 else 1 if x['month_map'] in x['promo_interval'].split(',') else 0, axis=1)                                     
        
     
        # Change Types
        # Competition and promo2 as interger
        df1['competition_open_since_month'] = df1['competition_open_since_month'].astype ( int ) 
        df1['competition_open_since_year'] = df1['competition_open_since_year'].astype ( int ) 
        df1['promo2_since_week'] = df1['promo2_since_week'].astype ( int )
        df1['promo2_since_year'] = df1['promo2_since_year'].astype ( int )
        
        return df1

    def feature_engineering( self, df2 ):
        
        # year
        df2[ 'year' ] = df2[ 'date' ].dt.year

        # month
        df2[ 'month' ] = df2[ 'date' ].dt.month

        # day
        df2[ 'day' ] = df2[ 'date' ].dt.day

        # week of year
        df2[ 'week_of_year' ] = df2[ 'date' ].dt.weekofyear

        # year week
        df2[ 'year_week' ] = df2[ 'date' ].dt.strftime( '%Y-%W' )

        # competition since
        df2[ 'competition_since' ] = df2.apply( lambda x: datetime.datetime( year=x[ 'competition_open_since_year' ], month=x[ 'competition_open_since_month' ],day=1 ), axis=1 )

        df2[ 'competition_time_month' ] = ( ( df2[ 'date' ] - df2[ 'competition_since' ] )/30 ).apply( lambda x: x.days ).astype( int )

        # promo since
        df2[ 'promo_since' ] = df2[ 'promo2_since_year' ].astype( str ) + '-' + df2[ 'promo2_since_week' ].astype( str )

        df2[ 'promo_since' ] = df2[ 'promo_since' ].apply( lambda x: datetime.datetime.strptime( x + '-1', '%Y-%W-%w' ) - datetime.timedelta( days=7 ) )

        df2[ 'promo_time_week' ] = ( ( df2[ 'date' ] - df2[ 'promo_since' ] )/7 ).apply( lambda x: x.days ).astype( int )

        # assortment
        df2[ 'assortment' ] = df2[ 'assortment' ].apply( lambda x: 'basic' if x == 'a' else 'extra' if x == 'b' else 'extended' )

        # state holiday
        df2[ 'state_holiday' ] = df2[ 'state_holiday' ].apply( lambda x: 'public_holiday' if x == 'a' else 'easter_holiday' if x == 'b' else 'christmas' if x == 'c' else 'regular_day' )

        # Variable Selection
        # Line Filtering
        # The stores should be open and sales should be higher than 0
        df2 = df2[ df2[ 'open' ] != 0 ]

        # Column Filtering
        cols_drop = [ 'open', 'promo_interval', 'month_map' ]
        df2 = df2.drop( cols_drop, axis=1 )
        
        return df2

    
    def data_preparation ( self, df5 ):

        # Rescaling
        # competition distance
        df5['competition_distance'] = self.rescaling_competition_distance.fit_transform( df5[['competition_distance']].values )

        # competition time month
        df5['competition_time_month'] = self.competition_time_month.fit_transform( df5[['competition_time_month']].values )

        # promo time week
        df5['promo_time_week'] = self.promo_time_week.fit_transform( df5[['promo_time_week']].values )

        # year
        df5['year'] = self.year.fit_transform( df5[['year']].values )

        # Transform
        # Encoding
        # state_holiday - One Hot Encoding
        df5 = pd.get_dummies( df5, prefix=['state_holiday'], columns=['state_holiday'] )

        # store_type - Label Encoding
        df5['store_type'] = self.enconding_store_type.fit_transform( df5['store_type'] )

        # assortment - Ordinal Encoding
        assortment_dict = {'basic': 1,  'extra': 2, 'extended': 3}
        df5['assortment'] = df5['assortment'].map( assortment_dict )

        # Nature Transformation
        # day of week
        df5['day_of_week_sin'] = df5['day_of_week'].apply( lambda x: np.sin( x * ( 2. * np.pi/7 ) ) )
        df5['day_of_week_cos'] = df5['day_of_week'].apply( lambda x: np.cos( x * ( 2. * np.pi/7 ) ) )

        # month
        df5['month_sin'] = df5['month'].apply( lambda x: np.sin( x * ( 2. * np.pi/12 ) ) )
        df5['month_cos'] = df5['month'].apply( lambda x: np.cos( x * ( 2. * np.pi/12 ) ) )

        # day 
        df5['day_sin'] = df5['day'].apply( lambda x: np.sin( x * ( 2. * np.pi/30 ) ) )
        df5['day_cos'] = df5['day'].apply( lambda x: np.cos( x * ( 2. * np.pi/30 ) ) )

        # week of year
        df5['week_of_year_sin'] = df5['week_of_year'].apply( lambda x: np.sin( x * ( 2. * np.pi/52 ) ) )
        df5['week_of_year_cos'] = df5['week_of_year'].apply( lambda x: np.cos( x * ( 2. * np.pi/52 ) ) )
        
        cols_selected = [ 'store', 'promo', 'store_type', 'assortment', 'competition_distance', 'competition_open_since_month',
                          'competition_open_since_year', 'promo2', 'promo2_since_week', 'promo2_since_year', 'competition_time_month', 'promo_time_week',
                          'day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos', 'day_sin', 'day_cos', 'week_of_year_sin', 'week_of_year_cos']
        
        return df5[ cols_selected ]
    
    def get_prediction( self, model, original_data, test_data ):
        
        # Prediction
        pred = model.predict( test_data )
        
        # Join pred into the original data
        original_data['prediction'] = np.expm1( pred )
        
        return original_data.to_json( orient='records', date_format='iso' )