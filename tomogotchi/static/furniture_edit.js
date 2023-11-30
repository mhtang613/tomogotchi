"use strict"

function displayGrid() {
    let grid = document.getElementById("grid-container");
    for (let i = grid.childElementCount; i < 400; i++) {
        let new_elem = document.createElement("div");
        new_elem.setAttribute("class", "gridlines");
        grid.append(new_elem);
    }
}
function hideGrid() {
    let grid = document.getElementById("grid-container");
    let index = 0;
    let original_cnt = grid.childElementCount;
    for (let i = 0; i < original_cnt; i++) {
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

class dragFurniture {
    static pos1 = 0; 
    static pos2 = 0; 
    static pos3 = 0; 
    static pos4 = 0;
    // This func get's attatched to furniture's onclick event
    static clickFurniture(event) {
        var elem = event.target || event.srcElement
        // Make a copy of the target furniture
        // Decrease count of target furniture
        // Make the copy draggable:
        dragFurniture.dragElement(elem);
    }

    static dragElement(elem) {
        elem.onmousedown = dragFurniture.dragMouseDown;   // set onmousedown
    }

    static dragMouseDown(e) {
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = dragFurniture.elementDrag;
    }

    static elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    static closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

// ---------------------------- Websockets Stuff ---------------------------- //

/*
 * Use a global variable for the socket.  Poor programming style, I know,
 * but I think the simpler implementations of the deleteItem() and addItem()
 * functions will be more approachable for students with less JS experience.
 */

class FurnitureHandler {
    static furniture_socket = null;

    static receiveCollisionList(collision_list) {
        displayMessage("furniture_edit.js receiveCollisionList")
        displayMessage(collision_list)
    }

    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/furniture/data/${myUserID}`
        this.furniture_socket = new WebSocket(url)

        // Handle any errors that occur.
        this.furniture_socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }

        // Show a connected message when the WebSocket is opened.
        this.furniture_socket.onopen = function(event) {
            displayMessage("Furniture WebSocket Connected")
        }

        // Show a disconnected message when the WebSocket is closed.
        this.furniture_socket.onclose = function(event) {
            displayMessage("Furniture WebSocket Disconnected")
        }

        // Handle messages received from the server.
        this.furniture_socket.onmessage = function(event) {
            let response = JSON.parse(event.data)
            if (Array.isArray(response)) {
                FurnitureHandler.receiveCollisionList(response)
            } else {
                displayResponse(response)
            }
        }
    }

    

    static updateList(items) {
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
    static makeListItemElement(item) {
        let deleteButton
        if (item.user.id === myUserID) { // myUserID defined in edit.html
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

    static sanitize(s) {
        // Be sure to replace ampersand first
        return s.replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
    }

    static addItem() {
        let textInputEl = document.getElementById("item")
        let itemText = textInputEl.value
        if (itemText === "") return

        // Clear previous error message, if any
        displayError("")
        
        let data = {"action": "add", "text": itemText}
        this.furniture_socket.send(JSON.stringify(data))

        textInputEl.value = ""
    }

    static deleteItem(id) {
        let data = {"action": "delete", "id": id}
        this.furniture_socket.send(JSON.stringify(data))
    }
}

FurnitureHandler.connectToServer();