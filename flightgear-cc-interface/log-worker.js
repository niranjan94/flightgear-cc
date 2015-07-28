self.addEventListener('message', function(e) {
    var data = e.data;
    switch (data.cmd) {
        case 'start':
            self.postMessage('WORKER STARTED: ' + data.msg);
            break;
        case 'stop':
            self.postMessage('WORKER STOPPED:');
            self.close();
            break;
        default:
            self.postMessage('Unknown command: ' + data.msg);
    }
}, false);

function saveFile(filename, data){
    var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
    saveAs(blob, filename+".csv");
}