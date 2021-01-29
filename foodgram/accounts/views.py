from django.shortcuts import render

from django.views.generic import CreateView

from .forms import CreationForm

from django.urls import reverse_lazy


class SingUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")

    template_name = "signup.html"