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

from sqlmodel import SQLModel, Field, create_engine, select, Session
from typing import Optional, ClassVar
from datetime import datetime, timezone

from contextlib import asynccontextmanager
import os

API_KEY = "1606api"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


DATABASE_URL = "mysql+pymysql://root:#Raje240103@localhost/crop_predict_db" 
engine = create_engine(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # auto-create table
    yield

app = FastAPI( lifespan=lifespan)

origins = [
    "http://127.0.0.1:8000",  
    "http://localhost:8000",
    "https://crop-prediction-1-t1e1.onrender.com" 
]


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
    __tablename__: ClassVar[str] = "sensorprediction"
    id: Optional[int] = Field(default=None, primary_key=True)
    N: Optional[float] = None
    P: Optional[float] = None
    K: Optional[float] = None
    temperature: float
    humidity: float
    ph: Optional[float] = None
    rainfall: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_temp: Optional[float] = None
    tds: Optional[float] = None 
    predicted_crop: str
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    log = SensorPrediction(
        temperature=sensor.temperature,
        humidity=sensor.humidity,
        soil_moisture=sensor.soil_moisture,
        soil_temp = sensor.soil_temp,
        tds = sensor.tds, 
        predicted_crop="--"
    )
    with Session(engine) as session:
        session.add(log)
        session.commit()
        log_id = log.id  # Access ID before session closes
    return {"message": "Sensor data stored", "id": log_id}



@app.post("/upload")
def sensor_upload(data: SensorInput, _: str = Depends(verify_api_key)):
    df = pd.DataFrame([data.model_dump()], columns=x_columns)
    # Scale the input data
    scaled = std.transform(df)   
    # Predict the crop using the model
    prediction = model.predict(scaled)
    # Decode the predicted crop label
    predicted_crop = le.inverse_transform(prediction)[0]
   
    with Session(engine) as session:
        latest_record = session.exec(
            select(SensorPrediction)
            .where(SensorPrediction.soil_moisture != None)
            .order_by(SensorPrediction.timestamp.desc())
        ).first()

        log = SensorPrediction(
            N=data.N,
            P=data.P,
            K=data.K,
            temperature=data.temperature,
            humidity=data.humidity,
            ph=data.ph,
            rainfall=data.rainfall,
            soil_moisture=latest_record.soil_moisture if latest_record else None,
            soil_temp=latest_record.soil_temp if latest_record else None,
            tds=latest_record.tds if latest_record else None,
            predicted_crop=predicted_crop
    )

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
                "soil_moisture": record.soil_moisture,
                "soil_temp": record.soil_temp,
                "tds": record.tds,
                "ph": record.ph,
                "rainfall": record.rainfall,
                "N": record.N,
                "P": record.P,
                "K": record.K,
                "crop": record.predicted_crop
            }
        else:
            return {
                "id": None,
                "temperature": 0,
                "humidity": 0,
                "soil_moisture": None,
                "soil_temp": None,
                "tds": None,
                "crop": "--"
            }

    
@app.get("/export/sensor-data", response_class=FileResponse)
def export_sensor_data(format: str = "csv", _: str = Depends(verify_api_key)):
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