from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from uuid import uuid4
from django.contrib.auth.models import User
from django.urls import reverse


PHASE_CHOICES = [
    ('single_phase', 'Single Phase'),
    ('three_phase', 'Three Phase')
]
    
CATEGORY_CHOICES = [
    ('Stock', (
            ('mounting_structures', 'Mounting Structures'),
            ('inverter', 'Inverter'),
            ('battery', 'Battery'),
        )
     ),
    ('Office', (
            ('stationery', 'Stationery'),
            ('cleaning', 'Cleaning Material'),
            ('supplies', 'Supplies')
        )
     ),
    ('Consumables', (
            ('packaging', 'Packaging'),
            ('general', 'General'),
        )
     ),
    ('Unknown', 'Unknown'),
]


class Lead(models.Model):
    LEAD_STATUS_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('quoted', 'Quoted'),
    ('cancelled', 'Cancelled'),
]   
    # __Lead_FIELDS__
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=150)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    address_line3 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    details = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='Single Phase')
    agent = models.ForeignKey(User, related_name='leads', on_delete=models.DO_NOTHING, 
                              blank=True, null=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='New')
    
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'lead'
        verbose_name_plural = 'leads'

    def __str__(self):
        return self.name
    
    @property
    def status_info(self):
        res = {'class': None}

        if self.status == "New":
            res['class'] = 'text-info'
        elif self.status == "Contacted":
            res['class'] = 'text-warning'
        elif self.status == "Quoted":
            res['class'] = 'text-success'
        elif self.status == "Quoted":
            res['class'] = 'text-success'

        return res
    
    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.name, self.uniqueId))
                
        # Update the slug field
        self.slug = slugify('{} {}'.format(self.name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        
        super(Lead, self).save(*args, **kwargs)
    
    # __Lead_FIELDS__END

class LastNumberCounter(models.Model):
    last_serial_number = models.PositiveIntegerField(default=1)
    last_invoice_number = models.PositiveIntegerField(default=1)
    last_supplier_invoice_number = models.PositiveIntegerField(default=1)
    last_quote_number = models.PositiveIntegerField(default=1)
    last_job_number = models.PositiveIntegerField(default=1)
    past_purchase_order_number = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'last_number_counter'
        verbose_name_plural = 'last_number_counters'
        
    def get_next_invoice_number(self):
        current_number = self.last_invoice_number
        self.last_invoice_number += 1
        self.save()
        return current_number

    def get_next_supplier_invoice_number(self):
        current_number = self.last_supplier_invoice_number
        self.last_supplier_invoice_number += 1
        self.save()
        return current_number
    
    def get_next_quote_number(self):
        current_number = self.last_quote_number
        self.last_quote_number += 1
        self.save()
        return current_number
    
    def get_next_job_number(self):
        current_number = self.last_job_number
        self.last_job_number += 1
        self.save()
        return current_number
    
    def get_next_purchase_order_number(self):
        current_number = self.last_purchase_order_number
        self.last_purchase_order_number += 1
        self.save()
        return current_number
    

class Client(models.Model):

    PROVINCES = [
        ('Western Cape', 'Western Cape'), 
        ('Gauteng', 'Gauteng'),
        ('Free State', 'Free State'),
        ('Limpopo', 'Limpopo'),
    ]

    #Basic Fields.
    clientName = models.CharField(null=True, blank=True, max_length=200)
    addressLine1 = models.CharField(null=True, blank=True, max_length=200)
    town = models.CharField(null=True, blank=True, max_length=200)
    clientLogo  = models.ImageField(default='default_logo.jpg', upload_to='company_logos')
    province = models.CharField(choices=PROVINCES, blank=True, max_length=100)
    postalCode = models.CharField(null=True, blank=True, max_length=10)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    emailAddress = models.CharField(null=True, blank=True, max_length=100)
    taxNumber = models.CharField(null=True, blank=True, max_length=100)
    erf = models.CharField(max_length=50, null=True, blank=True, default='')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    #Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '{} {} {}'.format(self.clientName, self.province, self.uniqueId)


    def get_absolute_url(self):
        return reverse('client-detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {} {}'.format(self.clientName, self.province, self.uniqueId))

        self.slug = slugify('{} {} {}'.format(self.clientName, self.province, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Client, self).save(*args, **kwargs)
        
 
class TaxRate(models.Model):
    # __TaxRate_FIELDS__
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return

    class Meta:
        verbose_name = 'tax_rate'
        verbose_name_plural = 'tax_rates'
# __TaxRate_FIELDS__END
 

class Product(models.Model):
    code = models.CharField(null=True, blank=True, max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True,default='')
    quantity_on_hand = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Unknown')
    notes = models.CharField(max_length=255, null=True, blank=True, default='')
    # List of dictionaries: [{'quantity_in_stock': quantity, 'cost_price ': unit_cost, 'supplier': sourced_from, \
    #  'supplier_invoice': invoice_number, 'supplier_part_number': supplier_part, 'serial_numbers': {}}...]
    stack = models.JSONField(default=list)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_of_measure = models.CharField(max_length=5, null=True, blank=True, default='ea')
    status = models.CharField(max_length=20, null=True, blank=True, default='In Stock')
    active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
  
    @property
    def status_info(self):
        res = {'class': None}

        if self.quantity_on_hand > 0:
            self.status = "In Stock"
            res['class'] = 'text-success'
        elif self.quantity_on_hand < self.reorder_level: 
            self.status == "Reorder"
            res['class'] = 'text-warning'
        elif self.quantity_on_hand == 0:
            self.status == "Out of Stock"
            res['class'] = 'text-danger'

        return res
    
    #Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '{} {}'.format(self.code, self.uniqueId)


    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.code, self.uniqueId))

        self.slug = slugify('{} {}'.format(self.code, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Product, self).save(*args, **kwargs)


class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey(Product, related_name='serial_numbers', on_delete=models.CASCADE)
    sold = models.BooleanField()
    customer = models.CharField(max_length=100, null=True, blank=True)
    invoice = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'serial_number'
        verbose_name_plural = 'serial_numbers'


class Invoice(models.Model):
    TERMS = [
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('30 days', '30 days'),
        ('60 days', '60 days'),
    ]

    STATUS = [
        ('CURRENT', 'CURRENT'),
        ('EMAIL_SENT', 'EMAIL_SENT'),
        ('OVERDUE', 'OVERDUE'),
        ('PARTIALLY PAID', 'PARTIALLY PAID'),
        ('FULLY PAID', 'FULLY PAID'),
        ('CREDITED', 'CREDITED'),
    ]

    number = models.CharField(null=True, blank=True, max_length=100)
    dueDate = models.DateField(null=True, blank=True)
    paymentTerms = models.CharField(choices=TERMS, default='14 days', max_length=100)
    status = models.CharField(choices=STATUS, default='CURRENT', max_length=100)
    notes = models.TextField(null=True, blank=True)
    reference = models.CharField(null=True, blank=True, max_length=100, default='')
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_excl_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_incl_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    #RELATED fields
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)

    #Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '{} {}'.format(self.number, self.uniqueId)


    def get_absolute_url(self):
        return reverse('invoice-detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.number, self.uniqueId))

        self.slug = slugify('{} {}'.format(self.number, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Invoice, self).save(*args, **kwargs)

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='invoice_lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='invoice_lines', on_delete=models.DO_NOTHING)
    quantity_sold = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    serial_numbers = models.CharField(max_length=255, null=True, blank=True)
    tax_rate = models.ForeignKey(TaxRate, related_name='invoice_lines', on_delete=models.DO_NOTHING)
    sale_tax = models.DecimalField(max_digits=10, decimal_places=2)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    #Related Fields
    invoice = models.ForeignKey(Invoice, blank=True, null=True, on_delete=models.CASCADE)

    #Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '{} {}'.format(self.invoice, self.uniqueId)


    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.invoice, self.uniqueId))

        self.slug = slugify('{} {}'.format(self.invoice, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Product, self).save(*args, **kwargs)


class Settings(models.Model):

    PROVINCES = [
        ('Western Cape', 'Western Cape'),
        ('Gauteng', 'Gauteng'),
        ('Free State', 'Free State'),
        ('Limpopo', 'Limpopo'),
    ]

    #Basic Fields
    clientName = models.CharField(null=True, blank=True, max_length=200)
    clientLogo = models.ImageField(default='default_logo.jpg', upload_to='company_logos')
    addressLine1 = models.CharField(null=True, blank=True, max_length=200)
    town = models.CharField(null=True, blank=True, max_length=200)
    province = models.CharField(choices=PROVINCES, blank=True, max_length=100)
    postalCode = models.CharField(null=True, blank=True, max_length=10)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    emailAddress = models.CharField(null=True, blank=True, max_length=100)
    taxNumber = models.CharField(null=True, blank=True, max_length=100)


    #Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return '{} {} {}'.format(self.clientName, self.province, self.uniqueId)


    def get_absolute_url(self):
        return reverse('settings-detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {} {}'.format(self.clientName, self.province, self.uniqueId))

        self.slug = slugify('{} {} {}'.format(self.clientName, self.province, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Settings, self).save(*args, **kwargs)


class Supplier(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    address_line3 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'supplier'
        verbose_name_plural = 'suppliers'

    def __str__(self):
        return self.name   
    
    
class SupplierInvoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ('current', 'Current'),
        ('overdue', 'Overdue'),
        ('paid', 'Paid'),
        ('credited', 'Credited'),
    ]

    INVOICE_TERMS_CHOICES = [
        ('cash', 'Cash'),
        ('7_days', '7 Days'),
        ('14_days', '14 Days'),
        ('30_days', '30 Days'),
        ('60_days', '60 Days'),
        ('90_days', '90 Days'),
    ]
    supplier = models.ForeignKey(Supplier, related_name='supplier_invoices', on_delete=models.DO_NOTHING)
    invoice_number = models.CharField(max_length=20, null=False, blank=False)
    due_date = models.DateTimeField(null=True, blank=True)
    payment_terms = models.CharField(max_length=20, choices=INVOICE_TERMS_CHOICES, default='Cash')
    reference = models.CharField(max_length=255, null=True, blank=True, default='')
    notes = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=12, choices=INVOICE_STATUS_CHOICES, default='Due')
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_excl_total = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_incl_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.invoice_number

    class Meta:
        verbose_name = 'supplier_invoice'
        verbose_name_plural = 'supplier_invoices'
        
    @property
    def status_info(self):
        res = {'class': None}

        if self.status == "Paid":
            res['class'] = 'text-success'
        elif self.status == "Due":
            res['class'] = 'text-warning'
        elif self.status == "Credited":
            res['class'] = 'text-danger'

        return res
        
    def save(self, *args, **kwargs):
        # Calculate tax total, invoice_excl_total, and invoice_incl_total
        self.tax_total = sum(line.sale_tax for line in self.supplier_invoice_lines.all())
        self.invoice_excl_total = sum(line.line_total for line in self.supplier_invoice_lines.all())
        self.invoice_incl_total = self.invoice_excl_total + self.tax_total

        super(SupplierInvoice, self).save(*args, **kwargs)

        # Refresh the form data to reflect the updated totals
        if 'refresh_form' in kwargs and kwargs['refresh_form']:
            form = kwargs['form']
            form.instance = self
            form.fields['tax_total'].initial = self.tax_total
            form.fields['invoice_excl_total'].initial = self.invoice_excl_total
            form.fields['invoice_incl_total'].initial = self.invoice_incl_total


class SupplierInvoiceLine(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, related_name='supplier_invoice_lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='supplier_invoice_lines', on_delete=models.DO_NOTHING)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity_bought = models.PositiveIntegerField()
    part_number = models.CharField(max_length=255, null=True, blank=True)
    serial_numbers = models.CharField(max_length=255, null=True, blank=True)
    tax_rate = models.ForeignKey(TaxRate, related_name='supplier_invoice_lines', on_delete=models.DO_NOTHING)
    sale_tax = models.DecimalField(max_digits=10, decimal_places=2)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'supplier_invoice_line'
        verbose_name_plural = 'supplier_invoice_lines'

    def save(self, *args, **kwargs):
        # Calculate sale tax, sale amount, and line total
        self.sale_tax = (self.unit_price * self.quantity_bought * self.tax_rate.rate) / 100
        self.sale_amount = self.unit_price * self.quantity_bought
        self.line_total = self.sale_amount + self.sale_tax

        super(SupplierInvoiceLine, self).save(*args, **kwargs)
        
        
class Sale(models.Model):
    product = models.ForeignKey(Product, related_name='sales', on_delete=models.DO_NOTHING)
    invoice = models.ForeignKey(Invoice, related_name='sales', on_delete=models.DO_NOTHING)
    quantity_sold = models.PositiveIntegerField()
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_of_goods_sold = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField()
    serial_numbers = models.JSONField(default=list)

    class Meta:
        verbose_name = 'sale'
        verbose_name_plural = 'sales'
        
    def __str__(self):
        return self.product.name


class Quote(models.Model):
    QUOTE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    address_line3 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    quote_number = models.CharField(unique=True, max_length=50, null=True, blank=True)
    scope = models.CharField(max_length=1000, null=True, blank=True)
    quote_date = models.DateTimeField(auto_now_add=True)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    quote_excl_total = models.DecimalField(max_digits=10, decimal_places=2)
    quote_incl_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=QUOTE_STATUS_CHOICES, default='Draft')
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'quote'
        verbose_name_plural = 'quotes'

    def __str__(self):
        return self.quote_number
    
    @property
    def status_info(self):
        res = {'class': None}

        if self.status == "Draft":
            res['class'] = 'text-info'
        elif self.status == "Sent":
            res['class'] = 'text-warning'
        elif self.status == "Accepted":
            res['class'] = 'text-success'
        elif self.status == "Cancelled":
            res['class'] = 'text-success'

        return res


class QuoteLine(models.Model):
    quote = models.ForeignKey(Quote, related_name='quote_lines', on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, related_name='quote_lines', on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()
    tax_rate = models.ForeignKey(TaxRate, related_name='quote_lines', on_delete=models.DO_NOTHING)
    sale_tax = models.DecimalField(max_digits=10, decimal_places=2)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'quote_line'
        verbose_name_plural = 'quote_lines'
        
        
class PurchaseOrder(models.Model):
    PURCHASE_ORDER_STATUS_CHOICES = [
        ('unapproved', 'Unapproved'),
        ('approved', 'Approved'),
    ]
    supplier = models.ForeignKey(Supplier, related_name='purchase_orders', on_delete=models.DO_NOTHING)
    po_number = models.CharField(unique=True, max_length=50, null=True, blank=True)
    customer = models.CharField(max_length=255, null=True, blank=True)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    po_excl_total = models.DecimalField(max_digits=10, decimal_places=2)
    po_incl_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PURCHASE_ORDER_STATUS_CHOICES, default='Unapproved')
    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'purchase_order'
        verbose_name_plural = 'purchase_orders'

    def __str__(self):
        return self.po_number
    
    @property
    def status_info(self):
        res = {'class': None}

        if self.status == "Unapproved":
            res['class'] = 'text-warning'
        elif self.status == "Approved":
            res['class'] = 'text-success'

        return res


class PurchaseOrderLine(models.Model):
    po_number = models.ForeignKey(PurchaseOrder, related_name='po_lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='po_lines', on_delete=models.DO_NOTHING)
    reserved = models.BooleanField(default=False)
    reference = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    tax_rate = models.ForeignKey(TaxRate, related_name='po_lines', on_delete=models.DO_NOTHING)
    sale_tax = models.DecimalField(max_digits=10, decimal_places=2)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'purhase_order_line'
        verbose_name_plural = 'purchase_order_lines'   
        

class InputTax(models.Model):
    invoice = models.ForeignKey(SupplierInvoiceLine, related_name='input_taxes', on_delete=models.DO_NOTHING)
    tax_rate = models.ForeignKey(TaxRate, related_name='input_taxes', on_delete=models.DO_NOTHING)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'input_tax'
        verbose_name_plural = 'input_taxes'
        
    def __str__(self):
        return self.name
 

class OutputTax(models.Model):
    invoice = models.ForeignKey(InvoiceLine, related_name='output_taxes', on_delete=models.DO_NOTHING)
    tax_rate = models.ForeignKey(TaxRate, related_name='output_taxes', on_delete=models.DO_NOTHING)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'output_tax'
        verbose_name_plural = 'output_taxes'
               
    def __str__(self):
        return self.name
 
 
class Settings(models.Model):
    clientName = models.CharField(null=True, blank=True, max_length=200)
    addressLine1 = models.CharField(null=True, blank=True, max_length=200)
    town = models.CharField(null=True, blank=True, max_length=200)
    clientLogo  = models.ImageField(default='default_logo.jpg', upload_to='company_logos')
    province = models.CharField(blank=True, max_length=100)
    postalCode = models.CharField(null=True, blank=True, max_length=10)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    emailAddress = models.CharField(null=True, blank=True, max_length=100)
    taxNumber = models.CharField(null=True, blank=True, max_length=100)
    erf = models.CharField(max_length=50, null=True, blank=True, default='')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Utility fields
    uniqueId = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.clientName
    
    class Meta:
        verbose_name_plural = "Settings"
                          