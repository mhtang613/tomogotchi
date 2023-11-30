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


// Takes in the furniture item you want to place, returns True if valid placement
function can_place_furniture(furn) {
    let furnX1 = furn.locationX;
    let furnX2 = furnX1 + furn.hitboxX
    let furnY1 = furn.locationY;
    let furnY2 = furnY1 + furn.hitboxY
    let collision_list = FurnitureHandler.getCollisionList();
    collision_list.forEach(placed_furn => {
        let pfurnX1 = placed_furn.locationX;
        let pfurnX2 = pfurnX1 + placed_furn.hitboxX
        let pfurnY1 = placed_furn.locationY;
        let pfurnY2 = pfurnY1 + placed_furn.hitboxY

        if (!(1 <= furnX1 && furnX2 <= 20 && 1 <= furnY1 && furnY2 <= 20)) {
            return false
        } 

        overlap_x = (furnX1 < pfurnX2) && (pfurnX1 < furnX2)
        overlap_y = (furnY1 < pfurnY2) && (pfurnY1 < furnY2)
        return !(overlap_x && overlap_y)
    })
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


// ---------------------------- Websockets Stuff ---------------------------- //

class FurnitureHandler {
    static furniture_socket = null;
    static collision_list = [];


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

    static receiveCollisionList(collision_list) {
        displayMessage("furniture_edit.js receiveCollisionList")
        displayMessage(collision_list)
        FurnitureHandler.collision_list = collision_list
    }

    static getCollisionList() {
        return this.collision_list
    }
    
}


FurnitureHandler.connectToServer();