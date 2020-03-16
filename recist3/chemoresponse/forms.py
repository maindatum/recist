from django import forms
from .models import Patient, TumorTarget, TargetImage, EvalModality
from django.utils.html import mark_safe
from django.conf import settings
from .widgets import FDatePickerInput
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.db.models import Max
import base64

class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if str(value) == '':
            html1 = "<img id='id_image' style='display:block' class='rounded float-left d-block'/>"
        else:
            html1 = "<img id='id_image' style='display:block' class='rounded float-left d-block' src='" + settings.MEDIA_URL + str(value) + "'/>"
        return mark_safe(html1)


class TargetImageForm(forms.ModelForm):
    image_container = forms.CharField(required=False, widget=forms.Textarea())
    class Meta:
        model = TargetImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TargetImageForm, self).__init__(*args, **kwargs)
        for el in kwargs:
            print(el)
        self.fields['target_image'].required = False
        print("this is target image form")

    def clean_target_image(self):
        data = self.cleaned_data['target_image']
        return data

    def clean_image_container(self):
        data = self.cleaned_data['image_container']
        return data

    def clean(self):
        data = self.cleaned_data
        for el in data:
            print ('this is cleaned_data in clean_target_image', el)
        print('this is clean target image function validation!!!')
        imgdata = self.cleaned_data['image_container']
        # print('imgdata is:', imgdata)
        if self.cleaned_data['target_image']:
            print('there is target_image')
            if not imgdata:
                print('there target_image but, no image at container')
                return self.cleaned_data
            else:
                print('there is target image and image at container')
                self.add_error('target_image','뭐여 양쪽에 image다 넣어놓고-target-image.')
                self.add_error('image_container', '뭐여 양쪽에 image다 넣어놓고-image container.')
                raise forms.ValidationError("뭐여 양쪽에 image다 넣어놓고.")
        elif imgdata:
            print('there is no target_image but image at container')
            return self.cleaned_data
        else:
            self.add_error('target_image', '양쪽에 다 없다 야 target-image.')
            self.add_error('image_container', '양쪽에 다 없다 야 image container.')
            raise forms.ValidationError("양쪽에 다 업다 야.")


    def save(self, commit=True):
        print('this is save function.')
        # self.instance.image_container.delete(False)
        for el in self.cleaned_data:
            print ('this is cleaned_data', el)
        imgdata = self.cleaned_data['image_container']
        print('this is imadata',imgdata)
        if not imgdata:
            print('this is target image', self.instance.target_image)
            print('file name is..', self.instance.target_image.name)
            origin_fname = self.instance.target_image.name
            origin_fname_ext = origin_fname.split('.')[-1]
            imgdate_str = str(self.instance.image_modal.image_date)
            ptname_str = str(self.instance.image_modal.patient.ptname)
            imgmodal_str = str(self.instance.image_modal.modality_type)
            unitnumb_str = str(self.instance.image_modal.patient.unitnumb)
            bodyfield_str = str(self.instance.image_modal.body_field)
            targetno_str = str(self.instance.target.target_no)
            if self.instance.target.targetimage_set.exists():
                imgserial_str = str(int(self.instance.target.targetimage_set.aggregate(Max('pk'))['pk__max']) + 1)
            else:
                imgserial_str = str(1)
            fname = unitnumb_str +'-' +ptname_str +'-' + bodyfield_str+ '-' + imgmodal_str +'-'+ imgdate_str +'-TN-'+targetno_str+'-SN-'+imgserial_str
            print('file name is', fname, type(fname))
            self.instance.target_image.name = fname + '.' + origin_fname_ext
        else:
            print('hello this presents imgdata')
            ftype = 'png'
            print(ftype)
            # fname = slugify(self.instance.title)

            imgdate_str = str(self.instance.image_modal.image_date)
            ptname_str = str(self.instance.image_modal.patient.ptname)
            imgmodal_str = str(self.instance.image_modal.modality_type)
            unitnumb_str = str(self.instance.image_modal.patient.unitnumb)
            bodyfield_str = str(self.instance.image_modal.body_field)
            targetno_str = str(self.instance.target.target_no)
            if self.instance.target.targetimage_set.exists():
                imgserial_str = str(int(self.instance.target.targetimage_set.aggregate(Max('pk'))['pk__max']) + 1)
            else:
                imgserial_str = str(1)
            fname = unitnumb_str + '-' + ptname_str + '-' + bodyfield_str + '-' + imgmodal_str + '-' + imgdate_str + '-TN-' + targetno_str + '-SN-' + imgserial_str
            imgdata64 =base64.b64decode(imgdata)
            print(fname)
            self.instance.target_image.save('%s.%s' % (fname, ftype), ContentFile(imgdata64))
        print('wow wow success')
        return super(TargetImageForm, self).save(commit=commit)


class TargetCreateForm(forms.ModelForm):
    class Meta:
        model = TumorTarget
        fields = ('target_no','target_yn','nontarget_yn', 'reference_yn')

    # def __init__(self, *args, **kwargs):
    #     patient_id = int(kwargs.pop('pk'))
    #     super(TargetCreateForm, self).__init__(*args, **kwargs)
    #     self.queryset = TumorTarget.objects.get(pk=patient_id)

class TargetUpdateForm(forms.ModelForm):
    class Meta:
        model = TumorTarget
        fields = ('target_no','target_yn','nontarget_yn', 'reference_yn')


class PatientCreateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ('unitnumb', 'ptname')

class TargetImageUpdateForm(forms.ModelForm):
    class Meta:
        model = TargetImage
        fields = '__all__'

class EvalModalCreateForm(forms.ModelForm):
    class Meta:
        model = EvalModality
        fields = '__all__'
        widgets={
            'image_date':FDatePickerInput(attrs={
                'autocomplete': 'off'
            }
            )
        }

    def __init__(self, *args, **kwargs):
        super(EvalModalCreateForm,self).__init__(*args,**kwargs)
        instance = getattr(self,'instance', None)
        if instance and instance.pk:
            self.fields['patient'].disabled = True
        else:
            self.fields['pateint'].disabled = False


class EvalModalUpdateForm(forms.ModelForm):
    class Meta:
        model = EvalModality
        fields = '__all__'
        widgets={
            'image_date':FDatePickerInput(attrs={
                'autocomplete': 'off'
            }
            )
        }

    def __init__(self, *args, **kwargs):
        super(EvalModalUpdateForm,self).__init__(*args,**kwargs)
        instance = getattr(self,'instance', None)
        if instance and instance.pk:
            self.fields['patient'].disabled = True
        else:
            self.fields['pateint'].disabled = False
