# HAP Dorm

My setup for running an Apple Homekit service on Raspberry Pi Zero W.

While most stuff here are very specific to the setup in my dorm, it can be
useful for others trying to set up similar service.

Currently, the following accessories are implemented:

- Temperature Sensor: Uses a BMP180 sensor on `i2c` bus for room temperature
  logging.
- Strands: (WIP) Controls a set of Neopixel (WS2812 RGB) strip.


## Libraries

This setup uses [`HAP-Python`](https://github.com/ikalchev/HAP-python/) for
Homekit bridge.

I tried using [`homebridge`](https://github.com/nfarina/homebridge) earlier
but it's current state makes it frustrating to add my own accessories and
control state.

BMP180 sensor is interfaced using Adafruit's
[`BMP085`](https://github.com/adafruit/Adafruit_Python_BMP) library.


License: MIT


