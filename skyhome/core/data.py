from core.models import WifiDevice, DeviceType, DeviceConfiguration
from django.http import HttpResponse
import json

class DataManager(object):
    def _json_encode(self, obj):
        # make sure the config looks nice in the db
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

    def register_device(self, name, type_name, ip_address, hostname, **kwargs):
        device_type, _ = DeviceType.objects.get_or_create(name=type_name)
        WifiDevice.objects.create(name=name,
                                  device_type_id=device_type.id,
                                  hostname=hostname,
                                  ip_address=ip_address,
                                  extra_details_json=self._json_encode(kwargs))
        return HttpResponse("")
    
    def create_or_update_config(self, name, wifi_device_name, **kwargs):
        wifi_device = WifiDevice.objects.get(name=wifi_device_name)
        updated_values = {'details_json': self._json_encode(kwargs)}
        DeviceConfiguration.objects.update_or_create(name=name, wifi_device_id=wifi_device.id, defaults=updated_values)
        return HttpResponse("")
