# set FLASK_APP=flask_app.app.py
from flask import Flask, request, render_template, jsonify, flash, redirect
import pandas as pd 
#from flask_pymongo import PyMongo
import pymongo
from fbprophet import Prophet
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

def create_app():
    app = Flask(__name__)
    mongo = pymongo.MongoClient(MONGO_URI, maxPoolSize=50, connect=False)
    db = pymongo.database.Database(mongo, 'citydata')
    col = pymongo.collection.Collection(db, 'alldata')
    CORS(app)

    @app.route('/')
    def root():
        return 'add city id to url'

    @app.route("/<id>")
    def forecast(id=None):
        doc = col.find_one({'_id':int(id)})
        key = 'Predictions'
        if doc is None:
            return jsonify({"message": "City Not Found!"})
        elif key in doc['Historical Property Value Data'] or doc['Total Population'] < 50000:
            return jsonify(doc)
        else:
            try:
                doc = col.find_one({'_id':int(id)})
                df = pd.DataFrame.from_dict(doc['Historical Property Value Data']['Average Home Value'], orient='index')
                df = df.reset_index()
                df = df.rename(columns={'index': 'ds', 0:'y'})
                df['ds'] = df['ds'] + '-01'
                df = df.dropna()
                m = Prophet(seasonality_mode='multiplicative').fit(df)
                future = m.make_future_dataframe(periods=60, freq='M')
                future = future[future['ds']>'2019-11-01']
                fcst = m.predict(future)
                y_pred = fcst[['ds','yhat','yhat_lower','yhat_upper']]
                y_pred['ds'] = y_pred['ds'].dt.strftime('%Y-%m')
                y_pred['ds'] = y_pred['ds'].drop_duplicates()
                y_pred = y_pred.dropna()
                y_pred = y_pred.set_index('ds')
                # y_pred = y_pred.to_dict('index')
                # for key in y_pred:
                #     y_pred[key] = y_pred[key]['yhat']
                # y_pred = {'AVG Home Value': y_pred}
                #y_pred = y_pred.to_json(orient='records')
                for index, row in y_pred.iterrows():
                    col.update_one({ '_id':int(id) }, {'$set': {"Historical Property Value Data.Predictions."+str(index): float(row['yhat'])}})
                    col.update_one({ '_id':int(id) }, {'$set': {"Historical Property Value Data.Lower_Predictions."+str(index): float(row['yhat_lower'])}}) 
                    col.update_one({ '_id':int(id) }, {'$set': {"Historical Property Value Data.Upper_Predictions."+str(index): float(row['yhat_upper'])}})
                doc = col.find_one({'_id':int(id)})
                return jsonify(doc)
            except:
                return jsonify({"message": "City Not Found!"})  


    return app

    