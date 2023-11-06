"use strict"

let socket = null

function connectToServer() {
    // Use wss: protocol if site using https:, otherwise use ws: protocol
    let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

    // Create a new WebSocket.
    let url = `${wsProtocol}//${window.location.host}/test/data`
    socket = new WebSocket(url)

    // Handle any errors that occur.
    socket.onerror = function(error) {
        displayMessage("WebSocket Error: " + error)
    }

    // Show a connected message when the WebSocket is opened.
    socket.onopen = function(event) {
        displayMessage("WebSocket Connected")
    }

    // Show a disconnected message when the WebSocket is closed.
    socket.onclose = function(event) {
        displayMessage("WebSocket Disconnected")
    }

    // Handle messages received from the server.
    socket.onmessage = function(event) {
        try {
            let response = JSON.parse(event.data)
        } catch (e) {
            console.log(`Not JSON: ${event.data}`)
            return
        }
        if (Array.isArray(response)) {
            // do something
        } else {
            displayResponse(response)
        }
    }
}

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

function sendRequest(element) {
    let data = {"action": "test", "message": element.value}
    socket.send(JSON.stringify(data))
}

function attachEvents() {
    let message_input = document.getElementById('message-input')
    message_input.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            console.log("Enter pressed")
            sendRequest(message_input)
        }
    })
}
