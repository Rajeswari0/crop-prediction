const baseURL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://crop-prediction-feue.onrender.com";

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
        const response = await fetch(`${baseURL}/crop_prediction`, {
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
}
