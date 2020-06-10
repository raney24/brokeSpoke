from django.forms import DateTimeInput

class XDSoftDateTimePickerInput(DateTimeInput):
    template_name = 'xdsoft_datetimepicker.html'
class XDSoftDatePickerInput(DateTimeInput):
    template_name = 'xdsoft_datepicker.html'