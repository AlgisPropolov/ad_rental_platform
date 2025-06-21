from django.shortcuts import render, redirect, get_object_or_404
from core.models import Deal, Client, Asset
from django import forms

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['title', 'client', 'assets', 'status']
        widgets = {
            'assets': forms.CheckboxSelectMultiple
        }


def list_deals_view(request):
    deals = Deal.objects.select_related('client').prefetch_related('assets').all()
    return render(request, 'core/deals/list.html', {'deals': deals})


def create_deal_view(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_deals')
    else:
        form = DealForm()
    return render(request, 'core/deals/create.html', {'form': form})


def edit_deal_view(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            form.save()
            return redirect('list_deals')
    else:
        form = DealForm(instance=deal)
    return render(request, 'core/deals/edit.html', {'form': form, 'deal': deal})


def delete_deal_view(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if request.method == 'POST':
        deal.delete()
        return redirect('list_deals')
    return render(request, 'core/deals/delete.html', {'deal': deal})
