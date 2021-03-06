from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django import forms
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.apps.discounts.models import Discount
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.apps.discounts.utils import assign_discount

END_DT_INITIAL = datetime.now() + timedelta(weeks=4)

class DiscountForm(TendenciBaseForm):
    class Meta:
        model = Discount
        fields = (
            'discount_code',
            'value',
            'start_dt',
            'end_dt',
            'never_expires',
            'cap',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail',
            )

        fieldsets = [('Discount Information', {
                      'fields': ['discount_code',
                                 'value',
                                 'cap',
                                 'never_expires',
                                 'start_dt',
                                 'end_dt',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]
        
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
        
    def __init__(self, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        if not self.user.profile.is_superuser:
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            
    def clean_discount_code(self):
        data = self.cleaned_data['discount_code']
        try:
            discount = Discount.objects.get(discount_code=data)
        except Discount.DoesNotExist:
            return data
        if not discount == self.instance:
            raise forms.ValidationError('There a discount for this code already exists.')
        return data

    def clean(self):
        cleaned_data = self.cleaned_data
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")

        if start_dt > end_dt:
            errors = self._errors.setdefault("end_dt", ErrorList())
            errors.append(u"This cannot be \
                earlier than the start date.")

        # Always return the full collection of cleaned data.
        return cleaned_data

class DiscountCodeForm(forms.Form):
    price = forms.DecimalField(decimal_places=2)
    code = forms.CharField()
    count = forms.IntegerField()
    
    def clean(self):
        code = self.cleaned_data.get('code', '')
        count = self.cleaned_data.get('count', 1)
        try:
            discount = Discount.objects.get(discount_code=code)
        except Discount.DoesNotExist:
            raise forms.ValidationError('This is not a valid discount code.')
        if not discount.available_for(count):
            raise forms.ValidationError('This is not a valid discount code.')
        return self.cleaned_data
        
    def new_price(self):
        code = self.cleaned_data['code']
        price = self.cleaned_data['price']
        count = self.cleaned_data['count']
        discount = Discount.objects.get(discount_code=code).value * Decimal(count)
        new_price = price - discount
        if new_price < 0:
            new_price = Decimal('0.00')
        return (new_price, discount)
    
    
class DiscountHandlingForm(forms.Form):
    """
    Process a list of prices, and returns a list of discounted prices.
    """
    prices = forms.CharField()
    code = forms.CharField()
    
    def clean(self):
        code = self.cleaned_data.get('code', '')
        [self.discount] = Discount.objects.filter(discount_code=code)[:1] or [None]
        if not self.discount:
            raise forms.ValidationError('This is not a valid discount code.')
        
        if not self.discount.never_expires:
            now = datetime.now()
            if self.discount.start_dt > now:
                raise forms.ValidationError('This discount code is not in effect yet.')
            if self.discount.end_dt <= now:    
                raise forms.ValidationError('This discount code has expired.')
        
        self.limit = 0
        if self.discount.cap != 0:
            self.limit = self.discount.cap - self.discount.num_of_uses()
            if self.limit <= 0:
                raise forms.ValidationError('This discount code has passed the limit.')
        
        return self.cleaned_data
        
    def get_discounted_prices(self):
        prices = self.cleaned_data['prices']
        price_list = [Decimal(price) for price in prices.split(';')]
        
        return assign_discount(price_list, self.discount)
        
            
            
        
        
        

