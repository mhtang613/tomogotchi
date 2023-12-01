"use strict"

class ShopHandler {
    static socket = null;
    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    
        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/shop/data`
        this.socket = new WebSocket(url)
    
        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }
    
        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            console.log("Shop WebSocket Connected")
        }
    
        // Show a disconnected message when the WebSocket is closed & try to reconnect
        this.socket.onclose = function(event) {
            displayMessage("Shop WebSocket Disconnected: Trying to Reconnect")
            setTimeout(function() {
                ShopHandler.connectToServer()
            }, 1000);
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
            
        }
    }

    static sendBuyItemRequest(item_id) {
        let data = {"action": "buy-item", "item_id": item_id}
        console.log(`${item_id}`)
        this.socket.send(JSON.stringify(data))
    }

    
    static attachEvents() {
        let buy_button = document.getElementById('buy-button')
        buy_button.addEventListener('click', function() {
            console.log("Buy-button clicked")

            let selectedIcon = document.querySelector('.icon[style*="border: 2px solid red;"]');
            if (selectedIcon) {
                ShopHandler.sendBuyItemRequest(selectedIcon.id)
            }
        })

    }
}

ShopHandler.connectToServer();
