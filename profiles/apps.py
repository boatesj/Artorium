from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        """
        Import signals to ensure they are connected when the app starts.
        """
        import profiles.signals  # This will now work because the signals.py file exists
