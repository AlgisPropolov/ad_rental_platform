from django.shortcuts import render
from core.models import DealTask

def task_list(request):
    tasks = DealTask.objects.all()
    return render(request, 'tasks/list.html', {'tasks': tasks})