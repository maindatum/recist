from django.forms import DateInput, TextInput


class FDatePickerInput(DateInput):
    template_name = 'widgets/fdatepicker.html'

    # class Media:
    #     css = {#
    #         # 'all':["https://cdnjs.cloudflare.com/ajax/libs/datepicker/0.6.5/datepicker.min.css",
    #         # ],
    #         # 'all':[
    #         #
    #         # ]
    #     }
    #     js = [
    #         "https://code.jquery.com/jquery-3.4.1.slim.min.js",
    #         "https://cdnjs.cloudflare.com/ajax/libs/datepicker/0.6.5/datepicker.min.js",
    #         "static/widgets/fdatepicker/datepicker.js",
    #     ]

    def build_attrs(self, *args, **kwargs):
        context = super().build_attrs(*args, **kwargs)
        context['data-toggle'] = 'datepicker'
        return context