document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
      const loadingScreen = document.getElementById("loading-screen");
      const appContent = document.querySelector(".App");
      loadingScreen.style.display = "none";
      appContent.style.display = "block";
    }, 1000);
  });
  