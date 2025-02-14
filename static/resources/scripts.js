let isFahrenheit = false;

//document.getElementById("submit_button").addEventListener("click", validateForm);

document.querySelector("#alternate").addEventListener('click', () => {
    const tempElement = document.querySelector("#main-temp p");
    const tempUnit = document.querySelector("#alternate");
    const currentTemp = parseInt(tempElement.innerText);


    if (isFahrenheit) {
        tempElement.innerText = convertToCelsius(currentTemp) + "°C";
        tempElement.appendChild(tempUnit);
        tempUnit.innerText = "|°F";
    } else {
        tempElement.innerText = convertToFahrenheit(currentTemp) + "°F";
        tempElement.appendChild(tempUnit);
        tempUnit.innerText = "|°C";
    }

    const forecastTemps = document.querySelectorAll(".forecast-temps");
    forecastTemps.forEach((temp) => {
        const tempText = temp.innerText;
        const temps = tempText.split("/");
        const highTemp = parseInt(temps[0]);
        const lowTemp = parseInt(temps[1]);

        if (isFahrenheit) {
            temp.innerText = convertToCelsius(highTemp) + "°C /" + convertToCelsius(lowTemp) + "°C";
        } else {
            temp.innerText = convertToFahrenheit(highTemp) + "°F /" + convertToFahrenheit(lowTemp) + "°F";
        }
    });

    isFahrenheit = !isFahrenheit;
});



function convertToCelsius(fahrenheit) {
    return Math.round((fahrenheit - 32) * 5 / 9);
}

function convertToFahrenheit(celsius) {
    return Math.round(celsius * 9 / 5 + 32);
}

function showLoadingState() {
    // Disable the submit button
    document.getElementById("submit_button").disabled = true;
    // Show a loading indicator or message
    // For example, you can add a spinner element to your HTML and show it:
    document.getElementById("loading_spinner").style.display = "block";
}

function hideLoadingState() {
    // Enable the submit button
    document.getElementById("submit_button").disabled = false;
    // Hide the loading indicator or message
    // For example, if you added a spinner element, you can hide it:
    document.getElementById("loading_spinner").style.display = "none";
}