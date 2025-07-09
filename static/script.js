document.addEventListener("DOMContentLoaded", () => {
 let latestId = null;

 const setText = (id, value) => {
   const element = document.getElementById(id);
   if(!element) {
     console.log(`Element with ID '${id}' was not found in html`);
    return;
   }
    console.log(`Setting text for ${id} to ${value}`);
     element.innerText = value;
  };

 async function fetchLiveSensor(event) {
   if (event && event.type === "click") {
     latestId = null; // Reset on button click
    }
   try {
    const res = await fetch("https://crop-prediction-1-t1e1.onrender.com/latest_sensor_data");
    const data = await res.json();
    
    
    setText("live-nitrogen", data.nitrogen ?? "82");
    setText("live-phosphorus", data.phosphorus ?? "43");
    setText("live-potassium", data.potassium ?? "42");
    setText("live-temp", data.temperature !=null ? data.temperature.toFixed(1):"22.0");
    setText("live-humidity", data.humidity !=null ? data.humidity.toFixed(1):"92.0");
    setText("live-ph", data.ph ?? "6.5");
    setText("live-rainfall", data.rainfall ?? "202");

    setText("result", data["recommended crop"] || data.crop || "--");

    
    latestId = data.id;
   } catch (err) {
    console.error("Error fetching live sensor data:", err);
   }
  }

setInterval(fetchLiveSensor, 10000);  // every 3 seconds
fetchLiveSensor();

});