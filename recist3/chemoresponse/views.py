from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.views import generic
from .models import Patient, TumorTarget, TargetImage, EvalModality
from django.urls import reverse
from .forms import TargetImageForm, TargetCreateForm, PatientCreateForm, TargetImageUpdateForm, EvalModalCreateForm,\
    TargetUpdateForm, EvalModalUpdateForm
from django.db.models import Avg, Max, Min, Sum
from PIL import ImageGrab
import base64
from io import BytesIO, StringIO
import codecs
import pandas as pd
import json
from django.template.loader import render_to_string
import datetime


# def imagegrabing(request):
#     img = ImageGrab.grabclipboard()
#     print(img)
#
#     context = {}
#     if img:
#         img_bytes = BytesIO()
#         img.save(img_bytes, format='png')
#         img_base64 = codecs.encode(img_bytes.getvalue(),'base64')
#         img_base64_text = codecs.decode(img_base64,'ascii')
#         html_img_tag = "<img height=\"200px\" src='data:image/png;base64, %s'/>" % img_base64_text
#         print(html_img_tag)
#         context['is_image'] = True
#         context['html_img_tag']=html_img_tag
#         print('there is image')
#         context['img_base64_text'] = img_base64_text
#     else:
#         context['is_image'] = False
#         context['html_img_tag']=img
#         print('there is no image')
#     return JsonResponse(context)


class PatientListView(generic.ListView):
    template_name = 'chemoresponse/patientlist.html'
    context_object_name = 'latest_patient_list'

    def get_queryset(self):
        return Patient.objects.order_by('regist_date')

class PatientCreateView(generic.CreateView):
    template_name = 'chemoresponse/patient-create.html'
    model = Patient
    form_class = PatientCreateForm

    def get_success_url(self):
        return reverse('chemoresponse:patientlist')

