document.addEventListener("DOMContentLoaded", () => {
  const previewContainer = document.getElementById("preview-container");
  const predictionText = document.getElementById("prediction-text");
  const confidenceText = document.getElementById("confidence-text");
  const previewImage = document.getElementById("preview-image");

  // Jika data dikirim dari Flask
  if (window.leafyData) {
    const { prediction, confidence, imgPath } = window.leafyData;

    predictionText.textContent = `🌿 Prediksi: ${prediction}`;
    confidenceText.textContent = `🎯 Akurasi: ${confidence}%`;
    previewImage.src = imgPath;
    previewContainer.classList.remove("hidden");
  }

  // Preview gambar sebelum kirim
  const fileInput = document.getElementById("file-input");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        previewImage.src = URL.createObjectURL(file);
        predictionText.textContent = "Gambar akan diklasifikasi setelah dikirim...";
        confidenceText.textContent = "";
        previewContainer.classList.remove("hidden");
      }
    });
  }
});
