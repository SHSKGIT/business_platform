/*
sign up form
**********************************************************************/
$('#purchase-button').click(function () {
    var user_id = document.getElementById('user-id').getAttribute('data-user-id');  // Pass the user's ID from the template
    // if using HTTP, websocket without SSL
    var socket_url = 'ws://' + window.location.host + ':8002/ws/purchase/' + encodeURIComponent(user_id) + '/';
    // if using HTTPS, websocket with SSL
//    var socket_url = 'wss://' + window.location.host + ':8002/ws/purchase/' + encodeURIComponent(user_id) + '/';
    var socket = new WebSocket(socket_url);

    socket.onopen = function(event) {
        // Optionally send a message to the server
        socket.send(JSON.stringify({type: 'greeting', user_id: user_id}));
    };

    // once receive a message from websocket server
    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        if (data.message) {
//            alert('Your purchase status is now: ' + data.message);
            document.getElementById('user-name').innerHTML = data.message;
        }
    };

    socket.onclose = function(event) {
        console.error('WebSocket closed unexpectedly');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
});
