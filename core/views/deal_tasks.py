# core/views/deal_tasks.py
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from core.models import DealTask, Deal


class DealTaskForm(forms.ModelForm):
    class Meta:
        model = DealTask
        fields = ['deal', 'description', 'is_done', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


def list_tasks_view(request):
    tasks = DealTask.objects.select_related('deal').order_by('due_date')
    return render(request, 'core/deal_tasks/list.html', {'tasks': tasks})


def create_task_view(request):
    form = DealTaskForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_tasks')
    return render(request, 'core/deal_tasks/create.html', {'form': form})
