
import time

from celery import Celery
from celery.schedules import crontab
from basic_selenium_auth import UbiSignInCheck

app = Celery("tasks", broker="amqp://admin:mypass@localhost:5672//")

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(),
        test_login.s(),
        name="adder",
        expires=60,  # Expires after 1 minutes
    )

@app.task
def test_login():
    tester = UbiSignInCheck("dsr", "asdfasdf1")
    print(tester.test())
    time.sleep(10)
    tester.close_browser()

