from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import DealTask
from ..forms import TaskForm


class DealTaskListView(ListView):
    model = DealTask
    template_name = 'core/tasks/list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('deal', 'assigned_to')

        # Фильтрация по статусу выполнения
        is_done = self.request.GET.get('is_done')
        if is_done:
            queryset = queryset.filter(is_done=is_done.lower() == 'true')

        return queryset


class DealTaskCreateView(CreateView):
    model = DealTask
    form_class = TaskForm
    template_name = 'core/tasks/create.html'

    def get_success_url(self):
        messages.success(self.request, 'Задача успешно создана')
        return reverse_lazy('task-list')


class DealTaskDetailView(DetailView):
    model = DealTask
    template_name = 'core/tasks/detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return super().get_queryset().select_related('deal', 'assigned_to')


class DealTaskUpdateView(UpdateView):
    model = DealTask
    form_class = TaskForm
    template_name = 'core/tasks/edit.html'

    def get_success_url(self):
        messages.success(self.request, 'Задача успешно обновлена')
        return reverse_lazy('task-detail', kwargs={'pk': self.object.pk})


class DealTaskDeleteView(DeleteView):
    model = DealTask
    template_name = 'core/tasks/delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Задача успешно удалена')
        return reverse_lazy('task-list')