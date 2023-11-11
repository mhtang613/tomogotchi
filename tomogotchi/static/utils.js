"use strict"

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function displayMessage(message) {
    // let messageElement = document.getElementById("message")
    // messageElement.innerHTML = message
    console.log(message)
}

function displayResponse(response) {
    if ("error" in response) {
        displayError(response.error)
    } else if ("message" in response) {
        displayMessage(response.message)
    } else {
        displayMessage("Unknown response")
    }
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function requestData() {
    let data = {"action": "get"}
    socket.send(JSON.stringify(data))
}