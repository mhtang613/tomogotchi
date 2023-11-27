"use strict"

function toggleFood() {
    const foodBar = document.getElementById("food-bar");
    const restoreButton = document.getElementById("restore-button");

    foodBar.classList.toggle("collapsed");
    restoreButton.style.display = foodBar.classList.contains("collapsed") ? "block" : "none";
}

function restoreFood() {
    const foodBar = document.getElementById("food-bar");
    const restoreButton = document.getElementById("restore-button");

    foodBar.classList.remove("collapsed");
    restoreButton.style.display = "none";
}