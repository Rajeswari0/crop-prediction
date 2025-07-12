# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 09:38:25 2025

@author: HP
"""

from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
from typing import Optional

import os

API_KEY = "1606api"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


app = FastAPI()
origins = [
    "http://127.0.0.1:8000",  # local frontend
    "http://localhost:8000",
    "https://crop-prediction-1-t1e1.onrender.com" #deployed frontend  
]

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use specific origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and template folders
base_dir = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Load model, scaler, and label encoder
with open('crop_recommendation_rf_model_api.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    std = pickle.load(f)
with open('label_encoder_2.pkl', 'rb') as f:
    le = pickle.load(f)

x_columns = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]



class BasicSensor(BaseModel):
    temperature: float
    humidity: float
    soil_moisture: Optional[float] = None
    soil_temp: Optional[float] = None
    tds: Optional[float] = None 

class SensorInput(BaseModel):
    N: float
    P: float
    K: float
    ph: float
    rainfall: float
    temperature: float
    humidity: float

    
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/sensor_data")
def receive_sensor_data(sensor: BasicSensor, _: str = Depends(verify_api_key)):
    return {"message": "Sensor data recieved", "data": sensor.model_dump()}



@app.post("/upload")
def sensor_upload(data: SensorInput, _: str = Depends(verify_api_key)):
    df = pd.DataFrame([data.model_dump()], columns=x_columns)
    # Scale the input data
    scaled = std.transform(df)   
    # Predict the crop using the model
    prediction = model.predict(scaled)
    # Decode the predicted crop label
    predicted_crop = le.inverse_transform(prediction)[0]
   
    return {"crop": predicted_crop}
    

