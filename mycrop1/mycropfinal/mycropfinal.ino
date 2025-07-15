#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>

//OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//DHT
#define DHTPIN 26
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

//soil temperature
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// TDS
#define TDS_PIN 34
#define VREF 3.3
#define ADC_RES 4095
float calibration_factor = 0.5;
float TEMP = 25.0;


#define SOIL_MOISTURE_PIN 32

//WiFi credentials
const char* ssid = "Galaxy M53 5G";
const char* password = "gkbu2351";
const char* serverURL = "https://crop-prediction-1-t1e1.onrender.com/sensor_data";
const char* apiKey = "1606api";

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
  sensors.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
  Serial.println("OLED init failed");
  while (true);
  }

  display.clearDisplay();
  display.setTextSize(0.5);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

}

void loop() {
  // put your main code here, to run repeatedly:

  //dht input
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  //soil moiosture input
  int asoilMoisture = analogRead(32);
  float soilMoisture = map(asoilMoisture, 0, 3580, 100, 0);
  
  //soil temperature input
  sensors.requestTemperatures();
  float soilTemp = sensors.getTempCByIndex(0);

  //tds input
  int tdsRaw = 0;
  for (int i = 0; i < 10; i++) {
   tdsRaw += analogRead(TDS_PIN);
   delay(10);
  }
  tdsRaw /= 10;
  float voltage = tdsRaw * (VREF / ADC_RES);
  float tds = (voltage * calibration_factor) * 1000;
  float tdsComp = tds / (1.0 + 0.02 * (soilTemp - 25.0));

  Serial.print("Temperature : ");
  Serial.print(temperature);
  Serial.println("  *C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println("  %");

  Serial.print("Soil Temperature: ");
  Serial.print(soilTemp);
  Serial.println("  *C");  

  Serial.print("Soil Moisture (Dryness %): ");
  Serial.print(soilMoisture);
  Serial.println("  %");

  Serial.print("TDS (ppm): ");
  Serial.println(tdsComp);

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("TEMPERATURE: ");display.print(temperature);display.println(" *C");
  display.print("HUMIDITY: ");display.print(humidity);display.println(" %");
  display.print("TDS:");display.print(tdsComp);display.println(" ppm");
  display.print("STEMPERATURE: ");display.print(soilTemp);display.println("*C");
  display.print("SOIL DRY %: ");display.println(soilMoisture);
  display.display();



  if(WiFi.status() == WL_CONNECTED){
    if (!isnan(temperature) && !isnan(humidity) && !isnan(soilMoisture) && !isnan(soilTemp) && !isnan(tdsComp)) {
     HTTPClient http;
     http.begin(String(serverURL));
     http.addHeader("Content-Type","application/json");
     http.addHeader("x-api-key", apiKey);

     String json = "{";
     json +="\"temperature\":" + String(temperature, 2) + ",";
     json +="\"humidity\":" + String(humidity, 2) + ",";
     json +="\"soil_moisture\":" + String(soilMoisture, 2) + ",";
     json +="\"soil_temp\":" + String(soilTemp, 2) + ",";
     json +="\"tds\":" + String(tdsComp, 2);
     json +="}";
  
     Serial.println("Sending JSON: " + json);


     int code = http.POST(json);
     Serial.print("Status code: ");
     Serial.println(code);

     String response = http.getString();
     Serial.println("Server Response: ");
     Serial.println(response);
     Serial.println("---------------");

     http.end();
    }
  }
  delay(10000);
}

