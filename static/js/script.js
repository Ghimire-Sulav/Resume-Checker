document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("resume_file");
  const dropZone = document.getElementById("drop-zone");
  const fileName = document.getElementById("file-name");
  const textArea = document.getElementById("resume_text");
  const counter = document.getElementById("char-count");
  const form = document.getElementById("resume-form");
  const button = document.getElementById("analyze-button");

  if (fileInput && fileName) {
    fileInput.addEventListener("change", () => {
      fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "Drop your resume here, or browse files";
    });
    ["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("drag-over");
    }));
    ["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.remove("drag-over");
    }));
    dropZone.addEventListener("drop", (event) => {
      const files = event.dataTransfer.files;
      if (files.length) {
        fileInput.files = files;
        fileInput.dispatchEvent(new Event("change"));
      }
    });
  }
  if (textArea && counter) {
    textArea.addEventListener("input", () => {
      counter.textContent = `${textArea.value.length.toLocaleString()} / 30,000`;
    });
  }
  if (form && button) {
    form.addEventListener("submit", () => {
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Analyzing…';
    });
  }
});
