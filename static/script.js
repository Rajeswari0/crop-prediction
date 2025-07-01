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
        const response = await fetch('http://127.0.0.1:8000/crop_prediction', {
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
// live meter updates
 window.addEventListener("load", () => {
    // Live meter updates only
    const fields = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"];
    const meterIds = ["n-meter", "p-meter", "k-meter", "t-meter", "h-meter", "ph-meter", "r-meter"];

    fields.forEach((field, i) => {
        const input = document.getElementById(field);
        const meter = document.getElementById(meterIds[i]);

        if (input && meter) {
            input.addEventListener("input", () => {
                meter.value = parseFloat(input.value) || 0;
            });
        }
    });
});