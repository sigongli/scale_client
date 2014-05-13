from __future__ import print_function
import subprocess
import re
from virtual_sensor import VirtualSensor
from sensed_event import SensedEvent

class TemperatureVirtualSensor(VirtualSensor):
	def __init__(
		self, queue, device,
		daemon_path,
		threshold
	):
		VirtualSensor.__init__(self, queue, device)
		self._daemon_path = daemon_path
		self._threshold = threshold
		self._result = None
		self._regexp = re.compile(r'Device ([^:]*): Sensor ([0-9]*): Temperature: ([0-9\.]*)')

	def type(self):
		return "Temperature Sensor"

	def connect(self):
		self._result = subprocess.Popen(
		#	['temperature-streams'],
			[self._daemon_path],
			shell=True,
			stdout=subprocess.PIPE
		)
		return True

	def read(self):
		line = next(iter(self._result.stdout.readline, '')) 
		match = self._regexp.match(line)
		try:
			temperature = float(match.group(3))
		except AttributeError as e:
			print('Error parsing temperature: %s' % e)
		return temperature

	def policy_check(self, data):
		ls_event = []
		if data > self._threshold:
			ls_event.append(
				SensedEvent(
					sensor = self.device.device,
					msg = {
						"event": "high_temperature",
						"threshold": self._threshold,
						"value": data
					},
					priority = 50
				)
			)
		
		# Lines below are for testing purpose
		if True:
			ls_event.append(
				SensedEvent(
					sensor = self.device.device,
					msg = {
						"event": "raw",
						"value": data
					},
					priority = 200
				)
			)
		return ls_event
