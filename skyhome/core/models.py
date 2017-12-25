from django.db import models

class WifiDevice(models.Model):
	"""
	A wifi device descriptor.
	"""
	name = models.CharField(unique=True, null=False, max_length=128)
	device_type_id = models.IntegerField(db_index=True, null=False)
	hostname = models.CharField(unique=True, max_length=64)
	ip_address = models.CharField(unique=True, max_length=24)
	extra_details_json = models.CharField(max_length=128)

	def base_url(self):
		# just use http for now
		return "http://%s" % self.ip_address

class DeviceType(models.Model):
	"""
	Type of device, for example Raspberry Pi 3.
	"""
	name = models.CharField(unique=True, null=False, max_length=128)

class DeviceConfiguration(models.Model):
	"""
	A configuration for a wifi device.
	"""
	name = models.CharField(unique=True, null=False, max_length=128)
	wifi_device_id = models.IntegerField()
	details_json = models.CharField(max_length=128)

	class Meta:
		unique_together = ('wifi_device_id', 'details_json')

class AuditLog(models.Model):
	"""
	Audit logs for state changes.
	"""
	wifi_device_id = models.IntegerField(null=False)
	action_type = models.IntegerField(null=False)
	timestamp = models.DateField()
	message = models.CharField(default=None, max_length=128)

	class Meta:
		index_together = ('wifi_device_id', 'action_type', 'timestamp')
