from datetime import timedelta, date
from core.models import DealTask

def get_due_soon_tasks():
    today = date.today()
    soon = today + timedelta(days=3)
    return DealTask.objects.filter(is_done=False, due_date__range=(today, soon))
