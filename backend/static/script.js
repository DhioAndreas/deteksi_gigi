document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const previewImage = document.getElementById('previewImage');
    const predictButton = document.getElementById('predictButton');
    const predictionResult = document.getElementById('predictionResult');
    // const confidenceResult = document.getElementById('confidenceResult'); // dihapus
    // const allScoresDiv = document.getElementById('allScores'); // dihapus
    const resultsArea = document.querySelector('.results-area');
    const loadingDiv = document.getElementById('loading');
    const errorMessageDiv = document.getElementById('errorMessage');

    let uploadedFile = null;

    const BASE_URL = "http://192.168.1.13:5000";

    imageUpload.addEventListener('change', (event) => {
        uploadedFile = event.target.files[0];

        if (uploadedFile) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                predictButton.disabled = false;
                resultsArea.style.display = 'none';
                errorMessageDiv.style.display = 'none';
                // allScoresDiv.innerHTML = ''; // dihapus
            };
            reader.readAsDataURL(uploadedFile);
        } else {
            resetView();
        }
    });

    predictButton.addEventListener('click', async () => {
        if (!uploadedFile) {
            displayError('Silakan pilih gambar terlebih dahulu.');
            return;
        }

        predictButton.disabled = true;
        loadingDiv.style.display = 'flex';
        resultsArea.style.display = 'none';
        errorMessageDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            const response = await fetch(`${BASE_URL}/predict`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Terjadi kesalahan saat memproses gambar.');
            }

            const data = await response.json();

            if (data.prediction === "Tidak Dikenali" || data.message) {
                displayError(data.message || 'Gambar tidak dikenali sebagai gigi. Silakan coba gambar lain.');
                return;
            }

            predictionResult.textContent = data.prediction;
            // confidenceResult.textContent = (data.confidence * 100).toFixed(2); // dihapus
            // allScoresDiv.innerHTML = ''; // tidak ditampilkan

            resultsArea.style.display = 'block';

        } catch (error) {
            displayError(`Gagal melakukan deteksi: ${error.message}`);
        } finally {
            loadingDiv.style.display = 'none';
            predictButton.disabled = false;
        }
    });

    function resetView() {
        previewImage.src = '#';
        previewImage.style.display = 'none';
        predictButton.disabled = true;
        resultsArea.style.display = 'none';
        errorMessageDiv.style.display = 'none';
        // allScoresDiv.innerHTML = ''; // dihapus
        predictionResult.textContent = '';
        // confidenceResult.textContent = ''; // dihapus
    }

    function displayError(message) {
        errorMessageDiv.textContent = message;
        errorMessageDiv.style.display = 'block';
        errorMessageDiv.scrollIntoView({ behavior: 'smooth' });

        predictionResult.textContent = '';
        // confidenceResult.textContent = ''; // dihapus
        // allScoresDiv.innerHTML = ''; // dihapus
        resultsArea.style.display = 'none';
    }
});
