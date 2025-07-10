document.addEventListener("DOMContentLoaded", () => {
 let latestId = null;

 const setText = (id, value) => {
   const element = document.getElementById(id);
   /*if(!element) {
     console.log(`Element with ID '${id}' was not found in html`);
    return;
   }
    console.log(`Setting text for ${id} to ${value}`);
     element.innerText = value;
     */ 
    if (element) {
    element.innerText = value;
    }
  };

 async function fetchLiveSensor() {
  
   try {
    const res = await fetch("https://crop-prediction-1-t1e1.onrender.com/latest_sensor_data");
    const data = await res.json();
    
    
    //setText("live-nitrogen", data.nitrogen ?? "82");
    //setText("live-phosphorus", data.phosphorus ?? "43");
    //setText("live-potassium", data.potassium ?? "42");
    setText("live-temp", data.temperature !=null ? data.temperature.toFixed(1):"--");
    setText("live-humidity", data.humidity !=null ? data.humidity.toFixed(1):"--");
    //setText("live-ph", data.ph ?? "6.5");
    //setText("live-rainfall", data.rainfall ?? "202");
    //setText("result", data["recommended crop"] || data.crop || "--");
    // latestId = data.id;
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
      const response = await fetch('/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      document.getElementById('result').textContent = result.recommended_crop;
    } catch (error) {
      console.error("Prediction error:", error);
      document.getElementById('result').textContent = "Prediction failed.";
    } finally {
      document.getElementById('loading').style.display = 'none';
    }
  });
});