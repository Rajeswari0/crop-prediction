# CROP RECOMMENDATI0N SYSTEM
A machine learning based web application which recommends the best suitable crop to grow based on the given input parameters.
## FEATURES
   - prediction of crop based on user input
   - web interface
   - FastAPI backend
   - RF trained ml model
   - Real-time feedback with loading indicator

## TECHNOLOGIES
   - FRONTEND: HTML, CSS, JavaScript
   - BACKEND: Python + FastAPI
   - ML MODEL: trained with Scikit-learn using Random Forest
   - DATABASE: MySQL
   - DEPLOYMENT: local server

## HOW TO RUN LOCALLY

1. Install dependencies:

   pip install -r requirements.txt

2. Start FastAPI backend:

   uvicorn main:app --reload

3. open browser and go to:

   http://127.0.0.1:8000

4. DATABASE SETUP (MySQL)

   create database crop_recommend_db;
   use crop_recommend_db;
   create table predictions(
   id INT AUTO_INCREMENT PRIMARY KEY,
       N FLOAT,
      P FLOAT,
      K FLOAT,
      temperature FLOAT,
      humidity FLOAT,
      ph FLOAT,
      rainfall FLOAT,
      predicted_crop VARCHAR(100),
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   select * from predictions;

## Project Folder Tips
crop prediction/
|- main.py
|-model.pkl
|-templates/
   |-index.html
|-static/
   |-style.css
   |-script.js
|-requirements.txt
|-README.md

## Notes
. Make sure your MySQL server is running locally
. Replace MySQL connection values in main.py with your own (user, password, host).


Main branch contains the stable version
Additional experimental features (e.g., live sensor data logging) are in development in other branches.