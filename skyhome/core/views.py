from core.data import DataManager
from core.api import SmartHomeManager
from django.shortcuts import render
from django.http import HttpResponse
import inspect
import json

def _get_client_ip_address_and_hostname(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', None)
    hostname = request.META.get('REMOTE_HOST', None)
    return ip_address, hostname

def _get_default_params(fn):
    args, _, _, defaults = inspect.getargspec(fn)
    return dict(zip(reversed(args), reversed(defaults)))

def post_with_params(params):
    def decorator(fn):
        def wrapper(request, *args, **kwargs):
            post_data = json.loads(request.body.decode('utf-8'))
            data = {}
            defaults = _get_default_params(fn)
            for param in params:
                data[param] = post_data.pop(param, None)
                if param not in defaults and data[param] is None:
                    raise Exception("'%s' is a required parameter." % param)
            kwargs.update(data)
            return fn(request, *args, **kwargs)
        return wrapper
    return decorator

def handle_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)
    return wrapper

@handle_exception
@post_with_params(('type_name', 'name'))
def register_device(request, type_name, name, **kwargs):
    ip_address, hostname = _get_client_ip_address_and_hostname(request)
    data_manager = DataManager()
    return data_manager.register_device(name=name,
                                        type_name=type_name,
                                        ip_address=ip_address,
                                        hostname=hostname,
                                        **kwargs)

@handle_exception
@post_with_params(('name', 'wifi_device_name'))
def create_or_update_config(request, name, wifi_device_name, **kwargs):
    data_manager = DataManager()
    return data_manager.create_or_update_config(name=name,
                                                wifi_device_name=wifi_device_name,
                                                **kwargs)

@handle_exception
@post_with_params(('name', 'action', 'args'))
def perform_action(request, name, action, args=None):
    if args is None:
        args = {}
    smart_home_manager = SmartHomeManager()
    return smart_home_manager.perform_action(wifi_device_name=name,
                                             action=action,
                                             args=args)
