from FlightGear import FlightGear
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
import sys
from string import whitespace

log = False
fg = None

# orientation = fg['/orientation[0]/alpha-deg']
# print "Alpha Deg %.5f" % (fg['/orientation[0]/alpha-deg'])

def get(parent, property):
    return unicode(fg["/" + parent + "[0]/" + property])

def handle_request(what):
    if what == "pitch":
        return get("orientation", "pitch-deg")
    elif what == "heading":
        return get("orientation", "heading-deg")
    elif what == "roll":
        return get("orientation", "roll-deg")
    elif what == "alpha":
        return get("orientation", "alpha-deg")
    elif what == "beta":
        return get("orientation", "beta-deg")
    elif what == "yaw":
        return get("orientation", "yaw-deg")
    elif what == "path":
        return get("orientation", "path-deg")
    elif what == "roll-rate":
        return get("orientation", "roll-rate-degps")
    elif what == "pitch-rate":
        return get("orientation", "pitch-rate-degps")
    elif what == "yaw-rate":
        return get("orientation", "yaw-rate-degps")
    elif what == "side-slip":
        return get("orientation", "side-slip-deg")
    elif what == "track":
        return get("orientation", "track-deg")
    elif what == "p-body":
        return get("orientation", "p-body")
    elif what == "q-body":
        return get("orientation", "p-body")
    elif what == "r-body":
        return get("orientation", "p-body")
    else:
        return unicode("error:Requested parameter not found")


def handle_log(csv):
    csv = "".join(csv.split())
    return unicode(csv)


class SocketHandler(WebSocket):
    def handleMessage(self):
        global fg
        fg_connected = fg is not None
        if self.data == "connect":
            if not fg_connected:
                try:
                    fg = FlightGear('127.0.0.1', 9000)
                    print self.address, 'Connected to FlightGear via telnet on port 9000'
                    self.sendMessage(unicode("Connected to FlightGear via telnet on port 9000"))
                except:
                    self.sendMessage(unicode("error:Cannot connect to FlightGear. Try the start command."))
            else:
                self.sendMessage(unicode("Already connected to FlightGear"))
        elif self.data == "exit":
            sys.exit()
        elif self.data.startswith("log:"):
            if fg_connected:
                self.sendMessage(handle_log(self.data.replace("log:", "")))
            else:
                self.sendMessage(unicode("error:Please connect to FlightGear before sending commands"))
        else:
            if fg_connected:
                self.sendMessage(handle_request(self.data))
            else:
                self.sendMessage(unicode("error:Please connect to FlightGear before sending commands"))

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


server = SimpleWebSocketServer('', 8000, SocketHandler)
server.serveforever()