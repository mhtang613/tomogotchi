"use strict"

function displayGrid() {
    grid = document.getElementById("grid-container");
    for (i = grid.childElementCount; i < 400; i++) {
        let new_elem = document.createElement("div");
        new_elem.setAttribute("class", "gridlines");
        grid.append(new_elem);
    }
}
function hideGrid() {
    grid = document.getElementById("grid-container");
    let index = 0;
    let original_cnt = grid.childElementCount;
    for (i = 0; i < original_cnt; i++) {
        let child = grid.children[index];
        if (child.getAttribute("class") == "gridlines") {
            child.remove()
        } else {
            index++;
        }
    }
}

function cellSelected() {
    alert("Selected furniture"); 
}

// ---------------------------- Websockets Stuff ---------------------------- //

/*
 * Use a global variable for the socket.  Poor programming style, I know,
 * but I think the simpler implementations of the deleteItem() and addItem()
 * functions will be more approachable for students with less JS experience.
 */
let furniture_socket = null


function connectToServer() {
    // Use wss: protocol if site using https:, otherwise use ws: protocol
    let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

    // Create a new WebSocket.
    let url = `${wsProtocol}//${window.location.host}/ws_todolist/data`
    socket = new WebSocket(url)

    // Handle any errors that occur.
    furniture_socket.onerror = function(error) {
        displayMessage("WebSocket Error: " + error)
    }

    // Show a connected message when the WebSocket is opened.
    furniture_socket.onopen = function(event) {
        displayMessage("WebSocket Connected")
    }

    // Show a disconnected message when the WebSocket is closed.
    furniture_socket.onclose = function(event) {
        displayMessage("WebSocket Disconnected")
    }

    // Handle messages received from the server.
    furniture_socket.onmessage = function(event) {
        let response = JSON.parse(event.data)
        if (Array.isArray(response)) {
            updateList(response)
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
    let errorElement = document.getElementById("message")
    errorElement.innerHTML = message
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

function updateList(items) {
    // Removes items from todolist if they not in items
    let liElements = document.getElementsByTagName("li")
    for (let i = 0; i < liElements.length; i++) {
        let element = liElements[i]
        let deleteIt = true
        items.forEach(item => {
            if (element.id === `id_item_${item.id}`) deleteIt = false
        })
        if (deleteIt) element.remove()
    }

    // Adds each to do list item received from the server to the displayed list
    let list = document.getElementById("todo-list")
    items.forEach(item => {
        if (document.getElementById(`id_item_${item.id}`) == null) {
            list.append(makeListItemElement(item))
        }
    })
}

// Builds a new HTML "li" element for the to do list
function makeListItemElement(item) {
    let deleteButton
    if (item.user === myUserName) {
        deleteButton = `<button onclick='deleteItem(${item.id})'>X</button>`
    } else {
        deleteButton = "<button style='visibility: hidden'>X</button> "
    }

    let details = `<span class="details">(id=${item.id}, ip_addr=${item.ip_addr}, user=${item.user})</span>`

    let element = document.createElement("li")
    element.id = `id_item_${item.id}`
    element.innerHTML = `${deleteButton} ${sanitize(item.text)} ${details}`

    return element
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addItem() {
    let textInputEl = document.getElementById("item")
    let itemText = textInputEl.value
    if (itemText === "") return

    // Clear previous error message, if any
    displayError("")
    
    let data = {"action": "add", "text": itemText}
    furniture_socket.send(JSON.stringify(data))

    textInputEl.value = ""
}

function deleteItem(id) {
    let data = {"action": "delete", "id": id}
    furniture_socket.send(JSON.stringify(data))
}