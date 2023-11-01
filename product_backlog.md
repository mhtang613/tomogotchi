# Product Backlog
1. Registering and logging in with Django and OAuth authentication
    * Players will be able to login to the website with OAuth authentication. This will create Player instances in a Player model that shadows Django’s default User model.
    * If the player does not already have an account: 
        * New Players will first see a egg-hatching animation in their home page.
        * New Players are given a random username but can edit it to any non-existing/unique username at any time from their house.
2. Modifying database models for Player, House, Items, Messages using Django
    * Player model - This contains all of the information unique to a player, including their corresponding house, inventory, friends, and more.
    * House model - This contains all of the information for a single player’s house, including all of the player’s furniture and the displayed furniture, messages, and active visitors.
    * Items model - This contains all of the available food items in the game, including their picture.
    * Furniture model - This contains all of the available furniture items, including a picture, dimensions, and location in a house.
    * Messages model - This contains all of the messages sent at all houses, including which house it was sent at and the sender.
3. Visiting houses using HTML
    * Each house will display the user’s placed furniture and a message boar and the current user’s friend list.
    * Each own house will also have links to editing
    * Users can visit their friend’s houses by clicking on links to their house from the displayed friend’s list.
4. Interacting with others using WebSockets and JavaScript
    * WebSockets are used to instantly update all interactions, such as message boards, friend requests, visiting players, and updating furniture layouts. 
        * This includes detecting when pets collide with newly placed furniture & when furniture collides with existing furniture.
        * When making a friend request, the other player is added to your friend’s list, and they also receive a system notification in their message box and can mutually add the other player.
    * Pets will be stationary in houses, but animated with JavaScript and SpriteJS.
5. Placing furniture
    * Players will be able to go to a separate “editing” page where they can view their inventory bar of furniture and a layout of their house. They can drag and drop furniture to place it, aligned to a grid.
    * After pressing a “save” button, users will be redirected to their home page with the updated furniture. The user’s pet and all other pets previously in the house will be moved to avoid collisions.
6. Displaying different views/rooms and users with HTML, CSS, and spritejs libraries
    * We will draw sprites or take premade sprite gifs and animate them
    * Players can transition between views with links/buttons.
7. Deploying to cloud
    * We will deploy Tomogotchi using EC2, Daphne, and MySql
