from _socket import SO_REUSEADDR, SOL_SOCKET
from libs.FlightGear import FlightGear
import sys
from libs.SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import subprocess
from threading import Thread, Event
from multiprocessing import Process, freeze_support
import SimpleHTTPServer
import SocketServer
import os
from datetime import datetime

flightgear_cc_port = 8888
flightgear_ws_port = 8778
flightgear_server = "127.0.0.1"
flightgear_server_port = 5555
log = False
fg = None
child_process = None
what_to_log = ""
log_filename = "log.csv"
flightgear_path = "C:\Program Files\FlightGear 3.4.0"
cancel_logger_instance = None

# orientation = fg['/orientation[0]/alpha-deg']
# print "Alpha Deg %.5f" % (fg['/orientation[0]/alpha-deg'])

def get(parent, property):
    return unicode(fg["/" + parent + "[0]/" + property])


def handle_request(what):
    if what == "altitude":
        return get("position", "altitude-ft")
    elif what == "pitch":
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
    elif what == "aileron":
        return get("controls[0]/flight", "aileron")
    elif what == "aileron-trim":
        return get("controls[0]/flight", "aileron-trim")
    elif what == "elevator":
        return get("controls[0]/flight", "elevator")
    elif what == "elevator-trim":
        return get("controls[0]/flight", "elevator-trim")
    elif what == "rudder":
        return get("controls[0]/flight", "rudder")
    elif what == "rudder-trim":
        return get("controls[0]/flight", "rudder-trim")
    elif what == "flaps":
        return get("controls[0]/flight", "flaps")
    elif what == "wing-sweep":
        return get("controls[0]/flight", "wing-sweep")
    elif what == "vertical-speed":
        return get("velocities", "vertical-speed-fps")
    elif what == "airspeed":
        return get("velocities", "airspeed-kt")
    elif what == "groundspeed":
        return get("velocities", "groundspeed-kt")
    elif what == "glideslope":
        return get("velocities", "glideslope")
    elif what == "mach":
        return get("velocities", "mach")
    elif what == "rpm":
        return get("engines[0]/engine", "rpm")
    elif what == "prop-thrust":
        return get("engines[0]/engine", "prop-thrust")
    elif what == "thrust":
        return get("engines[0]/engine", "thrust-lbs")
    elif what == "torque":
        return get("engines[0]/engine", "torque-ftlb")
    elif what == "fuel-consumed":
        return get("engines[0]/engine", "fuel-consumed-lbs")
    elif what == "gross-weight":
        return get("yasim", "gross-weight-lbs")
    else:
        return unicode("error:Requested parameter not found")


def handle_log(interval, csv):
    global log_filename
    log_filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S') + ".csv"
    csv = "".join(csv.split())
    parameters = csv.split(",")
    logging_worker(interval, csv, parameters)
    values = []
    for what in parameters:
        values.append(str(handle_request(what)))
    print "Logging_started" + ",".join(values)
    return unicode("Parameter logging started.")


def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    Thread(target=loop).start()
    return stopped.set


def write_param_to_file(parameters):
    global log_filename
    values = []
    for what in parameters:
        values.append(str(handle_request(what)))
    with open(log_filename, "a") as log_file:
        param_str = ",".join(values)
        # print "[INFO] Written to log:" + param_str
        log_file.write(param_str + "\n")


def logging_worker(interval, csv, parameters):
    global what_to_log
    global log_filename
    global cancel_logger_instance
    print 'Starting to log'
    if not os.path.exists("logs"):
        os.makedirs("logs")
    os.chdir("logs")
    with open(log_filename, "a") as log_file:
        log_file.write(csv + "\n")
    cancel_logger_instance = call_repeatedly(float(interval), write_param_to_file, parameters)


def cancel_logger():
    cancel_logger_instance()
    return unicode("Logging has been terminated")


class SocketHandler(WebSocket):
    def handleMessage(self):
        global fg
        global child_process
        global flightgear_path
        fg_connected = fg is not None
        if self.data == "connect":
            if not fg_connected:
                try:
                    fg = FlightGear(flightgear_server, flightgear_server_port)
                    print self.address, 'Connected to FlightGear via telnet on port ' + str(flightgear_server_port)
                    self.sendMessage(unicode("Connected to FlightGear via telnet on port 9000"))
                except:
                    self.sendMessage(unicode("error:Cannot connect to FlightGear. Try the start command."))
            else:
                self.sendMessage(unicode("Already connected to FlightGear"))
        elif self.data == "exit":
            sys.exit()

        elif self.data.startswith("set_path:"):
            input_cmd_str = self.data.replace("set_path:", "")
            if input_cmd_str is not None:
                if input_cmd_str != "":
                    flightgear_path = input_cmd_str

            self.sendMessage(unicode("FlightGear path has been set."))

        elif self.data == "start fg":
            # command = '"' + flightgear_path + '\\bin\\fgfs.exe" --fg-root="' + flightgear_path +'\data" --fg-scenery="' + flightgear_path + '\data\Scenery"; --aircraft=Cub --disable-random-objects --prop:/sim/rendering/random-vegetation=false --disable-ai-models --disable-ai-traffic --disable-real-weather-fetch --geometry=800x600 --bpp=32 --disable-terrasync --timeofday=noon --disable-fgcom --telnet=socket,out,30,localhost,5555,udp;'
            subprocess.Popen([flightgear_path + '\\bin\\fgfs.exe',
                              '--fg-root=' + flightgear_path + '\\data',
                              '--fg-scenery=' + flightgear_path + '\\data\\Scenery',
                              '--aircraft=Cub',
                              '--disable-random-objects',
                              '--prop:/sim/rendering/random-vegetation=false',
                              '--disable-ai-models',
                              '--disable-ai-traffic',
                              '--disable-real-weather-fetch',
                              '--geometry=800x600',
                              '--bpp=32',
                              '--fdm=yasim',
                              '--wind=0@0',
                              '--turbulence=0',
                              '--disable-terrasync',
                              '--timeofday=noon',
                              '--disable-fgcom',
                              '--telnet=socket,out,30,localhost,5555,udp'])

            self.sendMessage(unicode("FlightGear has been started."))
        elif self.data.startswith("log:"):
            if fg_connected:
                input_cmd_str = self.data.replace("log:", "")
                input_cmd_str = input_cmd_str.split(":")
                self.sendMessage(handle_log(input_cmd_str[0], input_cmd_str[1]))
            else:
                self.sendMessage(unicode("error:Please connect to FlightGear before sending commands"))
        elif self.data == "stop_log":
            self.sendMessage(cancel_logger())
        else:
            if fg_connected:
                self.sendMessage(handle_request(self.data))
            else:
                self.sendMessage(unicode("error:Please connect to FlightGear before sending commands"))

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


def start_http_server():
    os.chdir("ui")
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", flightgear_cc_port), handler)
    httpd.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    print "\nStarted HTTP Server. Goto http://localhost:" + str(flightgear_cc_port) + "/ on your browser\n"
    httpd.serve_forever()


def start_ws_server():
    server = SimpleWebSocketServer("", flightgear_ws_port, SocketHandler)
    print "\nStarted Web Socket Server on port " + str(flightgear_ws_port) + "\n"
    server.serveforever()


if __name__ == "__main__":
    freeze_support()
    print "\nStarting bridge\n"
    http_process = Process(target=start_http_server)
    ws_process = Process(target=start_ws_server)

    http_process.start()
    ws_process.start()
    print "\nPowering up.\n"
    raw_input("")







