"use strict"

function toggleFood() {
    const foodBar = document.getElementById("food-bar");
    const shrinkButton = document.getElementById("shrink-button");
    const home = document.getElementById("grid-container")

    foodBar.classList.toggle("collapsed");
    shrinkButton.innerHTML = foodBar.classList.contains("collapsed") ? "&#9650;" : "&#x25BC;";
    home.style.maxHeight = foodBar.classList.contains("collapsed") ? "80vh" : "75vH";
    home.style.maxWidth = foodBar.classList.contains("collapsed") ? "80vh" : "75vH";
}

function restoreFood() {
    const foodBar = document.getElementById("food-bar");
    const shrinkButton = document.getElementById("shrink-button");
    const home = document.getElementById("grid-container")

    foodBar.classList.remove("collapsed");
    shrinkButton.innerHTML = "&#x25BC;";
    home.style.maxHeight = "75vh";
    home.style.maxWidth = "75vh";
}

