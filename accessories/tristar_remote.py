import logging

from gpiozero import LED as GPIO
from time import sleep
from addict import Dict as AttrDict
from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_FAN
from itertools import cycle
from enum import Enum


PIN_MAP = AttrDict({
  'VCC': 22,    # 3 in wiringpi
  'SPD': 23,    # 4 in wiringpi
  'OSC': 24,    # 5 in wiringpi
  'POW': 25,    # 6 in wiringpi
})


gpio_pin = lambda x: GPIO(x, active_high=True, initial_value=True)


class ActiveState(Enum):
  on = 1
  off = 2

  @classmethod
  def from_value(cls, value):
    if value:
      return cls.on
    else:
      return cls.off


class FanSpeed(Enum):
  low = 1
  medium = 2
  high = 3

  def __rshift__(self, target):
    # low -> medium => trigger x1
    # low -> high => trigger x2
    # medium -> low => trigger x2
    # medium -> high => trigger x1
    # high -> low => trigger x1
    # high -> medium => trigger x2

    if target.value < self.value:
      return target.value - self.value + 3
    else:
      return target.value - self.value

  @classmethod
  def from_value(cls, value):
    if value < 30:
      return cls.low
    if value < 60:
      return cls.medium
    if value <= 100:
      return cls.high


class IrRemote:
  def __init__(self):
    self._setup_pins()
    self.state = AttrDict({
      'power': ActiveState.off,
      'swing': ActiveState.off,
      'speed': FanSpeed.low,
    })

  def _setup_pins(self):
    pins = AttrDict()
    pins.vcc = gpio_pin(PIN_MAP.VCC)
    pins.pow = gpio_pin(PIN_MAP.POW)
    pins.osc = gpio_pin(PIN_MAP.OSC)
    pins.spd = gpio_pin(PIN_MAP.SPD)
    self.pins = pins

  def __exit__(self, *args, **kwargs):
    self.pins.vcc.off()
    sleep(0.1)
    self.pins.pow.off()
    self.pins.osc.off()
    self.pins.spd.off()
    sleep(0.5)

  def __enter__(self):
    self.pins.pow.on()
    self.pins.osc.on()
    self.pins.spd.on()
    sleep(0.1)
    self.pins.vcc.on()
    sleep(0.5)

  def trigger(self, pin):
    with self:
      pin.off()
      sleep(0.5)
      pin.on()

  def verify_trigger(self):
    # Detect if the device beeped, otherwise try again!
    pass

  def power(self, state):
    if self.state.power != state:
      self.trigger(self.pins.pow)
      self.state.power = state

  def swing(self, state):
    if self.state.power != ActiveState.on:
      return
    if self.state.swing != state:
      self.trigger(self.pins.osc)
      self.state.swing = state

  def speed(self, target):
    if self.state.power != ActiveState.on:
      return
    for i in range(self.state.speed >> target):
      self.trigger(self.pins.spd)
    self.state.speed = target

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

    serv_fan = self.add_preload_service('Fanv2', chars=['Active', 'SwingMode', 'RotationSpeed'])

    self.char_active = serv_fan.configure_char('Active', setter_callback=self.toggle_power, value=0)
    self.char_swing = serv_fan.configure_char('SwingMode', setter_callback=self.toggle_swing, value=0)
    self.char_speed = serv_fan.configure_char('RotationSpeed', setter_callback=self.toggle_speed, value=20)

    self.remote = IrRemote()

  def toggle_power(self, value):
    self.remote.power(ActiveState.from_value(value))

  def toggle_swing(self, value):
    self.remote.swing(ActiveState.from_value(value))

  def toggle_speed(self, value):
    self.remote.speed(FanSpeed.from_value(value))
