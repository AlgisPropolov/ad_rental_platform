from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import DealTask
from ..forms import TaskForm

class TaskListView(ListView):
    model = DealTask
    template_name = 'core/tasks/list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('deal', 'assigned_to')

class TaskCreateView(CreateView):
    model = DealTask
    form_class = TaskForm
    template_name = 'core/tasks/create.html'
    success_url = reverse_lazy('task-list')

class TaskDetailView(DetailView):
    model = DealTask
    template_name = 'core/tasks/detail.html'
    context_object_name = 'task'

class TaskUpdateView(UpdateView):
    model = DealTask
    form_class = TaskForm
    template_name = 'core/tasks/edit.html'
    success_url = reverse_lazy('task-list')

class TaskDeleteView(DeleteView):
    model = DealTask
    template_name = 'core/tasks/delete.html'
    success_url = reverse_lazy('task-list')