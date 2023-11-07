"use strict"

let socket = null

function connectToServer() {
    // Use wss: protocol if site using https:, otherwise use ws: protocol
    let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

    // Create a new WebSocket.
    let url = `${wsProtocol}//${window.location.host}/messages/data`
    socket = new WebSocket(url)

    // Handle any errors that occur.
    socket.onerror = function(error) {
        displayMessage("WebSocket Error: " + error)
    }

    // Show a connected message when the WebSocket is opened.
    socket.onopen = function(event) {
        displayMessage("WebSocket Connected")
        requestData()
    }

    // Show a disconnected message when the WebSocket is closed.
    socket.onclose = function(event) {
        displayMessage("WebSocket Disconnected")
    }

    // Handle messages received from the server.
    socket.onmessage = function(event) {
        let response = null
        try {
            response = JSON.parse(event.data)
        } catch (e) {
            console.log(`Not JSON: ${event.data}`)
            return
        }
        if (Array.isArray(response)) {
            updateMessages(response)
            //auto scroll to bottom (with newest messages)
            let elem = document.getElementById('messages-list');    
            elem.scrollTop = elem.scrollHeight;
        } else {
            displayResponse(response)
        }
    }
}

function updateMessages(messages) {
    // Get the messages container
    let msg_container = document.getElementById("messages-list")
    // Adds each new message received from the server to the container
    messages.forEach(msg => {
        if (!document.getElementById(`id_msg_div_${msg.id}`)) {
            msg_container.append(makeMessageDiv(msg))
        }
    })
}

// Builds a new HTML "div" element for each message
function makeMessageDiv(msg) {
    let author_home_link = `<a class="home-inline" id="id_msg_home_${msg.id}" href="${otherHomeURL(msg.user.id)}">${msg.user.first_name} ${msg.user.last_name}</a>`
    let author_name = `<span class="msg_author"> ${author_home_link}: </span>`
    let msg_text = `<span id="id_msg_text_${msg.id}">${sanitize(msg.text)}</span>`
    let dash = '<span class="msg-info"> - </span>'
    
    let date = new Date(msg.date)
    let time_str = date.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})
    let msg_time = `<span class="msg-info" id="id_msg_date_time_${msg.id}">${date.toLocaleDateString()} ${time_str}</span>`
    
    let msg_div = document.createElement("div")
    msg_div.id = `id_msg_div_${msg.id}`
    msg_div.setAttribute("class", "message")
    msg_div.innerHTML = `${author_name} ${msg_text} ${dash} ${msg_time}`

    return msg_div
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

function requestData() {
    let data = {"action": "get"}
    socket.send(JSON.stringify(data))
}

function sendRequest(element) {
    displayError("")    // clear error
    let data = {"action": "add", "message": element.value}
    element.value = ""  // clear input box
    socket.send(JSON.stringify(data))
}

function attachEvents() {
    let message_input = document.getElementById('message-input')
    message_input.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            console.log("Enter pressed")
            if (message_input.value) {
                sendRequest(message_input)
            }
        }
    })
}
