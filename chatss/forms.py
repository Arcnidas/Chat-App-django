from difflib import get_close_matches
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.http import JsonResponse
from .models import accUser, FriendRequest, Profile
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = accUser
        fields = ('email', 'username', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = accUser
        fields = ('email', 'username', 'password', 'is_active', 'is_staff')


 # Adjust import paths to match your project



class FriendRequestForm(forms.ModelForm):
    
    class Meta:
        model = FriendRequest
        fields = ('receiver',)

    receiver = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'name-input'}))

    def clean_receiver(self):
        username = self.cleaned_data.get('receiver')  # Extract username
        print("username printed: "+username)
        if not username:
            raise forms.ValidationError("This field is required.")

        try:
            # Fetch the user object from the database
            user = accUser.objects.get(username=username)
            return user  # Return the actual accUser instance
        except accUser.DoesNotExist:
            # Suggest alternatives if no exact match exists
            all_users = accUser.objects.values_list('username', flat=True)
            closest_matches = get_close_matches(username, all_users, n=1, cutoff=0.6)
            if closest_matches:
                print(f"here is the closest match: {', '.join(closest_matches)}")
                raise forms.ValidationError(
                    f"No exact match found. Did you mean: {', '.join(closest_matches)}"
                )
            raise forms.ValidationError("No matching user found.")





class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields =('profile_picture', 'bio')

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'w-24 rounded-full'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea w-full', 'rows': 4, 'cols': 15})
    )

class CustomSignupForm(SignupForm):

    GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),)

    username = forms.CharField(max_length=150, label='Username')
    age = forms.IntegerField(label='Age', required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Gender', required=True)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.username = self.cleaned_data['username']
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.save()
        return user
