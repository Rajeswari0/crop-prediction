# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 09:38:25 2025

@author: HP
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import pymysql

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "#Raje240103",
    "database": "crop_recommend_db"
}
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class model_input(BaseModel):
    
    N : float
    P : float
    K : float
    temperature : float
    humidity : float
    ph : float
    rainfall : float
    
    
# Load model, scaler, and label encoder
with open('crop_recommendation_rf_model_api.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    std = pickle.load(f)
with open('label_encoder_2.pkl', 'rb') as f:
    le = pickle.load(f)

x_columns = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Static and template folders
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Route to serve the form
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/crop_prediction')
def crop_pred(input_parameters: model_input):
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_parameters.model_dump()], columns=x_columns)
    # Scale input
    input_scaled = std.transform(input_df)
    # Predict
    prediction = model.predict(input_scaled)
    # Decode label
    predicted_crop = le.inverse_transform(prediction)[0]
    # Save to database
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO predictions
            (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            input_parameters.N,
            input_parameters.P,
            input_parameters.K,
            input_parameters.temperature,
            input_parameters.humidity,
            input_parameters.ph,
            input_parameters.rainfall,
            predicted_crop
        )
        cursor.execute(insert_query, values)
        connection.commit()
    except Exception as e:
        print("Database insertion error:", e)
    finally:
        cursor.close()
        connection.close()
    return {"recommended crop": predicted_crop} 