class OverallResponseView(generic.DetailView):
    model = Patient
    template_name = "chemoresponse/overall-response.html"
    context_object_name = 'response_target_list'

    def post(self, request, *args, **kwargs):
        data=dict()
        print('this is post function', self.args, self.request.POST)
        print(request.POST.get('baseline_info'))
        self.object = self.get_object()
        baseline_info = request.POST.get('baseline_info')
        print('this is object', self.object)
        context = self.get_context_data()
        print('this is post context', context)

        # patient_id = self.kwargs['pk']
        # patient = Patient.objects.get(pk=patient_id)
        # self.kwargs['object']=patient
        data['html_table'] = render_to_string('chemoresponse/or-partial.html',
                                             context,
                                             request=request,
                                             )
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        baseline_info=self.request.POST.get('baseline_info')

        print('this is baseline_info of get_context_data',baseline_info)
        print(self.kwargs)# baselineinfo =self.kwargs['baselineinfo']
        context = super(OverallResponseView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['pk']
        patient=Patient.objects.get(pk=patient_id)
        targetimage=TargetImage.objects.filter(target__patient_id__exact=patient.id)
        lm = targetimage.values(
            'id','baseline','lesion_measure','target__target_no','target', 'image_modal__image_date'
        )
        # print(lm)
        # print(list(lm))
        lm_df = pd.DataFrame(list(lm))
        lm_df['image_month'] = lm_df.image_modal__image_date.map(lambda x : x.strftime('%Y-%m'))
        # print('this is lm_df', lm_df)
        lm_df_grouped = lm_df.groupby(['target__target_no', 'image_month'])
        lm_df_tgt_max= lm_df.pivot_table(index='target__target_no', columns='image_month', values='lesion_measure', margins=True, aggfunc=max)

        # print(lm_df_tgt_max.columns.to_list())
        # print('this is sum', lm_df_tgt_max.sum(axis=0))
        lm_df_tgt_max.loc['totalsum',:] = lm_df_tgt_max.sum(axis=0)
        baseline_info_list = []
        if not baseline_info:
            baseline_info_list = [0 for x in range(len(lm_df_tgt_max.columns))]
        else:
            baseline_info = json.loads(baseline_info)
            for key, val in baseline_info.items():
                print (type(val))
                if val ==True:
                    print('this is true value')
                    baseline_info_list.append(int(1))
                else:
                    print(val)
                    baseline_info_list.append(0)
        print(baseline_info_list)
        lm_df_tgt_max.loc['baseline', :] = baseline_info_list
        print('this is baseline', lm_df_tgt_max.loc[['baseline','totalsum'],])
        baseandsum = lm_df_tgt_max.loc[['baseline', 'totalsum'],]
        baseandsum_dict = baseandsum.to_dict('image_month')
        difference_list=[]
        percentchange_list=[]
        collist=lm_df_tgt_max.columns.to_list()
        # print('this is collist', collist)
        baseline = baseandsum_dict['totalsum'][collist[0]]
        # print('this is baseline', baseline)
        for key, val in baseandsum_dict['baseline'].items():
            difference = baseandsum_dict['totalsum'][key]-baseline
            percentchange=difference/baseline
            print('this is core values',key, val, baseline, difference)
            difference_list.append(difference)
            percentchange_list.append(format(percentchange,".2%"))
            if val == 1:
                new_baseline = baseandsum_dict['totalsum'][key]
                print(baseline)
                baseline=new_baseline
        print('this is difference', difference_list)
        lm_df_tgt_max.loc['difference', :] = difference_list
        lm_df_tgt_max.loc['percent', :] = percentchange_list
        lm_df_tgt_max_dict = lm_df_tgt_max.to_dict('index')

        # print('this is baseandsumdict', baseandsum_dict)
        #
        # for tgt, msm in lm_df_tgt_max_dict.items():
        #     for yr, msval in msm.items():
        #         print(msval)
        # print('this is dict', lm_df_tgt_max_dict)
        # # print('this is lm_df_grouped', lm_df_grouped)
        # # print(lm_df_grouped.sum())
        # # # for key, val in lm_df.items():
        # # #     print(key, val)
        context['response_dict']=lm_df_tgt_max_dict
        context['response_yrmonth'] = lm_df_tgt_max.columns.to_list()
        print(lm_df_tgt_max_dict)
        return context

class ResponseTargetListView(generic.DetailView):
    model = Patient
    template_name = "chemoresponse/response-target-list.html"
    context_object_name = 'response_target_list'

    def response_evaluation(self, targetimgs):
        response_dict = {}
        i = 0
        response_list = []
        if targetimgs:
            baseline_measure = targetimgs[0].lesion_measure
            for el in targetimgs:
                response_eval_dict = {}
                response_eval_dict['target_imageid'] = el.id
                response_eval_dict['target_index'] = i
                if not el.baseline:
                    try:
                        response_eval_dict['measure_differ'] = el.lesion_measure - baseline_measure
                        response_eval_dict['response_rate'] = (
                                                                          el.lesion_measure - baseline_measure) / baseline_measure * 100
                        response_list.append(int((el.lesion_measure - baseline_measure) / baseline_measure * 100))
                    except:
                        response_eval_dict['measure_differ'] = None
                        response_eval_dict['response_rate'] = None
                        response_list.append(None)
                else:
                    new_baseline = el.lesion_measure
                    baseline_measure = new_baseline
                    try:
                        response_eval_dict['measure_differ'] = el.lesion_measure - baseline_measure
                        response_eval_dict['response_rate'] = (
                                                                          el.lesion_measure - baseline_measure) / baseline_measure * 100
                        response_list.append(int((el.lesion_measure - baseline_measure) / baseline_measure * 100))
                    except:
                        response_eval_dict['measure_differ'] = None
                        response_eval_dict['response_rate'] = None
                        response_list.append(None)
                response_dict[i] = response_eval_dict
                i += 1
        return response_list

    def wrapping_response_dict(self, targetimgs, response_list):
        j = 0
        image_plus_response_dict_wrapped = {}
        if targetimgs:
            for el in targetimgs:
                image_plus_response_dict = {}
                image_plus_response_dict['img'] = el
                image_plus_response_dict['resp'] = response_list[j]
                image_plus_response_dict_wrapped['tgtimg' + str(el.id)] = image_plus_response_dict
                j = j + 1
            print(image_plus_response_dict_wrapped)
            for key, val in image_plus_response_dict_wrapped.items():
                print('interation:key', key)
                print('interation:val', val)
        return image_plus_response_dict_wrapped

    def get_context_data(self, *args, **kwargs):
        context = super(ResponseTargetListView,self).get_context_data(**kwargs)
        patient_id = self.kwargs['pk']
        tumortarget = TumorTarget.objects.filter(patient=patient_id).order_by('target_no')
        wrapped_targets = {}
        for tgt in tumortarget:
            targetimgs= tgt.targetimage_set.all().order_by('image_modal__image_date')
            print(targetimgs)
            response_list= self.response_evaluation(targetimgs)
            image_plus_response_dict_wrapped = self.wrapping_response_dict(targetimgs, response_list)
            wrapped_targets['target#'+str(tgt.id)] = image_plus_response_dict_wrapped
        context['tumortarget'] = tumortarget
        context['wrapped_targets'] = wrapped_targets
        print('this is context', context)
        return context



class TargetListView(generic.DetailView):
    model = Patient
    template_name = "chemoresponse/targetlist.html"

    def get_items_list(self, itemsdata):
        target_images_list = []
        for target_item in itemsdata:
            target_images = {}
            image_item = TargetImage.objects.filter(target=target_item).order_by('image_modal__image_date')
            if image_item:
                first_image_item = image_item[0]
                target_images['target_no'] = target_item.target_no
                target_images['first_image_item'] = first_image_item.target_image
            else:
                target_images['target_no'] = target_item.target_no
                target_images['first_image_item'] = None
            print(target_images)
            target_images_list.append(target_images)
        return target_images_list


    def get_context_data(self, **kwargs):
        context = super(TargetListView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        print('pk is', context['pk'])
        target_item_list = TumorTarget.objects.filter(patient=self.kwargs['pk'])
        target_item_list_targetlesion = target_item_list.filter(target_yn=True)
        target_item_list_nontargetlesion = target_item_list.filter(nontarget_yn=True)
        target_item_list_referencelesion = target_item_list.filter(reference_yn=True)
        target_item_list_noassignedlesion = target_item_list.filter(target_yn=False, nontarget_yn=False, reference_yn=False)
        target_item_list_values = target_item_list.values_list('target_no', flat=True).order_by('target_no')
        context['target_images_list'] = self.get_items_list(target_item_list)
        context['target_images_targetlesion_list'] = self.get_items_list(target_item_list_targetlesion)
        context['target_images_nontargetlesion_list'] = self.get_items_list(target_item_list_nontargetlesion)
        context['target_images_referencelesion_list'] = self.get_items_list(target_item_list_referencelesion)
        context['target_images_noassignedlesion_list'] = self.get_items_list(target_item_list_noassignedlesion)
        return context

class TargetListforImagesView(TargetListView):
    model = Patient
    template_name = "chemoresponse/targetlist-for-images.html"

class TargetListViewforUpdate(TargetListView):
    model = Patient
    template_name = "chemoresponse/targetlistforupdate.html"

class TargetCreateView(generic.CreateView):
    model = TumorTarget
    template_name = "chemoresponse/targetcreate.html"
    form_class = TargetCreateForm

    def get_form(self, form_class=form_class):
        form = super(TargetCreateView, self).get_form(form_class)
        patient_id = self.kwargs['pk']
        patient = Patient.objects.filter(pk=patient_id)
        # form.fields['patient'].queryset = patient
        max_target_no = TumorTarget.objects.filter(patient=patient[0]).aggregate(Max('target_no'))
        print(max_target_no['target_no__max'])

        if max_target_no['target_no__max'] is None:
            form.fields['target_no'].initial = 1
        else:
            form.fields['target_no'].initial = max_target_no['target_no__max']+1
        return form

    def get_success_url(self):
        patient_id = self.kwargs['pk']
        return reverse('chemoresponse:targetlist', kwargs={'pk':patient_id})

    def get_context_data(self, **kwargs):
        context = super(TargetCreateView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['pk']
        patient = Patient.objects.get(pk=patient_id)
        context['patient'] = patient
        print (context)
        # context['target_no'] = self.kwargs['target_no']
        # context['image_list'] = TumorTarget.objects.get(pk=self.kwargs['target_no']).targetimage_set.all()
        return context

    def form_valid(self,form):
        patient_id = self.kwargs['pk']
        patient = Patient.objects.get(pk=patient_id)
        form.instance.patient= patient
        return super(TargetCreateView,self).form_valid(form)

class TargetUpdateView(generic.UpdateView):
    model = TumorTarget
    template_name = "chemoresponse/targetupdate.html"
    form_class = TargetUpdateForm
    pk_url_kwarg = 'target_no'

    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        return reverse('chemoresponse:targetlist', kwargs={'pk':patient_id})


class EvalModalCreateView(generic.CreateView):
    model = EvalModality
    template_name = "chemoresponse/eval-modal-create.html"
    form_class = EvalModalCreateForm

    def get_form(self, form_class=form_class):
        form = super(EvalModalCreateView, self).get_form(form_class)
        patient_id = self.kwargs['pk']
        patient = Patient.objects.get(pk=patient_id)
        form.fields['patient'].initial = patient
        return form

    def get_success_url(self):
        patient_id = self.kwargs['pk']
        return reverse('chemoresponse:targetlist', kwargs={'pk':patient_id})

    def get_context_data(self, **kwargs):
        context = super(EvalModalCreateView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['pk']
        patient = Patient.objects.get(pk=patient_id)
        context['patient'] = patient
        print (context)
        return context

class EvalModalListView(generic.ListView):
    model = EvalModality
    template_name = "chemoresponse/eval-modal-list.html"
    pk_url_kwarg = 'patient_id'

    def get_context_data(self, **kwargs):
        context = super(EvalModalListView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(pk=patient_id)
        evalmodality = EvalModality.objects.filter(patient=patient).order_by('image_date')
        context['patient_id'] =patient_id
        context['evalmodaity'] = evalmodality
        print (context)
        return context

class EvalModalUpdateView(generic.UpdateView):
    model = EvalModality
    template_name = "chemoresponse/eval-modal-update.html"
    pk_url_kwarg = 'evalmodal_id'
    form_class = EvalModalUpdateForm

    def get_form(self, form_class=form_class):
        form = super(EvalModalUpdateView, self).get_form(form_class)
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(pk=patient_id)
        print('this is patient', patient)
        form.fields['patient'].object = patient
        form.fields['patient'].initial = patient
        return form

    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        return reverse('chemoresponse:evalmodality-list', kwargs={'patient_id':patient_id})

    def get_context_data(self, **kwargs):
        context = super(EvalModalUpdateView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(pk=patient_id)
        evalmodality = EvalModality.objects.filter(patient=patient)
        context['patient_id'] =patient_id
        context['evalmodaity'] = evalmodality
        print (context)
        return context


class TargetImageListView(generic.ListView):
    model = TumorTarget
    template_name = "chemoresponse/targetimagelist.html"
    context_object_name = 'tumortargetimage_list'
    pk_url_kwarg = 'target_no'

    # def get_object(self):
    #     return get_object_or_404(TargetImageListView, tumor_no=self.request.session['tumor_no'])
    #     # django CBV 에서 request 접근은 self.로부터 시작해야 한다.
    #     # url parameter 접근 시 detail CBV에서 pk가 아니라면 get_object 혹은 pk를 새로 지정 해야 한다.
    def get_context_data(self, **kwargs):
        context = super(TargetImageListView, self).get_context_data(**kwargs)
        context['patient_id'] = self.kwargs['patient_id']
        context['target_no'] = self.kwargs['target_no']
        patient = Patient.objects.get(pk=self.kwargs['patient_id'])
        targetimgs = TumorTarget.objects.get(patient=patient,
                                             target_no=self.kwargs['target_no']).targetimage_set.all().order_by(
            'image_modal__image_date')
        response_dict = {}
        i = 0
        response_list = []
        if targetimgs:
            baseline_measure = targetimgs[0].lesion_measure
            for el in targetimgs:
                response_eval_dict = {}
                response_eval_dict['target_imageid'] = el.id
                response_eval_dict['target_index'] = i
                if not el.baseline:
                    try:
                        response_eval_dict['measure_differ'] = el.lesion_measure - baseline_measure
                        response_eval_dict['response_rate'] = (el.lesion_measure - baseline_measure) / baseline_measure * 100
                        response_list.append(int((el.lesion_measure - baseline_measure) / baseline_measure * 100))
                    except:
                        response_eval_dict['measure_differ'] = None
                        response_eval_dict['response_rate']=None
                        response_list.append(None)
                else:
                    new_baseline = el.lesion_measure
                    baseline_measure = new_baseline
                    try:
                        response_eval_dict['measure_differ'] = el.lesion_measure - baseline_measure
                        response_eval_dict['response_rate'] = (el.lesion_measure - baseline_measure) / baseline_measure * 100
                        response_list.append(int((el.lesion_measure - baseline_measure) / baseline_measure * 100))
                    except:
                        response_eval_dict['measure_differ'] = None
                        response_eval_dict['response_rate']=None
                        response_list.append(None)
                response_dict[i] = response_eval_dict
                i += 1
        context['tumortargetimage_list'] = targetimgs
        context['tumor_response_dict']=response_dict
        context['tumor_response'] = response_list
        print(context)

        j = 0
        image_plus_response_dict_wrapped={}
        if targetimgs:
            for el in targetimgs:
                image_plus_response_dict = {}
                image_plus_response_dict['img'] = el
                image_plus_response_dict['resp'] = response_list[j]
                image_plus_response_dict_wrapped['pt'+ str(el.id)] = image_plus_response_dict
                j = j+1
            print(image_plus_response_dict_wrapped)
            for key, val in image_plus_response_dict_wrapped.items():
                print('interation:key', key)
                print('interation:val', val)
        context['image_plus_response_dict'] = image_plus_response_dict_wrapped
        print(context['image_plus_response_dict'])
        return context

    def get_queryset(self):
        print('patient id is', self.kwargs['patient_id'])
        print('target no is', self.kwargs['target_no'])
        patient = Patient.objects.get(pk=self.kwargs['patient_id'])
        tt = TumorTarget.objects.filter(patient=patient, target_no=self.kwargs['target_no'])
        print('patient name is',patient)
        print('filtered is',tt)
        print()
        targetimgs = TumorTarget.objects.get(patient=patient, target_no=self.kwargs['target_no']).targetimage_set.all().order_by(
            'image_modal__image_date')
        return targetimgs


class TargetImageDetailView(generic.DeleteView):
    model = TargetImage
    template_name = "chemoresponse/target-image-detail.html"
    context_object_name = 'targetimage_detail'
    pk_url_kwarg = 'image_no'

    def get_context_data(self, **kwargs):
        context = super(TargetImageDetailView, self).get_context_data(**kwargs)
        context['patient_id'] = self.kwargs['patient_id']
        context['target_no'] = self.kwargs['target_no']
        context['image_no'] = self.kwargs['image_no']
        return context


class TargetImageListViewforUpdate(TargetImageListView):
    model = TumorTarget
    template_name = "chemoresponse/targetimagelistforupdate.html"
    context_object_name = 'tumortargetimage_list'
    pk_url_kwarg = 'target_no'



class TargetImageUpdateView(generic.UpdateView):
    model=TargetImage
    template_name = "chemoresponse/targetimageupdate.html"
    form_class=TargetImageUpdateForm
    pk_url_kwarg = 'image_no'

    def get_context_data(self, **kwargs):
        context = super(TargetImageUpdateView, self).get_context_data(**kwargs)
        context['patient_id'] = self.kwargs['patient_id']
        context['target_no'] = self.kwargs['target_no']
        context['image_list'] = TumorTarget.objects.get(patient_id=context['patient_id'], target_no=context['target_no']).targetimage_set.all().order_by('image_date')
        return context

    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        target_no = self.kwargs['target_no']
        return reverse('chemoresponse:tumortargets', kwargs={'patient_id':patient_id,'target_no':target_no})

    def get_form(self, form_class=form_class):
        form = super(TargetImageUpdateView, self).get_form(form_class)
        patient_id = self.kwargs['patient_id']
        target_no = self.kwargs['target_no']
        print('patient_id', patient_id, "target_no", target_no)
        print(targetimage(self.request,patient_id,target_no))
         # = TumorTarget.objects.get(patient_id = patient_id, target_no=target_no)
        form.fields['target'].queryset = TumorTarget.objects.filter(patient_id=patient_id,target_no=target_no)
        form.fields['image_modal'].queryset = EvalModality.objects.filter(patient_id=patient_id).order_by('image_date')
        return form

class TargetImageDeleteView(generic.DeleteView):
    model = TargetImage
    template_name = "chemoresponse/targetimagedelete.html"
    pk_url_kwarg = 'image_no'

    def get_context_data(self, **kwargs):
        context = super(TargetImageDeleteView, self).get_context_data(**kwargs)
        context['patient_id'] = self.kwargs['patient_id']
        context['target_no'] = self.kwargs['target_no']
        context['image_list'] = TumorTarget.objects.get(patient_id=context['patient_id'], target_no=context['target_no']).targetimage_set.all().order_by('image_date')
        return context

    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        target_no = self.kwargs['target_no']
        return reverse('chemoresponse:tumortargets', kwargs={'patient_id':patient_id,'target_no':target_no})


class TargetImageCreateView(generic.CreateView):
    # model = TargetImage
    # fields = '__all__'
    form_class = TargetImageForm
    template_name = "chemoresponse/targetimagecreate.html"

    def get_context_data(self, **kwargs):
        context = super(TargetImageCreateView, self).get_context_data(**kwargs)
        context['patient_id'] = self.kwargs['patient_id']
        context['target_no'] = self.kwargs['target_no']
        context['image_list'] = TumorTarget.objects.get(patient_id=context['patient_id'], target_no=context['target_no']).targetimage_set.all().order_by('image_modal__image_date')
        return context

    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        target_no = self.kwargs['target_no']
        return reverse('chemoresponse:tumortargets', kwargs={'patient_id':patient_id,'target_no':target_no})

    # def get_form_kwargs(self):
    #     kwargs = super(TargetImageCreateView,self).get_form_kwargs()
    #     print(self.kwargs)
    #     kwargs['patient_id'] = self.kwargs['patient_id']
    #     kwargs['target_no'] = self.kwargs['target_no']
    #     print (kwargs)
    #     print (self.kwargs['patient_id'])
    #     return kwargs
    def get_form(self, form_class=form_class):
        form = super(TargetImageCreateView, self).get_form(form_class)
        patient_id = self.kwargs['patient_id']
        target_no = self.kwargs['target_no']
        print('patient_id', patient_id, "target_no", target_no)
        print(targetimage(self.request,patient_id,target_no))
         # = TumorTarget.objects.get(patient_id = patient_id, target_no=target_no)
        form.fields['target'].queryset = TumorTarget.objects.filter(patient_id=patient_id,target_no=target_no)
        form.fields['image_modal'].queryset = EvalModality.objects.filter(patient_id=patient_id).order_by('image_date')
        return form

    def form_valid(self,form):
        print('this is form-valid. function ')
        return super(TargetImageCreateView,self).form_valid(form)


def tumortarget(request, patient_id):
    # response = "Yore looking at tumortargets of patient_id %s."
    patient = get_object_or_404(Patient, pk=patient_id)
    try:
        selected_tumortarget = patient.tumortarget_set.get(pk=request.POST['tumortarget'])
    except (KeyError, TumorTarget.DoesNotExist):
        return render(request, 'chemoresponse/targetlist.html', {
            'patient': patient,
            'error_message': "you didnt select a choice"
        })
    else:
        selected_tumortarget.votes += 1
        selected_tumortarget.save()
    return HttpResponseRedirect(reverse('chemoresponse:results', args=(patient_id,)))


def targetimage(request, patient_id, targetimage_id):
    return HttpResponse("Youre seeing images of target %s of patient %s." % (targetimage_id, patient_id))


def results(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, 'chemoresponse/results.html', {'patient': patient})


class ResultsView(generic.DetailView):
    model = Patient
    template_name = 'chemoresponse/results.html'
