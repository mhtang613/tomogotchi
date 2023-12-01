"use strict"


function displayGrid() {
    let grid = document.getElementById("grid-container");
    for (const child of grid.children) {
        if (child.hasAttribute('class') && child.getAttribute('class') === 'item')
        {
            child.setAttribute('class', 'gridlines')
        }
    }
}
function hideGrid() {
    let grid = document.getElementById("grid-container");
    for (const child of grid.children) {
        if (child.hasAttribute('class') && child.getAttribute('class') === 'gridlines')
        {
            child.setAttribute('class', 'item')
        }
    }
}

class dragFurniture {
    static pos1 = 0; 
    static pos2 = 0; 
    static pos3 = 0; 
    static pos4 = 0;
    static elem = null;
    static hitboxX = 0;
    static hitboxY = 0;
    // This func get's attatched to unplaced furniture's onclick event
    static clickFurniture(event) {
        var count = this.getElementsByClassName('counter-circle-edit')[0];
        if (count.innerText <= 0) { return; }
        // Decrease count of target furniture
        count.innerText -= 1;

        // Make a copy of the target furniture
        var copy = this.cloneNode(true);
        copy.removeChild(copy.getElementsByClassName('counter-circle-edit')[0]);
        copy.getElementsByClassName('icon')[0].style.paddingLeft = "0px";

        // Remove original if count just reached 0
        if (count.innerText <= 0) {
            this.parentNode.removeChild(this)
        }

        // Get hitbox size of furniture
        dragFurniture.hitboxX = parseInt(this.getAttribute('data-hitX'))
        dragFurniture.hitboxY = parseInt(this.getAttribute('data-hitY'))

        // Store copy elem
        dragFurniture.elem = copy;
        console.log(dragFurniture.elem);

        // Make the copy draggable:
        dragFurniture.dragElement(event);
    }

    static clickPlacedFurniture(event) {
        const re = RegExp("\\d+ / \\d+ / span (\\d+) / span (\\d+)")
        const matches = re.exec(this.style.gridArea)
        dragFurniture.hitboxX = parseInt(matches[1])
        dragFurniture.hitboxY = parseInt(matches[2])

        dragFurniture.elem = this

        // Make the elem draggable:
        dragFurniture.dragElement(event);
    }

    static dragElement(event) {
        var elem = dragFurniture.elem;
        // Set correct (about) height & width for draggable div
        var tile = document.getElementById('tile_1_1').firstElementChild;
        var width = tile.width * dragFurniture.hitboxX;
        var height = tile.height * dragFurniture.hitboxY;
        elem.style.width = width + "px";
        elem.style.height = height + "px";

        // class = draggable at correct position
        elem.setAttribute('class', 'draggable');
        var rect = elem.getBoundingClientRect()
        elem.style.top = (event.clientY - height/2) + "px";
        elem.style.left = (event.clientX - width/2) + "px";
        document.body.append(elem);

        // Start the drag
        dragFurniture.dragMouseDown(event);
    }

    static dragMouseDown(e) {
        e.preventDefault();
        // get the mouse cursor position at startup:
        dragFurniture.pos3 = e.clientX;
        dragFurniture.pos4 = e.clientY;
        document.onmouseup = dragFurniture.closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = dragFurniture.elementDrag;
    }

    static elementDrag(e) {
        e.preventDefault();
        // calculate the new cursor position:
        dragFurniture.pos1 = dragFurniture.pos3 - e.clientX;
        dragFurniture.pos2 = dragFurniture.pos4 - e.clientY;
        dragFurniture.pos3 = e.clientX;
        dragFurniture.pos4 = e.clientY;
        // set the element's new position:
        dragFurniture.elem.style.top = (dragFurniture.elem.offsetTop - dragFurniture.pos2) + "px";
        dragFurniture.elem.style.left = (dragFurniture.elem.offsetLeft - dragFurniture.pos1) + "px";
    }

