import json
from gpiozero import PWMLED
from typing import Dict
from dataclasses import dataclass


@dataclass
class RGBColor:
    r: int
    g: int
    b: int

    @property
    def hex(self) -> str:
        return "#%02x%02x%02x" % (self.r, self.g, self.b)

    @property
    def rgb(self) -> str:
        return f"({self.r},{self.g},{self.b})"


class Lamp:
    STATE_ON: str = "ON"
    STATE_OFF: str = "OFF"

    def __init__(self):
        self.brightness: int = 100
        self.color_mode: str = "color_temp"
        self.color_rgb: RGBColor = RGBColor(r=255, g=255, b=255)
        self.color_temp: int = 153
        self._on: bool = True

    @property
    def on(self) -> str:
        return self.STATE_ON if self._on else self.STATE_OFF

    @on.setter
    def on(self, state: str) -> None:
        if state == self.STATE_ON:
            self._on = True
        elif state == self.STATE_OFF:
            self._on = False

    def update(self) -> None:
        # TODO: update actual hardware to match settings
        pass

    def read_json(self, json_data: str) -> None:
        data = json.loads(json_data)

        if on := data.get("state"):
            self.on = on
        # NOTE: Color mode never actually gets sent
        # if color_mode := data.get("color_mode"):
        #     self.color_mode = color_mode
        if brightness := data.get("brightness"):
            self.brightness = brightness
        if color_temp := data.get("color_temp"):
            self.color_temp = color_temp
            self.color_mode = "color_temp"
        elif color := data.get("color"):
            self.color_rgb = RGBColor(r=color["r"], g=color["g"], b=color["b"])
            self.color_mode = "rgb"

        self.update()

    def get_json(self) -> str:
        output = {
            "state": self.on,
            "color_mode": self.color_mode,
            "brightness": self.brightness,
            "color_temp": self.color_temp,
            "color": {
                "r": self.color_rgb.r,
                "g": self.color_rgb.g,
                "b": self.color_rgb.b,
            },
        }
        return json.dumps(output)

    def __str__(self):
        color_string = (
            f"Color temp: {self.color_temp}"
            if self.color_mode == "color_temp"
            else f"RGB: {self.color_rgb.rgb}, Hex: {self.color_rgb.hex}"
        )
        return (
            f"Lamp: [ On: {self._on}, Brightness: {self.brightness}, {color_string} ]"
        )
