from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .forms import *
from .models import *
from .functions import *

from django.contrib.auth.models import User, auth
from random import randint
from uuid import uuid4

from django.http import HttpResponse

import pdfkit
from django.template.loader import get_template
from django.views.generic.list import ListView
import os


class InvoiceList(ListView):
    model = Invoice
    template_name = 'partials/invoice-list.html'

    def get_queryset(self):
        return Invoice.objects.all().order_by('-id')
    
    
#Anonymous required
def anonymous_required(function=None, redirect_url=None):

   if not redirect_url:
       redirect_url = 'dashboard'

   actual_decorator = user_passes_test(
       lambda u: u.is_anonymous,
       login_url=redirect_url
   )

   if function:
       return actual_decorator(function)
   return actual_decorator


def index(request):
    context = {}
    return render(request, 'invoice/index.html', context)


@anonymous_required
def login(request):
    context = {}
    if request.method == 'GET':
        form = UserLoginForm()
        context['form'] = form
        return render(request, 'invoice/login.html', context)

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)

            return redirect('dashboard')
        else:
            context['form'] = form
            messages.error(request, 'Invalid Credentials')
            return redirect('login')


    return render(request, 'invoice/login.html', context)


@login_required
def dashboard(request):
    clients = Client.objects.all().count()
    invoices = Invoice.objects.all().count()
    paidInvoices = Invoice.objects.filter(status='PAID').count()


    context = {}
    context['clients'] = clients
    context['invoices'] = invoices
    context['paidInvoices'] = paidInvoices
    return render(request, 'invoice/dashboard.html', context)




# @login_required
# def invoices(request):
#     context = {}
#     invoices = Invoice.objects.all()
#     context['invoices'] = invoices

#     return render(request, 'invoice/invoices.html', context)


@login_required
def products(request):
    context = {}
    products = Product.objects.all()
    context['products'] = products

    return render(request, 'invoice/products.html', context)



@login_required
def clients(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients

    if request.method == 'GET':
        form = ClientForm()
        context['form'] = form
        return render(request, 'invoice/clients.html', context)

    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, 'New Client Added')
            return redirect('clients')
        else:
            messages.error(request, 'Problem processing your request')
            return redirect('clients')


    return render(request, 'invoice/clients.html', context)



@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


###--------------------------- Create Invoice Views Start here --------------------------------------------- ###

@login_required
def createInvoice(request):
    #create a blank invoice ....
    number = 'INV-'+str(uuid4()).split('-')[1]
    newInvoice = Invoice.objects.create(number=number)
    newInvoice.save()

    inv = Invoice.objects.get(number=number)
    return redirect('create-build-invoice', slug=inv.slug)




def createBuildInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the invoice lines - related to this invoice
    invoiceLines = InvoiceLine.objects.filter(invoice=invoice)


    context = {}
    context['invoice'] = invoice
    context['invoiceLines'] = invoiceLines

    if request.method == 'GET':
        inv_line_form  = InvoiceLineForm()
        inv_form = InvoiceForm(instance=invoice)
        select_client = ClientSelectForm(initial_client=invoice.client)
        context['inv_line_form'] = inv_line_form
        context['inv_form'] = inv_form
        context['select_client'] = select_client
        return render(request, 'invoice/create-invoice.html', context)

    if request.method == 'POST':
        inv_line_form  = InvoiceLineForm(request.POST)
        inv_form = InvoiceForm(request.POST, instance=invoice)
        select_client = ClientSelectForm(request.POST, initial_client=invoice.client, instance=invoice)

        if inv_line_form.is_valid():
            obj = inv_line_form.save(commit=False)
            obj.invoice = invoice
            obj.save()

            messages.success(request, "Invoice line added succesfully")
            return redirect('create-build-invoice', slug=slug)
        elif inv_form.is_valid and 'paymentTerms' in request.POST:
            inv_form.save()

            messages.success(request, "Invoice updated succesfully")
            return redirect('create-build-invoice', slug=slug)
        elif select_client.is_valid() and 'client' in request.POST:

            select_client.save()
            messages.success(request, "Client added to invoice succesfully")
            return redirect('create-build-invoice', slug=slug)
        else:
            context['inv_line_form'] = inv_line_form
            context['inv_form'] = inv_form
            context['select_client'] = select_client
            messages.error(request,"Problem processing your request")
            return render(request, 'invoice/create-invoice.html', context)


    return render(request, 'invoice/create-invoice.html', context)


def viewPDFInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the invoice lines - related to this invoice
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice)

    #Get Client Settings
    p_settings = Settings.objects.get(clientName='Premium Solar Energy')

    #Calculate the Invoice Total
    invoiceCurrency = 'R'
    invoiceTotal = 0.0
    if len(invoice_lines) > 0:
        for x in invoice_lines:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y
            invoiceCurrency = x.currency



    context = {}
    context['invoice'] = invoice
    context['invoice_lines'] = invoice_lines
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    context['invoiceCurrency'] = invoiceCurrency

    return render(request, 'invoice/invoice-template.html', context)



def viewDocumentInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the invoice liness - related to this invoice
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice)

    #Get Client Settings
    p_settings = Settings.objects.get(clientName='Premium Solar Energy')

    #Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(invoice_lines) > 0:
        for x in invoice_lines:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y



    context = {}
    context['invoice'] = invoice
    context['invoice_lines'] = invoice_lines
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

    #The name of your PDF file
    filename = '{}.pdf'.format(invoice.uniqueId)

    #HTML FIle to be converted to PDF - inside your Django directory
    template = get_template('invoice/pdf-template.html')


    #Render the HTML
    html = template.render(context)

    #Options - Very Important [Don't forget this]
    options = {
          'encoding': 'UTF-8',
          'javascript-delay':'10', #Optional
          'enable-local-file-access': None, #To be able to access CSS
          'page-size': 'A4',
          'custom-header' : [
              ('Accept-Encoding', 'gzip')
          ],
      }
      #Javascript delay is optional

    #Remember that location to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    #IF you have CSS to add to template
    css1 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'bootstrap.min.css')
    css2 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'dashboard.css')

    #Create the file
    file_content = pdfkit.from_string(html, False, configuration=config, options=options)

    #Create the HTTP Response
    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename = {}'.format(filename)

    #Return
    return response


def emailDocumentInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the invoice lines - related to this invoice
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice)

    #Get Client Settings
    p_settings = Settings.objects.get(clientName='Premium Solar Energy')

    #Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(invoice_lines) > 0:
        for x in invoice_lines:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y



    context = {}
    context['invoice'] = invoice
    context['invoice_lines'] = invoice_lines
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

    #The name of your PDF file
    filename = '{}.pdf'.format(invoice.uniqueId)

    #HTML FIle to be converted to PDF - inside your Django directory
    template = get_template('invoice/pdf-template.html')


    #Render the HTML
    html = template.render(context)

    #Options - Very Important [Don't forget this]
    options = {
          'encoding': 'UTF-8',
          'javascript-delay':'1000', #Optional
          'enable-local-file-access': None, #To be able to access CSS
          'page-size': 'A4',
          'custom-header' : [
              ('Accept-Encoding', 'gzip')
          ],
      }
      #Javascript delay is optional

    #Remember that location to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    #Saving the File
    filepath = os.path.join(settings.MEDIA_ROOT, 'client_invoices')
    os.makedirs(filepath, exist_ok=True)
    pdf_save_path = filepath+filename
    #Save the PDF
    pdfkit.from_string(html, pdf_save_path, configuration=config, options=options)


    #send the emails to client
    to_email = invoice.client.emailAddress
    from_client = p_settings.clientName
    emailInvoiceClient(to_email, from_client, pdf_save_path)

    invoice.status = 'EMAIL_SENT'
    invoice.save()

    #Email was send, redirect back to view - invoice
    messages.success(request, "Email sent to the client succesfully")
    return redirect('create-build-invoice', slug=slug)


def deleteInvoice(request, slug):
    try:
        Invoice.objects.get(slug=slug).delete()
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    return redirect('invoices')


def createClient(request):
    #create a new client ....
    uniqueId = str(uuid4()).split('-')[4]
    newClient = Client.objects.create(uniqueId=uniqueId)
    newClient.save()

    c = Client.objects.get(uniqueId=uniqueId)
    return redirect('client', uniqueId=c.uniqueId)

def add_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'clientListChanged'})
    else:
        form = ClientForm()
    return render(request, 'client-form.html', {'form': form})
    # 
def edit_client(request, uniqueId):
    client = Client.objects.get(uniqueId=uniqueId)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'clientListChanged'})
    else:
        form = ClientForm(instance=client)
    return render(request, 'client-form.html', {'form': form, client: client})



def companySettings(request):
    company = Settings.objects.get(clientName='Premium Solar Energy')
    context = {'company': company}
    return render(request, 'invoice/company-settings.html', context)




























###
##
#
