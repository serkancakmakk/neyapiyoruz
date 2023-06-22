from django import forms
from django.utils.safestring import mark_safe
import calendar

from django.utils.safestring import mark_safe

class CalendarWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            # Takvim widgetının HTML çıktısını oluşturun
            cal = calendar.HTMLCalendar().formatmonth(value.year, value.month)
            html = f'<div>{cal}</div>'
        else:
            # Geçerli bir tarih yoksa boş bir string döndürün
            html = ''
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        # Gelen veri dictinden değeri alın
        return data.get(name, None)
