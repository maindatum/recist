from django.db import models
from django.urls import reverse
from .fields import ImageWithThumbField
import os


class Patient(models.Model):
    unitnumb = models.IntegerField()
    ptname = models.CharField(max_length=16)
    regist_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ptname


class TumorTarget(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    target_no = models.IntegerField()
    votes = models.IntegerField(default=0)
    target_yn = models.BooleanField(default=False, verbose_name='target lesion Y/N')
    nontarget_yn = models.BooleanField(default=False, verbose_name='Non Target Y/N')
    reference_yn = models.BooleanField(default=False, verbose_name='reference Y/N')

    def __str__(self):
        tumortargetname = "patient id "+ str(self.patient_id) + ", target_no "+ str(self.target_no)
        return tumortargetname

class EvalModality(models.Model):
    CT = 'CT'
    MRI = 'MRI'
    PET = 'PET'
    USO = 'USO'
    HEAD_ORBIT = 'HEO'
    NECK = 'NEC'
    BRAIN = 'BRA'
    CHEST = 'CHE'
    ABDPEL = 'APE'
    SPINE = 'SPI'

    MODALITY_CHOICES = (
        (CT,'CT'),
        (MRI,'MRI'),
        (PET, 'PET'),
        (USO, 'US'),
    )
    BODY_CHOICES=(
        (HEAD_ORBIT, 'Head/Orbit/PNS'),
        (NECK, 'Neck'),
        (BRAIN, 'Brain'),
        (CHEST, 'Chest'),
        (ABDPEL, 'Abd/Pel'),
        (SPINE, 'Spine'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    modality_type = models.CharField(max_length=3, choices=MODALITY_CHOICES)
    body_field = models.CharField(max_length=10, choices=BODY_CHOICES)
    image_date = models.DateField()
    saved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        evalmodaldate = str(self.get_body_field_display())+" "+ str(self.get_modality_type_display()) +", taken at " +str(self.image_date)
        return evalmodaldate

    def get_absolute_url(self):
        return reverse('chemoresponse:eval-modal-create', args=(self.patient_id))


class TargetImage(models.Model):
    target = models.ForeignKey(TumorTarget, on_delete=models.CASCADE)
    target_image = ImageWithThumbField(upload_to='target_image', null=True)
    image_modal = models.ForeignKey(EvalModality, on_delete=models.CASCADE)
    baseline = models.BooleanField(default=False, verbose_name='baseline')
    lesion_measure = models.FloatField(null=True, blank=True, verbose_name='Measure')
    image_desc = models.TextField(blank=True, verbose_name='특기사항')
    saved_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        targetimagename = str(self.target) +", taken at " +str(self.image_modal.image_date)
        return targetimagename

    def get_absolute_url(self):
        return reverse('chemoresponse:targetimage-detail', args=(self.target.patient_id, self.target.target_no, self.id))

    def delete(self,*args, **kwargs):
        print('this is thumb_path in delete func',self.target_image.thumb_path)
        if os.path.exists(self.target_image.thumb_path):
            os.remove(self.target_image.thumb_path)
        os.remove(self.target_image.path)
        super(TargetImage,self).delete(*args, **kwargs)
