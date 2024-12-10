from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Заказы'

    def ready(self):
        # Подключаем обработчики сигналов
        import orders.paypal_handlers  # Подключаем наш файл с обработчиками