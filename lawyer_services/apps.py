from django.apps import AppConfig


class LawyerServicesConfig(AppConfig):
    name = "lawyer_services"

    def ready(self):
        import lawyer_services.signals
