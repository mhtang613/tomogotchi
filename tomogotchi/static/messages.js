"use strict"

class MessageHandler {
    static socket = null
    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/messages/data/${currentRoomID}`
        this.socket = new WebSocket(url)

        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            displayMessage("WebSocket Error: " + error)
        }

        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            console.log("Messages WebSocket Connected")
        }

        // Show a disconnected message when the WebSocket is closed & try to reconnect
        this.socket.onclose = function(event) {
            console.log("WebSocket Disconnected: Trying to Reconnect")
            setTimeout(function() {
                MessageHandler.connectToServer()
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

            MessageHandler.updateMessages(response)
            let elem = document.getElementById('messages-box');    
            elem.scrollTop = elem.scrollHeight;

            

            // if (Array.isArray(response.msg_list)) {
            //     MessageHandler.updateMessages(response)
            //     //auto scroll to bottom (with newest messages)
            //     let elem = document.getElementById('messages-box');    
            //     elem.scrollTop = elem.scrollHeight;
            // } else {
            //     displayResponse(response)
            // }
        }
    }

    static updateMessages(response) {
        let messages = response.msg_list
        // Get the messages container
        let msg_container = document.getElementById("messages-list")
        // Adds each new message received from the server to the container
        messages.forEach(msg => {
            if (!document.getElementById(`id_msg_div_${msg.id}`)) {
                msg_container.append(MessageHandler.makeMessageDiv(msg))
            }
        })

        let mood_meter = document.getElementById("mood");
        mood_meter.value = response.mood;
    }

    // Builds a new HTML "div" element for each message
    static makeMessageDiv(msg) {
        let author_home_link = `<a class="home-inline" id="id_msg_home_${msg.id}" href="${otherHomeURL(msg.user.id)}">${msg.user.player.name}</a>`
        let author_name = `<span class="msg_author"> ${author_home_link}: </span>`
        let msg_text = `<span id="id_msg_text_${msg.id}">${msg.text}</span>`
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

    static sendRequest(element) {
        displayError("")    // clear error
        let data = {"action": "add", "message": element.value}
        element.value = ""  // clear input box
        this.socket.send(JSON.stringify(data))
    }

    static attachEvents() {
        let message_input = document.getElementById('message-input')
        message_input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                if (message_input.value) {
                    MessageHandler.sendRequest(message_input)
                }
            }
        })
    }
}

MessageHandler.connectToServer()
