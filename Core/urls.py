from django.contrib import admin
from django.urls import path
from.import views

urlpatterns = [
    
    path('',views.home,name="home"),
    path('admin_dashboard/',views.admin_dashboard,name="admin_dashboard"),
    path('active_hazard/',views.active_hazards,name="Active_hazard"),
    path('hospital_details/',views.Hospital_details,name="Hospital_details"),
    path('hospital/<int:id>/dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hazard_report/',views.Hazard_report,name="Hazard_report"),
    path('hazard_detail/<int:id>/',views.hazard_detail,name="hazard_detail"),
    path('hazard/<int:id>/edit/',views.edit_hazard,name="edit_hazard"),
    path('hazard/<int:id>/delete/',views.delete_hazard,name="delete_hazard"),
    path('add_hospital/',views.add_hospital,name="add_hospital"),
    path('hospital_list/',views.hospital_list,name="hospital_list"),
    path('patients/', views.patient_list, name='patient_list'),
    path('patient/<int:id>/', views.patient_detail, name='patient_detail'),
    path('hospital/<int:id>/edit/',views.edit_hospital,name="edit_hospital"),
    path('hospital/<int:id>/delete/',views.delete_hospital,name="delete_hospital"),
    path(
    'hospital/<int:hospital_id>/hazard/<int:hazard_id>/add-patient/',
    views.add_patient,
    name='add_patient'
),
    path('patient/<int:id>/edit/',views.edit_patient,name="edit_patient"),
    path('patient/<int:id>/transfer/', views.transfer_patient, name='transfer_patient'),
    path('patient/<int:id>/release/', views.release_patient, name='release_patient'),
    path('missing_complaint/<int:hazard_id>/missing/',views.add_missing_complaint,name='add_missing_complaint'),
    path('missing_complaint/<int:id>/edit/',views.edit_missing_complaint,name="edit_missing_complaint"),
    path('missing_complaint/<int:id>/delete/',views.delete_missing_complaint,name="delete_missing_complaint"),
    path('register/',views.register,name="register"),
    path('create-initial-admin/', views.create_initial_admin, name='create_initial_admin'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('profile/',views.user_profile,name="profile"),
    path(
    "my-missing-complaints/",
    views.missing_complaints,
    name="my_missing_complaints"
),
    path("patient/<int:patient_id>/matches/",views.ai_match_dashboard, name="ai_match_dashboard"),
    path("complaint/<int:complaint_id>/matches",views.complaint_match_dashboard,name="complaint_match_dashboard"),
path(
    "analysis/<int:match_id>/",
    views.matching_analysis,
    name="matching_analysis",
),
path('patient/<int:patient_id>/identify/',views.identify_patient,name = 'identify_patient'),
    # Duplicate transfer route removed. Use 'patient/<int:id>/transfer/' above.
path('userprofile/edit/',views.edit_profile,name='edit_profile'),
path(
    'patient/<int:patient_id>/delete/',
    views.delete_patient,
    name='delete_patient'
),
path('view_hospital/<int:hospital_id>/',views.view_hospital,name='view_hospital'),
path(
    'hospital/<int:id>/edit/',
    views.edit_hospital,
    name='edit_hospital'
),

path(
    'emergency-report/',
    views.emergency_report,
    name='emergency_report'
),

path(
    'emergency-report/success/',
    views.emergency_report_success,
    name='emergency_report_success'
),

path(
    'emergency-reports-admin/',
    views.emergency_admin,
    name='emergency_admin'
),

path(
    'emergency/<int:report_id>/verify/',
    views.verify_emergency,
    name='verify_emergency'
),

path(
    'emergency/<int:report_id>/reject/',
    views.reject_emergency,
    name='reject_emergency'
),
]