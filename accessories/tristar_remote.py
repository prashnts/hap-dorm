from gpiozero import LED as GPIO
from time import sleep
from addict import Dict as AttrDict

PIN_MAP = AttrDict({
  'VCC': 22,
  'SPD': 23,
  'OSC': 24,
  'POW': 25,
})

gpio_pin = lambda x: GPIO(x, active_high=False, initial_value=True)


class IrRemote:
  def __init__(self):
    self._setup_pins()

  def _setup_pins(self):
    pins = AttrDict()
    pins.vcc = gpio_pin(PIN_MAP.VCC)
    pins.pow = gpio_pin(PIN_MAP.POW)
    pins.osc = gpio_pin(PIN_MAP.OSC)
    pins.spd = gpio_pin(PIN_MAP.SPD)
    self.pins = pins

  def trigger_pow(self):
    self.pins.pow.on()
    sleep(1000)
    self.pins.pow.off()
