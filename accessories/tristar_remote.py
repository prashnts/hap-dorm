import logging

from gpiozero import LED as GPIO
from time import sleep
from addict import Dict as AttrDict
from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_FAN


PIN_MAP = AttrDict({
  'VCC': 22,    # 3 in wiringpi
  'SPD': 23,    # 4 in wiringpi
  'OSC': 24,    # 5 in wiringpi
  'POW': 25,    # 6 in wiringpi
})

gpio_pin = lambda x: GPIO(x, active_high=True, initial_value=True)


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

  def trigger(self, pin):
    pin.off()
    sleep(1)
    pin.on()

  def trigger_pow(self):
    self.trigger(self.pins.pow)

  def shut_down(self):
    self.pins.pow.on()
    self.pins.osc.on()
    self.pins.spd.on()
    self.pins.vcc.on()
    self.pins.pow.close()
    self.pins.osc.close()
    self.pins.spd.close()
    self.pins.vcc.close()


class TristarFan(AsyncAccessory):
  category = CATEGORY_FAN

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.0',
      manufacturer='noop.pw',
      model='pw.noop.hap.tristar_ir',
      serial_number='42-AC-TRISTARIR')

    serv_fan = self.add_preload_service('Fanv2', chars=['Active', 'SwingMode'])

    self.char_active = serv_fan.configure_char('Active', setter_callback=self.toggle_power, value=0)
    self.char_swing = serv_fan.configure_char('SwingMode', setter_callback=self.toggle_swing, value=0)

    self.remote = IrRemote()

  def toggle_power(self, active):
    self.remote.trigger(self.remote.pins.pow)

  def toggle_swing(self, active):
    self.remote.trigger(self.remote.pins.osc)
