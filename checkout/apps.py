from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Ensures compatibility with newer Django versions
    name = 'checkout'

    def ready(self):
        """
        Import and connect signals to their handlers
        """
        import checkout.signals
