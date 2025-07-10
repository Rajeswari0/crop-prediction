# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 09:38:25 2025

@author: HP
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd

from sqlmodel import SQLModel, Field, create_engine, select, Session
from typing import Optional
from datetime import datetime

from contextlib import asynccontextmanager
import os



DATABASE_URL = "sqlite:///temperature_data.db"  # Use PostgreSQL later
engine = create_engine(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # auto-create table
    yield

app = FastAPI( lifespan=lifespan)

origins = [
    "http://127.0.0.1:8000",  # your local frontend
    "http://localhost:8000",
    "https://crop-prediction-1-t1e1.onrender.com"  # if frontend is also hosted here
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



class SensorPrediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    temperature: float
    humidity: float
    predicted_crop: str
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BasicSensor(BaseModel):
    temperature: float
    humidity: float

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

# Route to serve the form
#@app.get("/", response_class=HTMLResponse)
#def home(request: Request):
    #return templates.TemplateResponse("index.html", {"request": request})


#@app.post('/crop_prediction')
#def crop_pred(input_parameters: model_input):
    # Convert input to DataFrame
    #input_df = pd.DataFrame([input_parameters.model_dump()], columns=x_columns)
    # Scale input
    #input_scaled = std.transform(input_df)
    # Predict
    #prediction = model.predict(input_scaled)
    # Decode label
    #predicted_crop = le.inverse_transform(prediction)
    #return {"recommended crop": predicted_crop[0]}



@app.post("/sensor_data")
def receive_sensor_data(sensor: BasicSensor):
    log = SensorPrediction(
        temperature=sensor.temperature,
        humidity=sensor.humidity,
        predicted_crop="--"  # placeholder, not predicted yet
    )
    with Session(engine) as session:
        session.add(log)
        session.commit()
    return {"message": "Sensor data stored", "id": log.id}


@app.post("/upload")
def sensor_upload(data: SensorInput):
    df = pd.DataFrame([data.model_dump()], columns=x_columns)
    # Scale the input data
    scaled = std.transform(df)   
    # Predict the crop using the model
    prediction = model.predict(scaled)
    # Decode the predicted crop label
    predicted_crop = le.inverse_transform(prediction)[0]

    log = SensorPrediction(
        temperature=data.temperature,
        humidity=data.humidity,
        predicted_crop=predicted_crop
    )

    with Session(engine) as session:
        session.add(log)
        session.commit()
        return {"crop": predicted_crop, "id": log.id}
    
@app.get("/latest_sensor_data")
def latest_sensor():
    with Session(engine) as session:
        record = session.exec(
            select(SensorPrediction).order_by(SensorPrediction.timestamp.desc())
        ).first()
        if record:
            return {
                "id": record.id,
                "temperature": record.temperature,
                "humidity": record.humidity,
                "crop": record.predicted_crop
            }
        else:
            return {
                "id": None,
                "temperature": 0,
                "humidity": 0,
                "crop": "--"
            }

    
@app.get("/export/sensor-data", response_class=FileResponse)
def export_sensor_data(format: str = "csv"):
    with Session(engine) as session:
        records = session.exec(select(SensorPrediction)).all()

    if not records:
        return {"message": "No sensor data available to export."}

    # Convert SQLModel objects to list of dicts for DataFrame
    df = pd.DataFrame([r.model_dump() for r in records])

    filename = f"sensor_data_export.{format}"

    if format == "csv":
        df.to_csv(filename, index=False)
    elif format == "xlsx":
        try:
            import openpyxl
            df.to_excel(filename, index=False)
        except ImportError:
            return {"error": "Install openpyxl to export as Excel."}
    else:
        return {"error": "Format must be either 'csv' or 'xlsx'."}

    return FileResponse(path=filename, filename=filename, media_type="application/octet-stream")



