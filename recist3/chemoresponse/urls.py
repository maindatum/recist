from django.urls import path

from . import views

app_name = 'chemoresponse'
urlpatterns = [
    path('', views.PatientListView.as_view(), name='patientlist'),
    path('targetlist-main/', views.PatientListforTargetView.as_view(), name='targetlist-main'),
    path('imagelist-main/', views.PatientListforResponseView.as_view(), name='imagelist-main'),
    path('<int:pk>/targetlist', views.TargetListView.as_view(), name='targetlist'),
    path('<int:pk>/targetlist-for-images', views.TargetListforImagesView.as_view(), name='target-list-for-images'),
    path('<int:pk>/response-target-list', views.ResponseTargetListView.as_view(), name='reseponse-target-list'),
    path('<int:pk>/overall-response', views.OverallResponseView.as_view(), name='overall-reseponse'),
    path('<int:pk>/targetcreate/', views.TargetCreateView.as_view(), name='targetcreate'),
    path('<int:pk>/targetupdatelist/', views.TargetListViewforUpdate.as_view(), name='target-update-list'),
    path('<int:patient_id>/evalmodality-list/', views.EvalModalListView.as_view(), name='evalmodality-list'),
    path('<int:patient_id>/evalmodality-list/<int:evalmodal_id>/update/', views.EvalModalUpdateView.as_view(), name='evalmodality-update'),
    path('<int:patient_id>/targetupdatelist/<int:target_no>/targetupdate/',views.TargetUpdateView.as_view(),
         name='target-update'),
    path('<int:pk>/eval-modal-create/', views.EvalModalCreateView.as_view(), name='eval-modal-create'),
    path('<int:patient_id>/tumortarget/<int:target_no>/', views.TargetImageListView.as_view(), name='tumortargets'),
    path('<int:patient_id>/tumortarget/<int:target_no>/imagecreate/', views.TargetImageCreateView.as_view(), name='targetimagecreate'),
    path('<int:patient_id>/tumortarget/<int:target_no>/imageupdatelist/',views.TargetImageListViewforUpdate.as_view(), name='tumortargets-updatelist'),
    path('<int:patient_id>/tumortarget/<int:target_no>/imageupdatelist/<int:image_no>', views.TargetImageDetailView.as_view(),
         name='targetimage-detail'),
    path('<int:patient_id>/tumortarget/<int:target_no>/imageupdatelist/<int:image_no>/update', views.TargetImageUpdateView.as_view(),
         name='targetimage-update'),
    path('<int:patient_id>/tumortarget/<int:target_no>/imageupdatelist/<int:image_no>/delete', views.TargetImageDeleteView.as_view(),
         name='targetimage-delete'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:patient_id>/tumortarget/<int:targetimage_id>/targetimage/', views.targetimage, name='targetimages'),
    # path('getimage/', views.imagegrabing, name="imagegrab"),
    path('patient/create', views.PatientCreateView.as_view(), name='patient-create')
    # path('', views.index, name='index'),
    # path('<int:patient_id>/', views.detail, name='detail'),
    # path('<int:patient_id>/tumortarget/', views.tumortarget, name='tumortargets'),
    # path('<int:patient_id>/results/', views.results, name='results'),
    # path('<int:patient_id>/tumortarget/<int:targetimage_id>/targetimage/', views.targetimage, name='targetimages'),
]