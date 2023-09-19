from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Client, Pet
from .validators import validate_phone_number, validate_image_size
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from core.models import Region, Province, Municipality, Barangay

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Username',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be your username for logging in.',
                                'autocomplete': 'off'
                                }))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Password',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be your password for logging in.'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Confirm Password',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be your password for logging in.'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class' : 'form-control rounded-left wider-input', 'placeholder' : 'Email', 'autocomplete': 'off'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'First Name', 'autocomplete': 'off'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Last Name','autocomplete': 'off'}))
    gender = forms.ChoiceField(choices=[('', 'Gender'), ('Male', 'Male'), ('Female', 'Female')], widget=forms.Select(attrs={'id': 'gender', 'class': 'form-select'}), initial='')
    street = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control wider-input', 
            'placeholder': 'Street', 
            'autocomplete': 'off'
        })
    )

    province = forms.ModelChoiceField(
        required=True,
        queryset=Province.objects.all().order_by('name'), 
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select Province"
    )
    city = forms.ModelChoiceField(
        required=True,
        queryset=Municipality.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}), 
        empty_label="Select City/Municipality"
    )
    barangay = forms.ModelChoiceField(
        required=True,
        queryset=Barangay.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select Barangay"
    )
    contact_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
                                'class': 'form-control wider-input', 
                                'placeholder': 'Contact Number',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': "Input a valid number. It's for contact during appointments.", 'autocomplete': 'off'}), validators=[validate_phone_number], label='Contact Number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'data' in kwargs:
            if 'province' in kwargs['data']:
                province_id = kwargs['data']['province']
                self.fields['city'].queryset = Municipality.objects.filter(province_id=province_id)

            if 'city' in kwargs['data']:
                city_id = kwargs['data']['city']
                self.fields['barangay'].queryset = Barangay.objects.filter(municipality_id=city_id)
        
        self.fields['username'].widget.attrs.update({'autofocus': False})

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class PetRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control', 'placeholder': 'Enter pet name', 'autocomplete': 'off'}))
    birthday = forms.DateField(widget=forms.DateInput(attrs={'id': 'birthday', 'class': 'form-control', 'type': 'date', 'autocomplete': 'off'}))
    species = forms.CharField(widget=forms.TextInput(attrs={'id': 'species', 'class': 'form-control', 'placeholder': 'Enter species', 'autocomplete': 'off'}))
    breed = forms.CharField(widget=forms.TextInput(attrs={'id': 'breed', 'class': 'form-control', 'placeholder': 'Enter breed', 'autocomplete': 'off'}))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')],
                                widget=forms.Select(attrs={'id': 'gender', 'class': 'form-select'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'id': 'color', 'class': 'form-control', 'placeholder': 'Enter color', 'autocomplete': 'off'}))
    weight = forms.DecimalField(widget=forms.NumberInput(attrs={'id': 'weight', 'class': 'form-control', 'placeholder': 'Enter weight', 'step': '0.01', 'autocomplete': 'off'}))
    picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={'id': 'picture', 'class': 'form-control', 'autocomplete': 'off'}), validators=[validate_image_size])

    class Meta:
        model = Pet
        fields = ('name', 'birthday', 'species', 'breed', 'gender', 'color', 'weight', 'picture')

class AdminPetRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control', 'placeholder': 'Enter pet name'}))
    birthday = forms.DateField(widget=forms.DateInput(attrs={'id': 'birthday', 'class': 'form-control', 'type': 'date'}))
    species = forms.CharField(widget=forms.TextInput(attrs={'id': 'species', 'class': 'form-control', 'placeholder': 'Enter species'}))
    breed = forms.CharField(widget=forms.TextInput(attrs={'id': 'breed', 'class': 'form-control', 'placeholder': 'Enter breed'}))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')],
                                widget=forms.Select(attrs={'id': 'gender', 'class': 'form-select'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'id': 'color', 'class': 'form-control', 'placeholder': 'Enter color'}))
    weight = forms.DecimalField(widget=forms.NumberInput(attrs={'id': 'weight', 'class': 'form-control', 'placeholder': 'Enter weight', 'step': '0.01'}))
    picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={'id': 'picture', 'class': 'form-control'}), validators=[validate_image_size])
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'id': 'is_active', 'class': 'form-check-input'}))

    class Meta:
        model = Pet
        fields = ('name', 'birthday', 'species', 'breed', 'gender', 'color', 'weight', 'picture', 'is_active')

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
                'name': "username", 
                'class' : 'form-control rounded-left', 
                'placeholder' : 'Username', 
                'required' : 'true',
                'autocomplete': 'off'
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
            
    def confirm_login_allowed(self, user):
        pass
    # remember_me = forms.BooleanField(required=False)

class UserUpdateForm(UserChangeForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control rounded-left wider-input', 'placeholder' : 'Username'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class' : 'form-control rounded-left wider-input', 'placeholder' : 'Email'}))
    
    class Meta:
        model = User
        fields = ('username', 'email',)

class ClientUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Last Name'}))
    gender = forms.ChoiceField(choices=[('', 'Gender'), ('Male', 'Male'), ('Female', 'Female')],widget=forms.Select(attrs={'id': 'gender', 'class': 'form-select'}), initial='')
    street = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Street'}))
    barangay = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Barangay'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'City'}))
    province = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Province'}))
    #contact_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Contact Number', 'disabled': 'true'}))

    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'gender', 'street', 'barangay', 'city', 'province', 'two_auth_enabled',)

class PasswordResetStep1(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Username'}))

class PasswordResetStep2(forms.Form):
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control wider-input', 'placeholder': 'New Password'}))
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Confirm New Password'}))

class AdminChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}))
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}))

class TwoFactorAuthenticationForm(forms.Form):
    two_auth_enabled = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'On'), (False, 'Off'))))

class AdminTwoFactorAuthenticationForm(forms.Form):
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Phone Number'}), validators=[validate_phone_number])
    two_auth_enabled = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'On'), (False, 'Off'))))
    