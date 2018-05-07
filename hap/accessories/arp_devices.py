import scapy.all as scapy

from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_SENSOR


class ARPOccupancySensor(AsyncAccessory):
  category = CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.2',
      manufacturer='noop.pw',
      model='pw.noop.hap.arp-occ',
      serial_number='42-AC-ARPOCC')

    serv_occp = self.add_preload_service('OccupancySensor')
    self.char_presence = serv_occp.configure_char('OccupancyDetected')

  @AsyncAccessory.run_at_interval(5)
  async def run(self):
    ans, _ = scapy.arping('192.168.0.106')

    self.char_presence.set_value(1 if ans else 0)
