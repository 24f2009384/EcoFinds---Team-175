document.addEventListener("DOMContentLoaded", () => {
    const sellButton = document.querySelector(".sell-btn");
    sellButton.addEventListener("click", () => {
        alert("Redirecting to sell page...");
        // window.location.href = "/sell"; // Uncomment and define the route in Flask
    });
});
