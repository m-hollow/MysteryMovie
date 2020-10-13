from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('movies:index')
    template_name = 'registration/register.html'

    def form_valid(self, form):     # note: UserCreationForm is, indeed, a ModelForm; and thus the below behavior works
        self.object = form.save()   # saves the new user object (self.object is user object)
        login(self.request, self.object)    # logs in the newly created user
        return redirect(self.get_success_url())  # this simply returns success_url, as defined above.

