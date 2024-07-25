from django.apps import AppConfig
import threading

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from AngelOne.task import check_and_execute_trades
        from AngelOne.scheduler import schedule_daily_update
        from AngelOne.db import init_db

        # Make sure only single instance is created.
        # Does not work when using multiple gunicorn worker processes 

        if not hasattr(self, 'initialized'):
            self.initialized = True

            # Start background thread for checking and executing trades
            threading.Thread(target=check_and_execute_trades, daemon=True).start()

            # Initialize stocks database and schedule daily update
            init_db()
            threading.Thread(target=schedule_daily_update, daemon=True).start()
