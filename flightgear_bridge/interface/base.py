import re
from abc import ABC, abstractmethod
from typing import Union

property_dict = {
    #
    # Position & GPS
    #
    "altitude": ("position", "altitude-ft"),
    "odometer": ("instrumentation[0]/gps", "odometer"),
    #
    # Orientation
    #
    "pitch": ("orientation", "pitch-deg"),
    "heading": ("orientation", "heading-deg"),
    "roll": ("orientation", "roll-deg"),
    "alpha": ("orientation", "alpha-deg"),
    "beta": ("orientation", "beta-deg"),
    "yaw": ("orientation", "yaw-deg"),
    "path": ("orientation", "path-deg"),
    "roll-rate": ("orientation", "roll-rate-degps"),
    "pitch-rate": ("orientation", "pitch-rate-degps"),
    "yaw-rate": ("orientation", "yaw-rate-degps"),
    "side-slip": ("orientation", "side-slip-deg"),
    "track": ("orientation", "track-deg"),
    "p-body": ("orientation", "p-body"),
    "q-body": ("orientation", "q-body"),
    "r-body": ("orientation", "r-body"),
    #
    # Control Surfaces
    #
    "aileron": ("controls[0]/flight", "aileron"),
    "aileron-trim": ("controls[0]/flight", "aileron-trim"),
    "elevator": ("controls[0]/flight", "elevator"),
    "elevator-trim": ("controls[0]/flight", "elevator-trim"),
    "rudder": ("controls[0]/flight", "rudder"),
    "rudder-trim": ("controls[0]/flight", "rudder-trim"),
    "flaps": ("controls[0]/flight", "flaps"),
    "wing-sweep": ("controls[0]/flight", "wing-sweep"),
    #
    # Velocities
    #
    "vertical-speed": ("velocities", "vertical-speed-fps"),
    "airspeed": ("velocities", "airspeed-kt"),
    "groundspeed": ("velocities", "groundspeed-kt"),
    "glideslope": ("velocities", "glideslope"),
    "mach": ("velocities", "mach"),
    "u": ("fdm[0]/jsbsim[0]/velocities", "u-fps"),
    "v": ("fdm[0]/jsbsim[0]/velocities", "v-fps"),
    "w": ("fdm[0]/jsbsim[0]/velocities", "w-fps"),
    "p": ("fdm[0]/jsbsim[0]/velocities", "p-rad_sec"),
    "q": ("fdm[0]/jsbsim[0]/velocities", "q-rad_sec"),
    "r": ("fdm[0]/jsbsim[0]/velocities", "r-rad_sec"),
    #
    # Accelerations
    #
    "u-dot": ("fdm[0]/jsbsim[0]/accelerations", "udot-ft_sec2"),
    "v-dot": ("fdm[0]/jsbsim[0]/accelerations", "vdot-ft_sec2"),
    "w-dot": ("fdm[0]/jsbsim[0]/accelerations", "wdot-ft_sec2"),
    "p-dot": ("fdm[0]/jsbsim[0]/accelerations", "pdot-rad_sec2"),
    "q-dot": ("fdm[0]/jsbsim[0]/accelerations", "qdot-rad_sec2"),
    "r-dot": ("fdm[0]/jsbsim[0]/accelerations", "rdot-rad_sec2"),
    #
    # Engine, Thrust & Weight
    #
    "rpm": ("engines[0]/engine", "rpm"),
    "prop-thrust": ("engines[0]/engine", "prop-thrust"),
    "thrust": ("engines[0]/engine", "thrust-lbs"),
    "torque": ("engines[0]/engine", "torque-ftlb"),
    "fuel-consumed": ("engines[0]/engine", "fuel-consumed-lbs"),
    "weight": ("fdm[0]/jsbsim[0]/inertia", "weight-lbs"),
    #
    # Aerodynamic Coefficients
    #
    "CDo": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDo"),
    "CDDf": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDf"),
    "CDwbh": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDwbh"),
    "CDDe": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDDe"),
    "CDbeta": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CDbeta"),
    "CLwbh": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLwbh"),
    "CLDf": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDf"),
    "CLDe": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLDe"),
    "CLadot": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLadot"),
    "CLq": ("fdm[0]/jsbsim[0]/aero[0]/coefficient", "CLq"),
    "cl-squared": ("fdm[0]/jsbsim[0]/aero", "cl-squared"),
    "kCDge": ("fdm[0]/jsbsim[0]/aero[0]/function", "kCDge"),
    "kCLge": ("fdm[0]/jsbsim[0]/aero[0]/function", "kCLge"),
}

special_cases = {
    # Fuel Weight
    "fuel-tank-1": "/fdm[0]/jsbsim[0]/propulsion[0]/tank[0]/" + "contents-lbs",
    "fuel-tank-2": "/fdm[0]/jsbsim[0]/propulsion[0]/tank[1]/" + "contents-lbs",
}


def resolve_property_path(name: str) -> str:
    """Resolve a property name to a property path."""
    if name in property_dict:
        parent_path, property_name = property_dict[name]
        return f"/{parent_path}[0]/{property_name}"

    # Special cases
    if name in special_cases:
        return special_cases[name]

    raise ValueError("Requested parameter not found")


PROPERTY_PARSE_REGEX = re.compile(r"[^=]*=\s*'([^']*)'\s*([^\r]*)")


def parse_raw_value(raw_value: str) -> Union[float, int, str, None]:
    """Parse a raw value from the property tree into a Python type"""
    match = PROPERTY_PARSE_REGEX.match(raw_value)
    if not match:
        return None

    value, data_type = match.groups()
    if value == "":
        return None

    if data_type == "(double)":
        return float(value)
    elif data_type == "(int)":
        return int(value)
    elif data_type == "(bool)":
        if value == "true":
            return 1
        else:
            return 0
    else:
        return value


class BaseInterface(ABC):
    """Base interface for property tree access."""

    async def get_property(
        self, name: str, raw: bool = False
    ) -> Union[float, int, str, None]:
        """Get a property from the property tree."""
        raw_value = await self.get(resolve_property_path(name))
        if raw:
            return raw_value
        return parse_raw_value(raw_value)

    async def set_property(self, name: str, value: str):
        """Set a property in the property tree."""
        return await self.set(resolve_property_path(name), value)

    @abstractmethod
    async def get(self, path: str) -> str:
        raise NotImplemented("get is not implemented for this interface")

    @abstractmethod
    async def set(self, path: str, value: str):
        raise NotImplemented("set is not implemented for this interface")
