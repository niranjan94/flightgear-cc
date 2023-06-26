var socket;
var terminal = null;
var flag = false;
var disconnect_flag = false;
var isConnected = false;
var roll = 0;
var pitch = 0;
function connectToSocket() {
    loading(true);
    socket = new WebSocket("ws://" + window.location.host + "/api/v1/websocket");
    socket.onopen = function(evt) { onOpen(evt) };
    socket.onclose = function(evt) { onClose(evt) };
    socket.onmessage = function(evt) { onMessage(evt) };
    socket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
    loading(false);
    bridgeConnectButton(false);
    terminal.resume();
    terminal.clear();
    flag = true;
    isConnected = true;
}

function onClose(evt) {
    bridgeConnectButton(true);
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
    bridgeConnectButton(true);
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
            switch (command){
                case "help":
                    terminal.echo("Help function will be added shortly");
                    break;
                case "reconnect":
                    terminal.pause();
                    connectToSocket();
                    break;
                case "disconnect":
                    terminal.pause();
                    socket.close();
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

    $("#flight-gear-controls").hide();
    $("#flight-gear-parameter-controls").hide();
    $("#bridge-connect-btn").click(function () {
        $(this).disable();
        if(isConnected){
            terminal.exec("disconnect");
        } else {
            terminal.exec("reconnect");
        }

    }).disable();

    $("#flight-gear-connect-btn").click(function () {
        terminal.exec("connect fg");
    });

    $("#flight-gear-open-btn").click(function () {
        terminal.exec("set_path:" + localStorage.getItem("flightgear_path"));
        terminal.exec("start fg");
    });

    $("#single-parameter").submit(function (e) {
        e.preventDefault();
        terminal.exec($("select[name=parameter]").val());
    });

    $("#start-log-btn").click(function () {
        var csv = $('.parameters-checkbox:checked').map(function() {return this.value;}).get().join(',');
        var timeInterval = $("#logging-interval").val();
        terminal.exec("log:"+timeInterval+":"+csv);
        loggingButton(false);
    });

    var $setPathModal = $('#flightgear-path-modal');
    var $fgPath = $("#fg-path");

    $setPathModal.modal({
        backdrop : "static",
        keyboard: "false",
        show: false
    });

    if(localStorage.getItem("flightgear_path") == null || localStorage.getItem("flightgear_path") == ""){
        $setPathModal.modal("show");
        $fgPath.val('');
        fetch("/api/v1/flightgear-path").then(function (response) {
            return response.json();
        }).then(function (data) {
            $fgPath.val(data.path);
        })
    } else {
        $setPathModal.modal("hide");
        $fgPath.val(localStorage.getItem("flightgear_path"));
    }

    $("#fg-path-submit").click(function () {
        localStorage.setItem("flightgear_path", $fgPath.val())
    });

    $("#stop-logging-btn").click(function(){
        terminal.exec("stop_log");
        loggingButton(true);
    });


    $(".parameters-checkbox").change(function () {
        updateLoggingStatus();
    });

    $("#logging-interval").bind("propertychange change click keyup keypress input paste", function(event){
        updateLoggingStatus();
    });

});

function updateLoggingStatus(){
    var $loggingStatus = $("#logging-status");

    var param_count = parseFloat($('.parameters-checkbox:checked').length);
    var interval = parseFloat($("#logging-interval").val());

    var freq = param_count/interval;

    if(freq<=30){
        $loggingStatus.removeClass("text-danger").addClass("text-success").text("(logging will occur normally)")
    } else {
        $loggingStatus.addClass("text-danger").removeClass("text-success").text("(logging might be delayed)")
    }

}

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