from __future__ import annotations
import json

import pigpio
import homeassistant.util.color as color_util
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

    @staticmethod
    def from_color_temp(temp: int) -> RGBColor:
        kelvin = color_util.color_temperature_mired_to_kelvin(temp)
        rgb = color_util.color_temperature_to_rgb(kelvin)
        return RGBColor(rgb[0], rgb[1], rgb[2])


class Lamp:
    STATE_ON: str = "ON"
    STATE_OFF: str = "OFF"

    PIN_R: int = 17
    PIN_G: int = 27
    PIN_B: int = 22

    # Blue and green light is naturally more powerfull than red light so it needs to be dimmed to look balanced
    # Additional calibration is also for the specific LEDs
    BLUE_COMP: float = 0.3
    GREEN_COMP: float = 0.2

    def __init__(self):
        self.brightness: int = 100
        self.color_mode: str = "color_temp"
        self.color_rgb: RGBColor = RGBColor(r=255, g=255, b=255)
        self.color_temp: int = 153
        self._on: bool = True

        # GPIO Setup
        self._pi = pigpio.pi()

    def __del__(self):
        self._pi.stop()
        

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
        if self._on:
            if self.color_mode == "rgb":
                self._pi.set_PWM_dutycycle(self.PIN_R, int((self.color_rgb.r / 256) * self.brightness))
                self._pi.set_PWM_dutycycle(self.PIN_G, int((self.color_rgb.g / 256) * self.brightness * self.GREEN_COMP))
                self._pi.set_PWM_dutycycle(self.PIN_B, int((self.color_rgb.b / 256) * self.brightness * self.BLUE_COMP))
            elif self.color_mode == "color_temp":
                color = RGBColor.from_color_temp(self.color_temp)
                self._pi.set_PWM_dutycycle(self.PIN_R, int((color.r / 256) * self.brightness))
                self._pi.set_PWM_dutycycle(self.PIN_G, int((color.g / 256) * self.brightness * self.GREEN_COMP))
                self._pi.set_PWM_dutycycle(self.PIN_B, int((color.b / 256) * self.brightness * self.BLUE_COMP))
                # print(f"color temp as RGB: {color}")
        else:
            for pin in [self.PIN_R, self.PIN_G, self.PIN_B]:
                self._pi.set_PWM_dutycycle(pin, 0)

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
