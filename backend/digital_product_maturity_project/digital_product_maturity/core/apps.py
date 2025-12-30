from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'digital_product_maturity.core'
    
    def ready(self):
        import digital_product_maturity.core.signals
