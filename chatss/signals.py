from allauth.account.signals import email_confirmed

from django.dispatch import receiver
from .models import Profile
from allauth.account.signals import user_signed_up

@receiver(email_confirmed)
def create_profile_on_email_confirmed(request, email_address, **kwargs):
    user = email_address.user  
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)


@receiver(user_signed_up)
def create_profile_on_user_signed_up(sender, request, user, **kwargs):
    # Check if the profile already exists (to avoid duplication)
    if not hasattr(user, 'profile'):
        # Create a new profile
        Profile.objects.create(user=user)
        print(f"Profile created for user: {user.username}")
