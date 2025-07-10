document.addEventListener("DOMContentLoaded", () => {
 let latestId = null;

 const BASE_URL = location.hostname === "localhost" || location.hostname === "127.0.0.1"? "http://127.0.0.1:8000": "https://crop-prediction-1-t1e1.onrender.com";

 const setText = (id, value) => {
   const element = document.getElementById(id);
    if (element) {
    element.innerText = value;
    }
  };

 async function fetchLiveSensor() {
  
   try {
    const res = await fetch(`${BASE_URL}/latest_sensor_data`);

    const data = await res.json();
    
    setText("live-temp", data.temperature !=null ? data.temperature.toFixed(2):"--");
    setText("live-humidity", data.humidity !=null ? data.humidity.toFixed(2):"--");
    setText("live-moisture", data.soil_moisture != null ? data.soil_moisture.toFixed(2): "--");
    setText("live-soil-temp", data.soil_temp != null ? data.soil_temp.toFixed(2): "--");
    setText("live-turbidity", data.tds != null ? data.tds.toFixed(2): "--");
    if (data.id && data.id !== latestId) {
      latestId = data.id;
      console.log("Latest sensor data ID:", latestId);
    }
   } catch (err) {
    console.error("Error fetching live sensor data:", err);
   }
  }

setInterval(fetchLiveSensor, 10000);  // every 10 seconds
fetchLiveSensor();

const form=document.getElementById('sensor-form');
form.addEventListener('submit', async function (e) {
  e.preventDefault();
  const data = {
    N: parseFloat(form.nitrogen.value),
    P: parseFloat(form.phosphorus.value),
    K: parseFloat(form.potassium.value),
    temperature: parseFloat(document.getElementById('live-temp').textContent) || 0,
    humidity: parseFloat(document.getElementById('live-humidity').textContent) || 0,
    ph: parseFloat(form.ph.value),
    rainfall: parseFloat(form.rainfall.value)
  };
  document.getElementById('loading').style.display = 'inline-block';
  document.getElementById('result').textContent = "";

 try {
      const response = await fetch(`${BASE_URL}/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      document.getElementById('result').textContent = result.crop || "--";
    } catch (error) {
      console.error("Prediction error:", error);
      document.getElementById('result').textContent = "Prediction failed.";
    } finally {
      document.getElementById('loading').style.display = 'none';
    }
  });
});