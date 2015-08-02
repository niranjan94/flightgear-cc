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
import shutil

flightgear_cc_port = 8888
flightgear_ws_port = 8778
flightgear_server = "127.0.0.1"
flightgear_server_port = 5555
flightgear_process = None
log = False
fg = None
fg_connected = False
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
    #
    # POSITION & GPS
    #
    if what == "altitude":
        return get("position", "altitude-ft")
    elif what == "odometer":
        return get("instrumentation[0]/gps", "odometer")
    #
    # ORIENTATION
    #
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
    #
    # CONTROL SURFACES
    #
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
    #
    # VELOCITIES
    #
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
    elif what == "u":
        return get("fdm[0]/jsbsim[0]/velocities", "u-fps")
    elif what == "v":
        return get("fdm[0]/jsbsim[0]/velocities", "v-fps")
    elif what == "w":
        return get("fdm[0]/jsbsim[0]/velocities", "w-fps")
    elif what == "p":
        return get("fdm[0]/jsbsim[0]/velocities", "p-rad_sec")
    elif what == "q":
        return get("fdm[0]/jsbsim[0]/velocities", "q-rad_sec")
    elif what == "r":
        return get("fdm[0]/jsbsim[0]/velocities", "r-rad_sec")
    #
    # ACCELERATIONS
    elif what == "u-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "udot-ft_sec2")
    elif what == "v-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "vdot-ft_sec2")
    elif what == "w-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "wdot-ft_sec2")
    elif what == "p-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "pdot-rad_sec2")
    elif what == "q-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "qdot-rad_sec2")
    elif what == "r-dot":
        return get("fdm[0]/jsbsim[0]/accelerations", "rdot-rad_sec2")
    #
    #
    # ENGINE, THRUST & WEIGHT
    #
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
    elif what == "weight":
        return get("fdm[0]/jsbsim[0]/inertia", "weight-lbs")
    #
    # AERODYNAMIC COEFFICIENTS
    #
    elif what == "CDo":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDo")
    elif what == "CDDf":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDf")
    elif what == "CDwbh":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDwbh")
    elif what == "CDDe":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDe")
    elif what == "CDbeta":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDbeta")
    elif what == "CLwbh":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLwbh")
    elif what == "CLDf":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDf")
    elif what == "CLDe":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDe")
    elif what == "CLadot":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLadot")
    elif what == "CLq":
        return get("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLq")
    elif what == "cl-squared":
        return get("fdm[0]/jsbsim[0]/aero", "cl-squared")
    elif what == "kCDge":
        return get("fdm[0]/jsbsim[0]/aero[0]/function", "kCDge")
    elif what == "kCLge":
        return get("fdm[0]/jsbsim[0]/aero[0]/function", "kCLge")
    #
    # DEFAULT - NOT FOUND
    #
    else:
        return unicode("error:Requested parameter not found")


def handle_log(interval, csv):
    global log_filename

    if fg_connected is not None and fg_connected:
        log_filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S') + ".csv"
        csv = "".join(csv.split())
        parameters = csv.split(",")
        logging_worker(interval, csv, parameters)
        values = []
        for what in parameters:
            values.append(str(handle_request(what)))
        print "Logging_started" + ",".join(values)
        return unicode("Parameter logging started.")
    else:
        return unicode("error:Please connect to FlightGear before sending commands")

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
        global fg_connected
        fg_connected = fg is not None and fg_connected
        if self.data == "connect fg":
            if not fg_connected:
                try:
                    fg = FlightGear(flightgear_server, flightgear_server_port)
                    print self.address, 'Connected to FlightGear via telnet on port ' + str(flightgear_server_port)
                    self.sendMessage(unicode("Connected to FlightGear via telnet on port 9000"))
                    fg_connected = True
                except:
                    self.sendMessage(unicode("error:Cannot connect to FlightGear. Try the start command."))
            else:
                self.sendMessage(unicode("Already connected to FlightGear"))
                fg_connected = True

        elif self.data == "disconnect fg":
            fg.quit()
            fg_connected = False
            print self.address, 'Disconnected from FlightGear '
            self.sendMessage(unicode("Disconnected from FlightGear"))

        elif self.data == "exit":
            http_process.terminate()
            ws_process.terminate()
            sys.exit()

        elif self.data.startswith("set_path:"):
            try:
                input_cmd_str = self.data.replace("set_path:", "")
                if input_cmd_str is not None:
                    if input_cmd_str != "":
                        flightgear_path = input_cmd_str
                try:
                    os.remove(flightgear_path + "\\data\\Aircraft\\c172p\\splash.png")
                except Exception:
                    pass

                shutil.copy("splash.png", flightgear_path + "\\data\\Aircraft\\c172p\\")
                self.sendMessage(unicode("FlightGear path has been set."))
            except Exception as err:
                print type(err)
                print err.args
                print err
                pass

        elif self.data == "start fg":
            # command = '"' + flightgear_path + '\\bin\\fgfs.exe" --fg-root="' + flightgear_path +'\data" --fg-scenery="' + flightgear_path + '\data\Scenery"; --aircraft=Cub --disable-random-objects --prop:/sim/rendering/random-vegetation=false --disable-ai-models --disable-ai-traffic --disable-real-weather-fetch --geometry=800x600 --bpp=32 --disable-terrasync --timeofday=noon --disable-fgcom --telnet=socket,out,30,localhost,5555,udp;'
            try:
                subprocess.Popen([flightgear_path + '\\bin\\fgfs.exe',
                                  '--fg-root=' + flightgear_path + '\\data',
                                  '--fg-scenery=' + flightgear_path + '\\data\\Scenery',
                                  '--aircraft=c172p',
                                  '--disable-random-objects',
                                  '--prop:/sim/rendering/random-vegetation=false',
                                  '--disable-ai-models',
                                  '--disable-ai-traffic',
                                  '--disable-real-weather-fetch',
                                  '--geometry=800x600',  # DISPLAY RESOLUTION
                                  '--model-hz=120'  # FREQUENCY OF THE FDM
                                  '--bpp=32',
                                  '--wind=0@0',  # WIND SPEED AND DIRECTION
                                  '--fog-fastest',
                                  '--turbulence=0',
                                  '--disable-terrasync',
                                  '--timeofday=noon',
                                  '--disable-fgcom',
                                  '--telnet=socket,out,60,localhost,5555,udp'  # TELNET SERVER CONFIGURATION
                                  ])
            except Exception as err:
                print type(err)
                print err.args
                print err
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







