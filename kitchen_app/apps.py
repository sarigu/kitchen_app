from django.apps import AppConfig


class KitchenAppConfig(AppConfig):
    name = 'kitchen_app'

    def ready(self):
        from . signals import create_user_profile