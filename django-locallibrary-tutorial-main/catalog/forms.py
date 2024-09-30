from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime  # for checking renewal date range.

from django import forms
#from .models import Rating



class RenewBookForm(forms.Form):
    """Form for a librarian to renew books."""
    renewal_date = forms.DateField(
            help_text="Введите на сколько хотите взять книгу. Максимальный срок: 1 месяц.")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Неправильно написана дата - максимальный срок: 1 месяц'))

        # Remember to always return the cleaned data.
        return data
    
#class RatingForm(forms.ModelForm):
#    class Meta:
#        model = Rating
#        fields = ['value']
#        widgets = {
#            'value': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
#        }