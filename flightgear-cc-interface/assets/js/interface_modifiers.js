function bridgeConnectButton (connect){
    var btn = $("#bridge-connect-btn");
    btn.enable();
    if(connect){
        btn.html("Connect to Bridge");
        btn.addClass("btn-success").removeClass("btn-danger");
        $("#flight-gear-controls").hide();
        $("#flight-gear-parameter-controls").hide();
    } else {
        btn.html("Disconnect from Bridge");
        btn.removeClass("btn-success").addClass("btn-danger");
        $("#flight-gear-controls").show();
        $("#flight-gear-parameter-controls").show();
    }
}

function loggingButton(turnOnAllowed){
    var $stopLogBtn = $("#stop-logging-btn");
    var $startLogBtn = $("#logging-select-btn");
    if(turnOnAllowed){
        $startLogBtn.removeClass("hidden");
        $stopLogBtn.addClass("hidden");
    } else {
        $startLogBtn.addClass("hidden");
        $stopLogBtn.removeClass("hidden");
    }
}