from django.forms import DateTimeInput

class XDSoftDateTimePickerInput(DateTimeInput):
    template_name = 'xdsoft_datetimepicker.html'
# class AutoCompleteSearch(Charfield):
#     template_name = 'ajax_search.html'