"use strict"

class FriendHandler {
    static socket = null;
    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    
        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/friends/data/${myUserID}` // myUserID defined in home.html
        this.socket = new WebSocket(url)
    
        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }
    
        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            console.log("Friend WebSocket Connected")
            displayMessage("")
        }
    
        // Show a disconnected message when the WebSocket is closed & try to reconnect
        this.socket.onclose = function(event) {
            displayMessage("Friend WebSocket Disconnected: Trying to Reconnect")
            setTimeout(function() {
                FriendHandler.connectToServer()
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
            if (Array.isArray(response)) {
                FriendHandler.updateFriendList(response)
                //auto scroll to bottom (with newest messages)
                let elem = document.getElementById('friends-list');    
                elem.scrollTop = elem.scrollHeight;
            } else {
                displayResponse(response)
            }
        }
    }

    static updateFriendList(friends) {
        // Get the friend list
        let friends_list = document.getElementById("friends-list")
        // Adds each new message received from the server to the list
        friends.forEach(friend => {
            if (!document.getElementById(`id_friend_div_${friend.id}`)) {
                friends_list.append(FriendHandler.makeFriendDiv(friend))
            }
        })
    }

    // Builds a new HTML "div" element for each message
    static makeFriendDiv(friend) {
        let friend_name= `<a class="home-inline" id="id_friend_home_${friend.id}" href="${otherHomeURL(friend.id)}">${friend.player_name}</a>`
        let friend_pfp = `<img src="/static/${friend.picture}" width="50" class="pixel-art">`
        
        let friend_div = document.createElement("div")
        friend_div.id = `id_friend_div_${friend.id}`
        friend_div.innerHTML = `${friend_pfp} ${friend_name}`
        

        return friend_div
    }

    // NOTE: other side of sending friend requests here
    static sendRequest(element) {
        displayError("")    // clear error
        let data = {"action": "add", "name": element.value}
        element.value = ""  // clear input box
        this.socket.send(JSON.stringify(data))
    }

    // NOTE: other side of sending friend requests here
    static attachEvents() {
        let search_input = document.getElementById('search-friend-input')
        search_input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                if (search_input.value) {
                    FriendHandler.sendRequest(search_input)   // sends request with friend-search-text
                }
            }
        })
        let search_button = document.getElementById('search-friend-button')
        search_button.addEventListener('click', function() {
            console.log("Button Q clicked")
            if (search_input.value) {
                FriendHandler.sendRequest(search_input)   // sends request with friend-search-text
            }
        })
    }
}

FriendHandler.connectToServer();
