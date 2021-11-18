from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class PaymentForm(forms.Form):
    CHOICES = (('MasterCard', 'MasterCard'), ('Visa', 'Visa'), ('Paypal', 'Paypal'))
    card = forms.ChoiceField(choices=CHOICES)
    number = forms.IntegerField(max_value=9999999999999999, min_value=1000000000000000, widget=forms.TextInput(attrs={'placeholder': 'Card Nmber'}))
    date = forms.DateField(widget=forms.widgets.DateInput(format="%m/%Y"))
    name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    cvc = forms.IntegerField(min_value=100, max_value=999, widget=forms.TextInput(attrs={'placeholder': 'CVC'}))

