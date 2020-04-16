# set FLASK_APP=flask_app.app.py
from flask import Flask, request, render_template, jsonify, flash, redirect
import pandas as pd 
#from flask_pymongo import PyMongo
import pymongo
from fbprophet import Prophet
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

def create_app():
    app = Flask(__name__)
    mongo = pymongo.MongoClient(MONGO_URI, maxPoolSize=50, connect=False)
    db = pymongo.database.Database(mongo, 'citydata')
    col = pymongo.collection.Collection(db, 'alldata')

    @app.route('/')
    def root():
        return 'add city id to url'

    @app.route("/<id>")
    def forecast(id=None):
        try:   
            doc = col.find_one({'_id':int(id)})
            df = pd.DataFrame.from_dict(doc['Historical Property Value Data']['Average Home Value'], orient='index')
            df = df.reset_index()
            df = df.rename(columns={'index': 'ds', 0:'y'})
            df['ds'] = df['ds'] + '-01'
            df = df.dropna()
            m = Prophet(seasonality_mode='multiplicative').fit(df)
            future = m.make_future_dataframe(periods=24, freq='M')
            fcst = m.predict(future)
            y_pred = fcst[['ds','yhat']]
            y_pred = y_pred.to_json(orient='records')
            return y_pred
        except:
            return jsonify({"message": "City Not Found!"})  


    return app

    