    static closeDragElement(e) {
        // stop moving when mouse button is released:
        dragFurniture.elem.onmousedown = dragFurniture.dragElement;   // set onmousedown
        document.onmouseup = null;
        document.onmousemove = null;
        // Get grid location of elem
        var offsetX = parseFloat(dragFurniture.elem.style.width)/(dragFurniture.hitboxX*2);
        var offsetY = parseFloat(dragFurniture.elem.style.height)/(dragFurniture.hitboxY*2);
        var gridloc = document.elementsFromPoint(parseFloat(dragFurniture.elem.style.left) + offsetX, 
                                                 parseFloat(dragFurniture.elem.style.top) + offsetY);
        var gridX, gridY = null;
        var matched = false;
        const re = new RegExp("tile_(\\d+)_(\\d+)")
        gridloc.forEach((elt) => {
            var matches = re.exec(elt.id);
            if (matches) {
                gridX = parseInt(matches[1]);
                gridY = parseInt(matches[2]);
                matched = true;
            }
          });
        if (!matched || gridX + dragFurniture.hitboxX > 21 || gridY + dragFurniture.hitboxY > 21) {
            if (matched) {
                console.log("Out of Bounds: ", gridX + dragFurniture.hitboxX, gridY + dragFurniture.hitboxY)
            }
            return;
        }
        dragFurniture.elem.onmousedown = dragFurniture.clickPlacedFurniture;   // placement completed
        console.log("Furniture moved to: ", gridX, gridY);
        dragFurniture.elem.style.gridArea = `${gridX} / ${gridY} / span ${dragFurniture.hitboxX} / span ${dragFurniture.hitboxY}`
        dragFurniture.elem.style.top = null
        dragFurniture.elem.style.left = null
        dragFurniture.elem.style.width = null
        dragFurniture.elem.style.height = null
        // Clear static vars
        dragFurniture.referenceElem = null
        // remove draggable property
        dragFurniture.elem.setAttribute('class', 'placed-furniture');
        var grid = document.getElementById("grid-container");
        grid.append(dragFurniture.elem)
    }

    // Attach events to all furniture & placed furniture to make them movable
    static attachEvents() {
        var nonplaced = Array.from(document.getElementsByClassName("furniture"))
        nonplaced.forEach((furn) => {
            furn.addEventListener('mousedown', dragFurniture.clickFurniture)
        })
        var placed = Array.from(document.getElementsByClassName("placed-furniture"))
        placed.forEach((furn) => {
            furn.addEventListener('mousedown', dragFurniture.clickPlacedFurniture)
        })
    }    
}

// ---------------------------- Websockets Stuff ---------------------------- //

class FurnitureHandler {
    static socket = null;
    static collision_list = [];


    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/furniture/data/${myUserID}`
        this.socket = new WebSocket(url)

        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }

        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            console.log("Furniture Websocket Connection Successful")
        }

        // Show a disconnected message when the WebSocket is closed.
        this.socket.onclose = function(event) {
            console.log("WebSocket Disconnected: Trying to Reconnect")
            setTimeout(function() {
                FurnitureHandler.connectToServer()
            }, 1000);
        }

        // Handle messages received from the server. (Should not recieve anything other than error / confirmed messages)
        this.socket.onmessage = function(event) {
            let response = JSON.parse(event.data)
            displayResponse(response)
        }
    }

    static sendUpdates() {
        displayError("")    // clear error
        var placed = Array.from(document.getElementsByClassName("placed-furniture"))
        var furnlist = []
        placed.forEach((furn) => {
            const re = RegExp("(\\d+) / (\\d+) / span \\d+ / span \\d+")
            const matches = re.exec(furn.style.gridArea)
            furnlist.push({
                "id": furn.firstElementChild.id, 
                "pos": {
                    "x": parseInt(matches[2]), 
                    "y": parseInt(matches[1])
                },
                "placed": true
            })
        })
        let data = {"action": "update", "furniture-list": furnlist}
        this.socket.send(JSON.stringify(data))
    }

    static attachEvents() {
        var saveButton = document.getElementById("save")
        saveButton.addEventListener('click', function () {
            FurnitureHandler.sendUpdates()
        })
    }
    
}

FurnitureHandler.connectToServer();