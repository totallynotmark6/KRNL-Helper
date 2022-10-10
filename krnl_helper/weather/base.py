class Weather:
    _services = {}

    @classmethod
    def register_service(cls, service):
        if isinstance(service.name, str):
            cls._services[service.name] = service
        elif isinstance(service.name, list):
            for name in service.name:
                cls._services[name] = service

    @classmethod
    def get_service(cls, service):
        return cls._services[service]


class WeatherService:
    name = "N/A"

    def __init__(self):
        pass
