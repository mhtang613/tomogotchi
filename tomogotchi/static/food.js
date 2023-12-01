"use strict"

function toggleFood() {
    const foodBar = document.getElementById("food-bar");
    const shrinkButton = document.getElementById("shrink-button");
    const home = document.getElementById("grid-container")

    foodBar.classList.toggle("collapsed");
    shrinkButton.innerHTML = foodBar.classList.contains("collapsed") ? "Food &#9650;" : "Food &#x25BC;";
//     home.style.maxHeight = foodBar.classList.contains("collapsed") ? "80vh" : "75vH";
//     home.style.maxWidth = foodBar.classList.contains("collapsed") ? "80vh" : "75vH";
}

function restoreFood() {
    const foodBar = document.getElementById("food-bar");
    const shrinkButton = document.getElementById("shrink-button");
    const home = document.getElementById("grid-container")

    foodBar.classList.remove("collapsed");
    shrinkButton.innerHTML = "Food &#x25BC;";
    // home.style.maxHeight = "75vh";
    // home.style.maxWidth = "75vh";
}

class FoodHandler {
    static socket = null;
    static connectToServer() {
        // Use wss: protocol if site using https:, otherwise use ws: protocol
        let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    
        // Create a new WebSocket.
        let url = `${wsProtocol}//${window.location.host}/food/data/${myUserID}`
        this.socket = new WebSocket(url)
    
        // Handle any errors that occur.
        this.socket.onerror = function(error) {
            console.log("WebSocket Error: " + error)
        }
    
        // Show a connected message when the WebSocket is opened.
        this.socket.onopen = function(event) {
            console.log("Food WebSocket Connected")
        }
    
        // Show a disconnected message when the WebSocket is closed & try to reconnect
        this.socket.onclose = function(event) {
            console.log("Food WebSocket Disconnected: Trying to Reconnect")
            setTimeout(function() {
                FoodHandler.connectToServer()
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
            if (Array.isArray(response.food_list)) {
                FoodHandler.updateFoodList(response)
            } else {
                displayResponse(response)
            }
        }
    }


    static updateFoodList(response) {
        console.log("food.js updateFoodList")
        let food_bar = document.getElementById("food-bar-container")
        response.food_list.forEach(food => {
            let existing_div = document.getElementById(`id_food_div_${food.food_id}`);
            if (!existing_div && food.count > 0) {
                let new_div = FoodHandler.makeFoodDiv(food);
                food_bar.appendChild(new_div)
            } else if (!existing_div && food.count <= 0) {
                // do nothing
            } else {
               console.log(`id, count = ${food.food_id} ${food.count}`);
                if ((food.count) <= 0) {
                    existing_div.remove();
                } else {
                    let count_div = document.getElementById(`id_count_food_div_${food.food_id}`);
                    count_div.innerHTML = food.count;   
                }
            }
        })

        let food_meter = document.getElementById("hunger");
        if (!food_meter) {
            food_meter.value = food_meter.value + response.hunger;
        }
    }

    static makeFoodDiv(food) {
        console.log("food.js makeFoodDiv")
        let foodDiv = document.createElement("div")
        foodDiv.id = `id_food_div_${food.food_id}`
        foodDiv.className = "food-elem"

        let img = document.createElement("img")
        img.className = "food-elem";
        img.id = food.food_id;
        img.src = `/get-item-picture/${food.name}`;

        let countDiv = document.createElement("div")
        countDiv.innerHTML = food.count;
        countDiv.className = "counter-circle"
        countDiv.id = `id_count_food_div_${food.food_id}`

        foodDiv.appendChild(img);
        foodDiv.appendChild(countDiv);
        foodDiv.addEventListener('click', function() {
            FoodHandler.sendUseFoodRequest(food.food_id)
        })
        return foodDiv;
    }

    static sendUseFoodRequest(food_id) {
        console.log("food.js sendUseFoodRequest")
        let data = {"action": "use-food", "food_id": food_id}
        console.log(`using food id ${food_id}`)
        this.socket.send(JSON.stringify(data))
    }

    
    // static attachEvents() {
    //     let foodElements = document.querySelectorAll('.food-elem')
    //     let foodArray = Array.from(foodElements)
    //     foodArray.forEach((food_elem) => {
    //         food_elem.addEventListener('click', function() {
    //             FoodHandler.sendUseFoodRequest(food_elem.id)
    //         })
    //     })
    // }
}

FoodHandler.connectToServer();
