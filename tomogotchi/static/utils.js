"use strict"

class NameHandler {
    static socket = null
    static original_name = null
    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/editname`
        this.socket = new WebSocket(url)

        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }

        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            displayMessage("Edit Name WebSocket Connected")
        }

        // Show a disconnected message when the WebSocket is closed & try to reconnect
        this.socket.onclose = function(event) {
            displayMessage("WebSocket Disconnected: Name Editing finished")
            this.socket = null   // reset static 
        }

        // Handle messages received from the server.
        this.socket.onmessage = function(event) {
            let response = null
            try {
                response = JSON.parse(event.data)
            } catch (e) {
                console.log(`Server: ${event.data}`)
                return
            }
            if (response.hasOwnProperty('name')) {
                NameHandler.updateName(response.name)
            } else {
                displayResponse(response)
            }
        }
    }

    // Enters name editing mode
    static editName() {
        NameHandler.connectToServer()   // create websocket

        let edit_button = document.getElementById("edit-name-button")
        edit_button.innerText = "Submit"
        
        let name_div = document.getElementById("player-name")
        let name_ref = name_div.firstElementChild
        
        self.original_name = name_ref.innerText // save valid name
        name_ref.style.visibility = "hidden"    // disable link - no clicking
        name_ref.innerText = ""

        let name_entry = document.createElement("input")
        name_entry.type = "text"
        name_entry.value = self.original_name
        name_entry.id = "name-entry"
        name_entry.maxLength = 15
        name_div.append(name_entry)

        NameHandler.editingEvents()
    }
    
    static submitName() {
        let name_entry = document.getElementById('name-entry')
        // only send name if name non-empty & different from original
        if (name_entry.value && !(name_entry.value === self.original_name) ) { 
            displayError("")    // clear error
            let data = {"action": "edit", "name": name_entry.value}
            name_entry.value = ""  // clear input box
            this.socket.send(JSON.stringify(data))
        }
    }

    static updateName(name) {
        let name_ref = document.getElementById("player-name").firstElementChild
        name_ref.innerText = name
        NameHandler.exit_editing()
    }

    // Undos changes editName made to go into name editing mode
    static exit_editing() {
        let name_div = document.getElementById("player-name")
        
        let name_ref = name_div.firstElementChild
        name_ref.style.visibility = "visible" 

        self.original_name = null   // reset static

        let name_entry = document.getElementById('name-entry')
        name_div.removeChild(name_entry)

        let edit_button = document.getElementById("edit-name-button")   
        edit_button.innerText = "Edit!"  // reset edit button
        this.socket.close() // editing done, websocket no longer needed
    }

    static editingEvents() {
        let name_entry = document.getElementById('name-entry')
        name_entry.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                NameHandler.submitName()
            }
        })
        
        // Stop editing if user clicks escape
        document.body.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                console.log(`${event.key} Pressed`)
                let name_ref = document.getElementById("player-name").firstElementChild
                name_ref.innerText = self.original_name
                NameHandler.exit_editing()
            }
        })
    }

    static attachEvents() {
        let edit_button = document.getElementById("edit-name-button")
        edit_button.addEventListener('click', function() {
            switch (edit_button.innerText) {
                case 'Edit!':
                    NameHandler.editName()
                    break;
                case 'Submit':
                    NameHandler.submitName()
                    break;
                default:
                    console.log(`Error: Invalid name_edit button text ${edit_button.innerText}`)
                    break;
            }
        })
    }
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function displayMessage(message) {
    let messageElement = document.getElementById("message")
    messageElement.innerHTML = message
}

function displayResponse(response) {
    if ("error" in response) {
        displayError(response.error)
    } else if ("message" in response) {
        displayMessage(response.message)
    } else if ("debug" in response) {
        console.log(response.debug)
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