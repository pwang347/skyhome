from core.models import WifiDevice
from django.http import HttpResponse
import json
import requests

class SmartHomeManager(object):
	def _enable_json_mode(self, device_name):
		wifi_device = WifiDevice.objects.get(name=device_name)
		requests.get("%s/json" % wifi_device.base_url(), params={'onoff': 1})

	def _filter_status(self, status_json, ports):
		seen_pins = set()
		for pin_type, pin_list in status_json.items():
			new_list = []
			for pin in pin_list:
				if pin['port'] in ports:
					seen_pins.add(pin['port'])
					new_list.append(pin)
			status_json[pin_type] = new_list
		if seen_pins != set(ports):
			raise Exception("Could not find status for ports: %s" % list(set(ports) - seen_pins))
		return status_json

	def output(self, wifi_device, enabled, ports):
		for port in ports:
			params = {
				'port': port,
				'onoff': int(enabled)
			}
			response = requests.get("%s/gpo" % wifi_device.base_url(), params=params)
			if response.status_code != 200:
				raise Exception("Failed to set port %d to %s for the following device: %s" % (port, enabled, wifi_device.name))	

		filtered_status = self._filter_status(response.json(), ports)
		return HttpResponse(json.dumps(filtered_status), content_type='application/json')

	def read(self, wifi_device, ports):
		response = requests.get("%s/status" % wifi_device.base_url())
		if response.status_code != 200:
			raise Exception("Failed to get status for the following device: %s" % wifi_device.name)
		filtered_status = self._filter_status(response.json(), ports)
		return HttpResponse(json.dumps(filtered_status), content_type='application/json')

	def status(self, wifi_device):
		response = requests.get("%s/status" % wifi_device.base_url())
		if response.status_code != 200:
			raise Exception("Failed to get status for the following device: %s" % wifi_device.name)
		return HttpResponse(json.dumps(response.json()), content_type='application/json')

	def perform_action(self, wifi_device_name, action, args):
		self._enable_json_mode(wifi_device_name)
		wifi_device = WifiDevice.objects.get(name=wifi_device_name)
		return getattr(self, action)(wifi_device, **args)
