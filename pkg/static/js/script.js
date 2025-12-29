const fileInput = document.getElementById('fileInput');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const imagePreview = document.getElementById('imagePreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const scanLine = document.getElementById('scanLine');
const resultOverlay = document.getElementById('resultOverlay');

// Handle Image Upload
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            uploadPlaceholder.style.display = 'none';
            analyzeBtn.disabled = false;
        }
        reader.readAsDataURL(file);
    }
});

function resetApp() {
    // 1. Hide the result overlay
    resultOverlay.classList.remove('active');
    
    // 2. Clear the preview image
    imagePreview.style.display = 'none';
    imagePreview.src = ''; 
    
    // 3. Show the upload box again
    uploadPlaceholder.style.display = 'block';
    
    // 4. IMPORTANT: Clear the file input so selecting the same file triggers 'change'
    fileInput.value = ''; 
    
    // 5. Disable the main button until a new file is dropped
    analyzeBtn.disabled = true;
    analyzeBtn.innerText = "Run AI Diagnosis"; // Reset text just in case
}

// Simulate AI Analysis
// --- REPLACE THE OLD runAnalysis WITH THIS ---

async function runAnalysis() {
    const file = fileInput.files[0];
    
    if (!file) {
        alert("Please upload an image first.");
        return;
    }

    // 1. UI Updates: Start scanning animation
    scanLine.style.display = 'block';
    analyzeBtn.innerText = "Processing...";
    analyzeBtn.disabled = true;
    
    // 2. PACKAGING: Put the file in the "envelope"
    const formData = new FormData();
    formData.append('file', file); // 'file' matches request.files['file'] in Python

    try {
        // 3. SENDING: Send the envelope to your Python route
        // Note: Your route is defined as '/predict/' in Python
        const response = await fetch('/predict/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Stop scanning
        scanLine.style.display = 'none';
        analyzeBtn.innerText = "Run AI Diagnosis";

        if (data.status === 'success') {
            updateResultUI(data); // Update the screen with real data
            resultOverlay.classList.add('active');
        } else {
            alert('Error: ' + data.error);
            analyzeBtn.disabled = false;
        }

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while connecting to the server.');
        scanLine.style.display = 'none';
        analyzeBtn.innerText = "Run AI Diagnosis";
        analyzeBtn.disabled = false;
    }
}

// --- ADD THIS NEW FUNCTION ---
// This function takes the Python data and puts it into the HTML
function updateResultUI(data) {
    const card = document.querySelector('.result-card');
    const badge = card.querySelector('.badge');
    const title = card.querySelector('h3');
    const desc = card.querySelector('p');
    const confidenceText = card.querySelector('.confidence-meter').previousElementSibling.lastElementChild;
    const meterFill = card.querySelector('.meter-fill');

    // Update Text based on Python response
    badge.innerText = data.prediction; // "Cancerous" or "Healthy"
    title.innerText = data.is_cancerous ? "Carcinogenic Features" : "Normal Tissue Structure";
    desc.innerText = data.is_cancerous 
        ? "The AI Model has detected irregular tissue patterns consistent with early-stage malignancy." 
        : "No irregularities were detected. The tissue structure appears healthy.";
    
    // Update Confidence Score
    // data.confidence_score comes in as 0.95, so we multiply by 100
    const percentage = Math.round(data.confidence_score * 100);
    confidenceText.innerText = percentage + "%";

    // Update Colors
    if (data.is_cancerous) {
        badge.className = "badge danger";
        badge.style.background = "#fee2e2";
        badge.style.color = "#ef4444";
        meterFill.style.background = "#ef4444";
    } else {
        badge.className = "badge safe";
        badge.style.background = "#d1fae5";
        badge.style.color = "#10b981";
        meterFill.style.background = "#10b981";
    }

    // Animate Meter
    setTimeout(() => {
        meterFill.style.width = percentage + "%";
    }, 100);
}