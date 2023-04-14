from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Client, Pet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CombinedRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Username'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Confirm Password'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}))
    contact_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}))

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


# class UserRegistrationForm(UserCreationForm):
#     username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Username'}))
#     password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Password'}))
#     password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control rounded-left', 'placeholder' : 'Confirm Password'}))

#     class Meta:
#         model = User
#         fields = ('username', 'password1', 'password2')

#     def save(self, commit=True):
#         user = super(UserRegistrationForm, self).save(commit=False)
#         user.username = self.cleaned_data['username']
#         user.set_password(self.cleaned_data['password1'])

#         if commit:
#             user.save()

#         return user

# class ClientInfoForm(forms.Form):
#     first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
#     last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
#     address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}))
#     contact_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}))
#     otp_code = forms.CharField(required=False, widget=forms.HiddenInput())

class PetRegistrationForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ('name', 'species', 'breed', 'age', 'gender')

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
                'name': "username", 
                'class' : 'form-control rounded-left', 
                'placeholder' : 'Username', 
                'required' : 'true'
            }))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=
            {
                'name': 'password', 
                'class' : 'form-control rounded-left', 
                'placeholder' : 'Password', 
                'required' : 'true'
            }))
    remember_me = forms.BooleanField(required=False)