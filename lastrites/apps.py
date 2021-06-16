from django.apps import AppConfig


class LastritesConfig(AppConfig):
    name = "lastrites"

    def ready(self):
        import lastrites.signals
