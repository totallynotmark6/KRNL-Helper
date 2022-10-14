import requests


class Weather:
    _services = {}
    _active = {}

    @classmethod
    def register_service(cls, service):
        if isinstance(service.name, str):
            cls._services[service.name] = service
        elif isinstance(service.name, list):
            for name in service.name:
                cls._services[name] = service

    @classmethod
    def get_service(cls, service) -> "WeatherService":
        cached = cls._active.get(service)
        if cached:
            return cached
        else:
            service = cls._services.get(service)
            if service:
                service = service()
                cls._active[service.name] = service
                return service
            else:
                raise ValueError(f"Service {service} not found")


class WeatherService:
    name = "N/A"
    url = "N/A"

    def __init__(self):
        self.refresh()

    def refresh(self):
        resp = requests.get(self.url)
        if resp.status_code == 200:
            self._parse(resp.json())
