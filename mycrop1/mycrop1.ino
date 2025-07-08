#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"
//#include <OneWire.h>
//#include <DallasTemperature.h>

#define DHTPIN 27
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

//#define ONE_WIRE_BUS 15
//OneWire oneWire(ONE_WIRE_BUS);
//DallasTemperature sensors(&oneWire);

//#define SOIL_MOISTURE_PIN 34
//#define GAS_SENSOR_PIN 35
//#define TDS_SENSOR_PIN 32

//WiFi credentials
const char* ssid = "Galaxy M53 5G";
const char* password = "gkbu2351";
const char* serverURL = "https://crop-prediction-feue.onrender.com/crop_prediction";


void setup() {
  // put your setup code here, to run once:
 Serial.begin(115200);
 WiFi.begin(ssid,password);

 //connect to wifi
  while(WiFi.status() !=WL_CONNECTED){
   delay(1000);
   Serial.println("Connecting to WiFi.....");
  }
  Serial.println("Connected to WiFi!!!");
  dht.begin();
  //sensors.begin();


}

void loop() {
  // put your main code here, to run repeatedly:
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  //int asoilMoisture = analogRead(34);
  //int agasValue = analogRead(35);
  //int aTDS = analogRead() 

  //sensors.requestTemperatures();
  //float soilTemp = sensors.getTempCByIndex(0);
  Serial.print("Temperature in * C: ");
  Serial.println(temperature);
  Serial.print("Humidity: ");
  Serial.println(humidity);
 

  if(WiFi.status() == WL_CONNECTED){
    if (!isnan(temperature) && !isnan(humidity)) {
     HTTPClient http;
     http.begin(serverURL);
     http.addHeader("Content-Type","application/json");

     String json = "{";
     json +="\"Temperature\":" + String(temperature, 2) + ",";
     json +="\"Humidity\":" + String(humidity, 2) + ",";
     //json +="\"Soil Moisture\":" + String(soilMoisture, 2) + ",";
     //json +="\"Soil Temperature\":" + String(soilTemp, 2) + ",";
     //json +="\"Gas level\":" + String(gasValue, 2) + ",";
     //json +="\"tds\":" + String(tds,2);
     json +="}";
  

     int code = http.POST(json);
     Serial.print("Status code: ");
     Serial.println(code);
     http.end();
    }
  }
  delay(5000);
}

