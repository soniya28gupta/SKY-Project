// static/js/scanner.js
class PlantScanner {
    constructor() {
        // use current origin so it works on any host/port
        this.apiBase = window.location.origin + '/api';
    }

    async scanImage(imageFile) {
        try {
            const formData = new FormData();
            formData.append('file', imageFile);

            const response = await fetch(`${this.apiBase}/scan`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`Server returned HTML instead of JSON: ${text.substring(0, 200)}`);
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Scan error:', error);
            throw error;
        }
    }

    async scanRandom() {
        try {
            const response = await fetch(`${this.apiBase}/random-scan`, {
                headers: {
                    'Accept': 'application/json'
                }
            });

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`Server returned HTML instead of JSON: ${text.substring(0, 200)}`);
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('Random scan error:', error);
            throw error;
        }
    }
}

// Usage bindings (these expect the elements below to exist)
const scanner = new PlantScanner();

document.getElementById('uploadButton').addEventListener('click', async function() {
    const fileInput = document.getElementById('imageInput');
    if (fileInput.files.length === 0) {
        alert('Please select an image file');
        return;
    }

    try {
        const result = await scanner.scanImage(fileInput.files[0]);
        displayResults(result);
    } catch (error) {
        displayError(error.message);
    }
});

document.getElementById('randomScanButton').addEventListener('click', async function() {
    try {
        const result = await scanner.scanRandom();
        displayResults(result);
    } catch (error) {
        displayError(error.message);
    }
});

function displayResults(result) {
    const resultsDiv = document.getElementById('scanResults');
    if (result.success) {
        resultsDiv.innerHTML = `
            <h3>Scan Results</h3>
            <p><strong>Health Score:</strong> ${result.data.health_score}%</p>
            <p><strong>Disease Detected:</strong> ${result.data.disease_detected ? 'Yes' : 'No'}</p>
            <p><strong>Plant Type:</strong> ${result.data.plant_type}</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                ${result.data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    } else {
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
    }
}

function displayError(error) {
    const resultsDiv = document.getElementById('scanResults');
    resultsDiv.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
}
