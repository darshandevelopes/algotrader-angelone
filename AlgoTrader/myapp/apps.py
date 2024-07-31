from django.apps import AppConfig
import threading

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from AngelOne.task import check_and_execute_trades, send_alerts_for_executed_orders
        from AngelOne.scheduler import schedule_daily_update

        # Make sure only single instance is created.
        # Does not work when using multiple gunicorn worker processes 

        if not hasattr(self, 'initialized'):
            self.initialized = True

            # Start background thread for checking and executing trades
            threading.Thread(target=check_and_execute_trades, daemon=True).start()

            # Start background thread for sending alerts for executed orders
            threading.Thread(target=send_alerts_for_executed_orders, daemon=True).start()

            # Schedule daily update of stock data
            threading.Thread(target=schedule_daily_update, daemon=True).start()

