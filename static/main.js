document.getElementById("btn1").addEventListener("click", function () {
    // Create a hidden file input dynamically
    let fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".csv";
    fileInput.style.display = "none";

    // When user selects a file, upload it
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length === 0) {
            alert("No file selected.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        fetch("http://127.0.0.1:5300/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            window.location.replace("analysis");
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to upload file.");
        });
    });

    // Trigger the file input dialog
    fileInput.click();
});