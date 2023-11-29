from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Client, Pet
from .validators import (
    validate_phone_number, 
    validate_image_size, 
    validate_weight, 
    validate_contains_special_character, 
    validate_contains_digit, 
    validate_contains_uppercase,
    validate_first_name,
    validate_last_name
)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from core.models import Region, Province, Municipality, Barangay
from datetime import datetime, timedelta

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
        'class': 'form-control rounded-left wider-input',
        'placeholder': 'Password',
        'data-bs-toggle': 'tooltip',
        'data-bs-placement': 'right',
        'data-html': 'true',
        'title': ('<div class="text-start mt-2"><div class="text-center">Password Requirements</div><br>'
                '<ul>'
                '<li class="small me-2">At least 8 characters long.</li>'
                '<li class="small me-2">Must not be too common.</li>'
                '<li class="small me-2">Must not be too similar to the username.</li>'
                '<li class="small me-2">Contains both uppercase and lowercase characters.</li>'
                '<li class="small me-2">Contains at least one numerical digit.</li>'
                '<li class="small me-2">Contains at least one special character (e.g., @, #, $, etc.).</li>'
                '</ul></div>')
    }), validators=[validate_contains_special_character, validate_contains_digit, validate_contains_uppercase])


    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Confirm Password',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be your password for logging in.'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class' : 'form-control rounded-left wider-input', 'placeholder' : 'Email', 'autocomplete': 'off'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'First Name', 'autocomplete': 'off'}), validators=[validate_first_name])
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Last Name','autocomplete': 'off'}), validators=[validate_last_name])
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

class WalkinUserRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Username',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be the username for logging in.',
                                'autocomplete': 'off'
                                }))

    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded-left wider-input',
        'placeholder': 'Password',
        'data-bs-toggle': 'tooltip',
        'data-bs-placement': 'right',
        'data-html': 'true',
        'title': ('<div class="text-start mt-2"><div class="text-center">Password Requirements</div><br>'
                '<ul>'
                '<li class="small me-2">At least 8 characters long.</li>'
                '<li class="small me-2">Must not be too common.</li>'
                '<li class="small me-2">Must not be too similar to the username.</li>'
                '<li class="small me-2">Contains both uppercase and lowercase characters.</li>'
                '<li class="small me-2">Contains at least one numerical digit.</li>'
                '<li class="small me-2">Contains at least one special character (e.g., @, #, $, etc.).</li>'
                '</ul></div>')
    }), validators=[validate_contains_special_character, validate_contains_digit, validate_contains_uppercase])


    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
                                'class' : 'form-control rounded-left wider-input',
                                'placeholder' : 'Confirm Password',
                                'data-bs-toggle': 'tooltip',
                                'data-bs-placement': 'right',
                                'title': 'This will be the password for logging in.'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class' : 'form-control rounded-left wider-input', 'placeholder' : 'Email', 'autocomplete': 'off'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'First Name', 'autocomplete': 'off'}), validators=[validate_first_name])
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Last Name','autocomplete': 'off'}), validators=[validate_last_name])
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

    today = datetime.today()
    twenty_years_ago = today - timedelta(days=50*365.25)

    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control', 'placeholder': 'Enter pet name', 'autocomplete': 'off'}))
    
    birthday = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'id': 'birthday',
                'class': 'form-control',
                'type': 'date',
                'autocomplete': 'off',
                'min': twenty_years_ago.strftime('%Y-%m-%d'),
                'max': today.strftime('%Y-%m-%d')
            }
        )
    )

    species = forms.CharField(widget=forms.TextInput(attrs={'id': 'species', 'class': 'form-control', 'placeholder': 'Enter species', 'autocomplete': 'off'}))
    breed = forms.CharField(widget=forms.TextInput(attrs={'id': 'breed', 'class': 'form-control', 'placeholder': 'Enter breed', 'autocomplete': 'off'}))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')],
                                widget=forms.Select(attrs={'id': 'gender', 'class': 'form-select'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'id': 'color', 'class': 'form-control', 'placeholder': 'Enter color', 'autocomplete': 'off'}))
    weight = forms.DecimalField(validators=[validate_weight], widget=forms.NumberInput(attrs={'id': 'weight', 'class': 'form-control', 'placeholder': 'Enter weight', 'step': '0.01', 'autocomplete': 'off', 'min': 1, 'max': 150}))
    picture = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={
                'id': 'picture',
                'class': 'form-control',
                'autocomplete': 'off',
                'accept': 'image/jpeg, image/png, image/webp',
            }
        ),
        required=False,
        validators=[validate_image_size]
    )


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
    weight = forms.DecimalField(validators=[validate_weight], widget=forms.NumberInput(attrs={'id': 'weight', 'class': 'form-control', 'placeholder': 'Enter weight', 'step': '0.01', 'autocomplete': 'off', 'min': 1, 'max': 150}))
    picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={'id': 'picture', 'class': 'form-control'}), required=False, validators=[validate_image_size])
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
    # street = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Street'}))
    # barangay = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Barangay'}))
    # city = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'City'}))
    # province = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Province'}))
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
        empty_label="Select Province",
    )
    city = forms.ModelChoiceField(
        required=True,
        queryset=Municipality.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select City/Municipality",
    )
    barangay = forms.ModelChoiceField(
        required=True,
        queryset=Barangay.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select Barangay",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'data' in kwargs:
            if 'province' in kwargs['data']:
                province_id = kwargs['data']['province']
                self.fields['city'].queryset = Municipality.objects.filter(province_id=province_id)

            if 'city' in kwargs['data']:
                city_id = kwargs['data']['city']
                self.fields['barangay'].queryset = Barangay.objects.filter(municipality_id=city_id)

        instance = kwargs.get('instance')
        if instance:
            self.fields['city'].queryset = Municipality.objects.filter(name=instance.city, province__name=instance.province)
            self.fields['barangay'].queryset = Barangay.objects.filter(name=instance.barangay, municipality__name=instance.city)
            
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'gender', 'street', 'barangay', 'city', 'province', 'two_auth_enabled',)

class PasswordResetStep1(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Username'}))

class PasswordResetStep2(forms.Form):
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control wider-input', 'placeholder': 'New Password'}), validators=[validate_contains_special_character, validate_contains_digit, validate_contains_uppercase])
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Confirm New Password'}))

class AdminChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}), validators=[validate_contains_special_character, validate_contains_digit, validate_contains_uppercase])
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}))

class TwoFactorAuthenticationForm(forms.Form):
    two_auth_enabled = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'On'), (False, 'Off'))))

class AdminTwoFactorAuthenticationForm(forms.Form):
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control wider-input', 'placeholder': 'Phone Number'}), validators=[validate_phone_number])
    two_auth_enabled = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'On'), (False, 'Off'))))
    