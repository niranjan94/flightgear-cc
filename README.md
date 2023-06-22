## FlightGear Command Center 

> This project is not currently under active maintenance.


<p style="float: left">
<img src="https://res.cloudinary.com/niranjan94/image/upload/f_auto,q_auto/v1/Personal/flightgear-cc-dashboard" height="210"/>
<img src="https://res.cloudinary.com/niranjan94/image/upload/f_auto,q_auto/v1/Personal/flightgear-cc-parameters" height="210"/>
</p>


A user-friendly tool based on Python and JavaScript, designed to offer a more intuitive interaction with the FlightGear flight simulator. Born out of a need to navigate FlightGear's complex PropertyTree, API, and limited documentation, this project aims to streamline the experience for beginners and experienced users alike.

Given the challenging nature of FlightGear's system, my goal was to make it accessible for individuals with little or no programming knowledge, simplifying exploration of various FlightGear features and consuming its API.

### Features

The FlightGear Interface enhances user interaction by offering the following functionalities:

1. **Live Parameters Monitoring**: Facilitates the real-time viewing of various aircraft and simulation parameters.
2. **Easy Parameter Selection and Logging**: Enables users to effortlessly select and log various parameters for easier tracking and analysis.

Even though the project isn't actively maintained currently, we hope you find the existing features helpful in navigating and understanding FlightGear and its API better.

### Usage

#### Requirements
1. [Python 3.8+](https://www.python.org/) - Runtime
2. A [virtual environment](https://docs.python.org/3/library/venv.html) (Highly Recommended!)
3. [FlightGear](https://www.flightgear.org/download/) - 2020.3 or above recommended.

#### Setup

```bash
# Clone the repository
git clone git@github.com:niranjan94/flightgear-cc.git
cd flightgear-cc

# Install dependencies
pip install -r requirements.txt
```

#### Run the app

```bash
python -m flightgear_bridge.asgi
```

#### Build a self-contained binary (Optional)

[PyInstaller](https://www.pyinstaller.org/) is used to build a self-contained binary for the app. The binary will be available in the `dist` folder.

```bash
pyinstaller flightgear_bridge.spec
```

### Features Ideas

If you're interested in contributing to this project, here are some ideas to get you started:

1. Select aircraft, airport and various other settings
2. Change parameters in real time while Flight Gear is running
3. Provide external API for other apps to communicate easily with FlightGear.
4. Improve the throughput of the logging system to get more real time data.
5. Explore alternatives to the telnet interface (If a better one exists to get data feeds)
6. Upgrade and replace frontend asset files in repo with external CDN urls.

To suggest a new feature, please [open a new issue](https://github.com/niranjan94/flightgear-cc/issues/new), with the label **feature request**.


## Open Source License ##

Unless explicitly stated otherwise all files in this repository are licensed under the [Apache Software License 2.0](http://choosealicense.com/licenses/apache-2.0/). All projects must properly attribute [The Original Source](https://github.com/niranjan94/flightgear-cc).
    
    Copyright 2023 Niranjan Rajendran
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
