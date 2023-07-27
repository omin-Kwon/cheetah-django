from django.apps import AppConfig


class PushSchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pushscheduler'
    def ready(self):

        from .scheduler import start
        start()
