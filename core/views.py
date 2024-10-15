from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

class LogoutView(View):
    def get(self, request):
        # Perform any pre-logout operations here
        # For example, you might want to log the logout event

        # Log out the user
        logout(request)

        # Add a success message
        messages.success(request, "You have been successfully logged out.")

        # Redirect to the dashboard
        return redirect(reverse('web:index'))

    def post(self, request):
        # Handle POST requests if needed
        return self.get(request)