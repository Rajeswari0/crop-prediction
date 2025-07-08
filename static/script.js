/*
async function recommendCrop(event) {
    event.preventDefault();

    const resultElement = document.getElementById("result");
    const resultCard = document.getElementById("result-card");
    const loadingSpinner = document.getElementById("loading");

    resultElement.innerText = "Predicting...";
    resultCard.style.display = "block";
    loadingSpinner.style.display = "inline-block";


    const form = document.forms[0];
    const data = {
        N: parseFloat(form.nitrogen.value),
        P: parseFloat(form.phosphorus.value),
        K: parseFloat(form.potassium.value),
        temperature: parseFloat(form.temperature.value),
        humidity: parseFloat(form.humidity.value),
        ph: parseFloat(form.ph.value),
        rainfall: parseFloat(form.rainfall.value)
    };

    try {
        const response = await fetch('https://crop-prediction-feue.onrender.com/crop_prediction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

       if (!response.ok) throw new Error("Server error");

    const result = await response.json();
    const crop = result["recommended crop"];
    resultElement.innerText = ` ${crop}`;
  } catch (err) {
    resultElement.innerText = "Error: " + err.message;
  } finally {
    loadingSpinner.style.display = "none";
  }
}*/


let latestId = null;

async function fetchLiveSensor() {
  try {
    const res = await fetch("https://crop-prediction-1-t1e1.onrender.com/latest_sensor_data");
    const data = await res.json();
    
    document.getElementById("live-temp").innerText = data.temperature.toFixed(1);
    document.getElementById("live-humidity").innerText = data.humidity.toFixed(1);
    document.getElementById("live-crop").innerText = data.crop || "--";
    
    latestId = data.id;
  } catch (err) {
    console.error("Error fetching live sensor data:", err);
  }
}

setInterval(fetchLiveSensor, 3000);  // every 3 seconds
fetchLiveSensor();

async function sendFeedback(event) {
  event.preventDefault();
  const feedback = document.getElementById("feedback").value;
  try {
    const response = await fetch("https://crop-prediction-1-t1e1.onrender.com/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: latestId, feedback: feedback })
    });

    if (!response.ok) throw new Error("Failed to submit feedback");
    alert("Feedback submitted!");
  } catch (err) {
    alert("Error submitting feedback: " + err.message);
  }
}
