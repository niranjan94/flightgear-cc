var socket;
var terminal = null;
var flag = false;
var disconnect_flag = false;
var isConnected = false;
function connectToSocket() {
    loading(true);
    socket = new WebSocket("ws://localhost:8000/");
    socket.onopen = function(evt) { onOpen(evt) };
    socket.onclose = function(evt) { onClose(evt) };
    socket.onmessage = function(evt) { onMessage(evt) };
    socket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
    loading(false);
    terminal.resume();
    terminal.clear();
    flag = true;
    isConnected = true;
}

function onClose(evt) {
    isConnected = false;
    loading(false);
    terminal.resume();
    if(disconnect_flag){
        disconnect_flag = false;
        terminal.echo("You have been disconnected from the bridge.");
        terminal.echo("Use reconnect command to continue.")
    } else if(flag) {
        terminal.error("Connection was lost with the bridge.");
        terminal.error("Use reconnect command to continue.")
    }
}

function onMessage(evt) {
    writeToConsole(evt.data);
}

function onError(evt) {
    isConnected = false;
    terminal.resume();
    loading(false);
    if(flag){
        terminal.error("Connection was lost with the bridge.");
        terminal.error("Use reconnect command to continue.")
    } else {
        terminal.error("Connection could not be established.");
        terminal.error("Start the bridge and use reconnect command to continue.\n");
    }
    socket.close();
}

function writeToConsole(message) {
    terminal.resume();
    loading(false);
    if(message.startsWith("error:")){
        terminal.error(message.replace("error:",""));
    } else {
        terminal.echo(message);
    }
}

function send(message) {
    terminal.pause();
    loading(true);
    socket.send(message);
}

$(document).ready(function () {
    connectToSocket();
    terminal = $('#console').terminal(function(command, term) {
        if (command !== '') {
            command = command.toLowerCase().trim();
            switch (command){
                case "help":
                    terminal.echo("Help function will be added shortly");
                    break;
                case "reconnect":
                    terminal.pause();
                    connectToSocket();
                    break;
                case "exit":
                    disconnect_flag = true;
                    send("exit");
                    break;
                default:
                    if(isConnected){
                        send(command);
                    } else {
                        writeToConsole("error:Please connect to bridge first");
                    }

            }

        } else {
            term.error('Please enter a command. Or type help.');
        }
    },{
        greetings: 'Connecting to bridge...',
        name: 'console',
        height: 400,
        exit: false,
        prompt: '# '});
    terminal.pause();



});

if (typeof String.prototype.startsWith != 'function') {
    // see below for better implementation!
    String.prototype.startsWith = function (str){
        return this.indexOf(str) === 0;
    };
}

function loading(state){
    if(state){
        $(".spinner").fadeIn(100);
    } else {
        $(".spinner").fadeOut(100);
    }
}