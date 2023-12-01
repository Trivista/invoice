from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from .models import *
import json

#Form Layout from Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column



class DateInput(forms.DateInput):
    input_type = 'date'


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(
                            widget=forms.TextInput(attrs={'id': 'floatingInput', 'class': 'form-control mb-3'}),
                            required=True)
    password = forms.CharField(
                            widget=forms.PasswordInput(attrs={'id': 'floatingPassword', 'class': 'form-control mb-3'}),
                            required=True)

    class Meta:
        model=User
        fields=['username','password']



class ClientForm(forms.ModelForm):
    clientName = forms.CharField(
                            required = True,
                            label='Client Name',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Client Name'}),),
    clientLogo = forms.ImageField(
                            required = False,
                            label='Client Logo',
                            widget=forms.FileInput(attrs={'class': 'form-control mb-3'}),),
    addressLine1 = forms.CharField(
                            required = False,
                            label='Address',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Address line 1'}),),
    province = forms.ChoiceField(
                            required = False,
                            label='Province',
                            choices = Client.PROVINCES,
                            widget=forms.Select(attrs={'class': 'form-control mb-3'}),),
    postalCode = forms.CharField(
                            required = False,
                            label='Postal Code',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Postal Code'}),),
    phoneNumber = forms.CharField(
                            required = False,
                            label='Phone Number',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Phone Number'}),),
    emailAddress = forms.CharField(
                            required = False,
                            label='Email Address',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Email Address'}),),
    taxNumber = forms.CharField(
                            required = False,
                            label='Tax Number',
                            widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Tax Number'}),),
     
    class Meta:
        model = Client
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 'phoneNumber', 'emailAddress', 'taxNumber']


class ProductForm(forms.ModelForm):
    code = forms.CharField(
                    required = True,
                    label='Product Name',
                    widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Product Name'}),),
    description = forms.CharField(
                    required = False,
                    label='Product Description',
                    widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Product Description'}),),
    quantity_on_hand = forms.IntegerField(
                    required = True,
                    label='Quantity on Hand',
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Product Quantity'}),),
    selling_price = forms.DecimalField(
                    required = True,
                    label='Product Price',
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter Product Price'}),),
    unit_of_measure = forms.CharField(
                    required = True,
                    label='Unit of Measure',
                    widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),),
    active = forms.BooleanField(
                    required = False,
                    label='Active',
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),),
    status = forms.CharField(
                    required = True,
                    disabled=True,
                    label='Status',
                    widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),),
    
    class Meta:
        model = Product
        fields = ['code', 'description', 'quantity_on_hand', 'selling_price', 'unit_of_measure',
                  'active', 'status']


class InvoiceForm(forms.ModelForm):
    THE_OPTIONS = [
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('30 days', '30 days'),
        ('60 days', '60 days'),
    ]
    STATUS_OPTIONS = [
        ('CURRENT', 'CURRENT'),
        ('EMAIL_SENT', 'EMAIL_SENT'),
        ('OVERDUE', 'OVERDUE'),
        ('PARTIALLY PAID', 'PARTIALLY PAID'),
        ('FULLY PAID', 'FULLY PAID'),
        ('CREDITED', 'CREDITED'),
    ]

    reference = forms.CharField(
                    required = True,
                    label='Reference',
                    disabled=True,
                    widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),)
    paymentTerms = forms.ChoiceField(
                    choices = THE_OPTIONS,
                    required = True,
                    label='Select Payment Terms',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    status = forms.ChoiceField(
                    choices = STATUS_OPTIONS,
                    required = True,
                    label='Change Invoice Status',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    notes = forms.CharField(
                    required = True,
                    label='Enter any notes for the client',
                    widget=forms.Textarea(attrs={'class': 'form-control mb-3'}))

    dueDate = forms.DateField(
                        required = True,
                        label='Invoice Due',
                        widget=DateInput(attrs={'class': 'form-control mb-3'}),)
    
    tax_total = forms.DecimalField(
                        required = True,
                        label='Tax Total',
                        disabled=True,
                        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    invoice_excl_total = forms.DecimalField(
                        required = True,
                        label='Invoice Excl Total',
                        disabled=True,
                        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    invoice_incl_total = forms.DecimalField(
                        required = True,
                        label='Invoice Incl Total',
                        disabled=True,
                        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('reference', css_class='form-group col-md-6'),
                Column('dueDate', css_class='form-group col-md-6'),
                css_class='form-row'),
            Row(
                Column('paymentTerms', css_class='form-group col-md-6'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'),
            'notes',

            Submit('submit', ' SAVE INVOICE '))

    class Meta:
        model = Invoice
        fields = ['reference', 'dueDate', 'paymentTerms', 'status', 'notes']


class InvoiceLineForm(forms.ModelForm):
    product = forms.ModelChoiceField(
                    queryset=Product.objects.all(),
                    required = True,
                    label='Select Product',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    
    quantity = forms.IntegerField(
                    required = True,
                    label='Product Quantity',
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)    
    
    price = forms.DecimalField(
                    required = True,
                    label='Product Price',
                    disabled=True,
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    tax_rate = forms.ModelChoiceField(
                    queryset=TaxRate.objects.all(),
                    required = True,
                    label='Select Tax Rate',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)
    
    #  Calculated Fields
    sale_tax = forms.DecimalField(
                    required = True,
                    label='Tax',
                    disabled=True,
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    sale_amount = forms.DecimalField(
                    required = True,
                    label='Sale Amount',
                    disabled=True,
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    line_total = forms.DecimalField(
                    required = True,
                    label='Line Total',
                    disabled=True,
                    widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}),)
    
    class Meta:
        model = InvoiceLine
        fields = ['product', 'quantity', 'price', 'tax_rate', 'sale_tax', 'sale_amount', 
                  'line_total']
        

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['clientName', 'clientLogo', 'addressLine1', 'province', 'postalCode', 
                  'phoneNumber', 'emailAddress', 'taxNumber']


class ClientSelectForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.initial_client = kwargs.pop('initial_client')
        self.CLIENT_LIST = Client.objects.all()
        self.CLIENT_CHOICES = [('-----', '--Select a Client--')]


        for client in self.CLIENT_LIST:
            d_t = (client.uniqueId, client.clientName)
            self.CLIENT_CHOICES.append(d_t)


        super(ClientSelectForm,self).__init__(*args,**kwargs)

        self.fields['client'] = forms.ChoiceField(
                                        label='Choose a related client',
                                        choices = self.CLIENT_CHOICES,
                                        widget=forms.Select(attrs={'class': 'form-control mb-3'}),)

    class Meta:
        model = Invoice
        fields = ['client']


    def clean_client(self):
        c_client = self.cleaned_data['client']
        if c_client == '-----':
            return self.initial_client
        else:
            return Client.objects.get(uniqueId=c_client)





















# <input type="email" class="form-control" id="floatingInput" placeholder="name@example.com">
# <input type="password" class="form-control" id="floatingPassword" placeholder="Password">
