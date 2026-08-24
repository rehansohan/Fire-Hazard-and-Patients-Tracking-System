from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from .forms import HazardReportForm,HospitalForm,PatientForm,MissingComplaintForm,RegisterForm,PatientTransferForm,ProfileForm,EmergencyReportForm
from.models import HazardReport,Hospital,Patient,MissingComplaint,Profile,PatientTransfer
from django.contrib.auth import get_user_model
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth import authenticate, login,logout
from.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_list_or_404
from Core.models import Patient,PatientMatch

from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .utils.matching_engine import (
    run_ai_matching,
    run_ai_matching_for_complaint
)
import base64

from django.core.files.base import ContentFile

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.category == 'admin'

def home(request):
    return render(request,'home.html')

def admin_dashboard(request):
    hazards_count = HazardReport.objects.count()
    active_count = HazardReport.objects.filter(status='active').count()
    resolved_count = HazardReport.objects.filter(status='resolved').count()
    patients_count = Patient.objects.count()
    hospitals_count = Hospital.objects.count()
    missing_count = MissingComplaint.objects.count()

    recent_hazards = HazardReport.objects.order_by('-created_at')[:6]
    recent_complaints = MissingComplaint.objects.order_by('-created_at')[:6]

    return render(request, 'admin_dashboard.html', {
        'hazards_count': hazards_count,
        'active_count': active_count,
        'resolved_count': resolved_count,
        'patients_count': patients_count,
        'hospitals_count': hospitals_count,
        'missing_count': missing_count,
        'recent_hazards': recent_hazards,
        'recent_complaints': recent_complaints,
    })

def Active_hazard(request):
    return render(request,'active_hazard.html')

def Hazard_details(request):
    return render(request,'hazard_details.html')

def Hospital_details(request):
    return render(request,'hospital.html')
@login_required
@permission_required("Core.add_hazardreport", raise_exception=True)
def Hazard_report(request):

     
    if request.method == 'POST':
         form = HazardReportForm(request.POST)
         if form.is_valid():
             hazard = form.save(commit=False)
             hazard.user = request.user
             hazard.save()
             return redirect('home')
         
    else:
        form= HazardReportForm()
        
    return render(request,'hazard_report.html',{'form':form})

def active_hazards(request):
    hazards = HazardReport.objects.filter(status='active')
    print("COUNT:", hazards.count())  

    return render(request, 'active_hazard.html', {
        'hazards': hazards
    })
    
    
def hazard_detail(request,id):
    hazard = get_object_or_404(HazardReport,id=id)
    query = request.GET.get('q')
    patients = hazard.patients.all()
    missing_form = MissingComplaintForm()
    if query:
        patients = patients.filter(
            Q(name__icontains=query)|
            Q(patient_id__icontains = query)
        )
    return render(
        request,
        'hazard_details.html',{
            'hazard':hazard,
            'patients':patients
            ,'missing_form': missing_form
        }
    )
    
@login_required
@permission_required("Core.add_hospital", raise_exception=True)
def add_hospital(request):
    if request.method=='POST':
        form = HospitalForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    else:
        form=HospitalForm()
    
    return render(request,'add_hospital.html',{'form':form})

def hospital_list(request):
    hospitals=Hospital.objects.all()
    print("Total hospitals:", hospitals.count())
    
    return render(request,'show_hospital.html',{'hospitals':hospitals})




from django.core.exceptions import PermissionDenied
@login_required
@permission_required(
    "Core.view_hospital_dashboard",
    raise_exception=True
)

def hospital_dashboard(request, id):
    hospital = get_object_or_404(Hospital, id=id)
    
    # Superuser সব hospital access করতে পারবে
    if not request.user.is_superuser:

        # User-এর assigned hospital-এর মধ্যে এই hospital আছে কিনা
        if not request.user.hospitals.filter(
            id=hospital.id
        ).exists():
            raise PermissionDenied
        
    patients = list(
        Patient.objects.select_related('hazard', 'created_by')
        .filter(hospital=hospital)
        .order_by('hazard__title', '-created_at')
    )

    grouped_patients = defaultdict(list)

    for patient in patients:
        grouped_patients[patient.hazard].append(patient)



    active_hazards = HazardReport.objects.filter(
        status='active'
    ).order_by('-created_at')


    hazard_groups = [
        {
            'hazard': hazard,
            'patients': grouped_patients.get(hazard, []),
            'patients_count': len(grouped_patients.get(hazard, [])),
            'critical_count': sum(
                1
                for patient in grouped_patients.get(hazard, [])
                if patient.condition == 'critical'
            ),
            'admitted_count': sum(
                1
                for patient in grouped_patients.get(hazard, [])
                if patient.status == 'admitted'
            ),
            'transferred_count': sum(
                1
                for patient in grouped_patients.get(hazard, [])
                if patient.status == 'transferred'
            ),
            'released_count': sum(
                1
                for patient in grouped_patients.get(hazard, [])
                if patient.status == 'released'
            ),
        }
        for hazard in active_hazards
    ]
    selected_hazard_id = request.GET.get('hazard')
    selected_group = None
    if hazard_groups:
        if selected_hazard_id:
            selected_group = next(
                (group for group in hazard_groups if str(group['hazard'].id) == str(selected_hazard_id)),
                hazard_groups[0],
            )
        else:
            selected_group = hazard_groups[0]

    selected_hazard = selected_group['hazard'] if selected_group else None
    selected_patients = selected_group['patients'] if selected_group else []

    transferred_patient_ids = []
    released_patient_ids = []
    if selected_hazard:
        transferred_patient_ids = list(
            PatientTransfer.objects.filter(
                patient__hazard=selected_hazard,
                from_hospital=hospital,
                action='transfer'
            ).values_list('patient_id', flat=True).distinct()
        )
        released_patient_ids = list(
            PatientTransfer.objects.filter(
                patient__hazard=selected_hazard,
                from_hospital=hospital,
                action='release'
            ).values_list('patient_id', flat=True).distinct()
        )

    selected_transferred_patients = Patient.objects.filter(
        id__in=transferred_patient_ids
    ).order_by('-created_at')
    selected_released_patients = Patient.objects.filter(
        id__in=released_patient_ids
    ).order_by('-created_at')

    return render(
        request,
        'hospital_dashboard.html',
        {
            'active_hazards':active_hazards,
            'hospital': hospital,
            'hazard_groups': hazard_groups,
            'selected_hazard': selected_hazard,
            'selected_group': selected_group,
            'selected_patients': selected_patients,
            'selected_transferred_patients': selected_transferred_patients,
            'selected_released_patients': selected_released_patients,
            'patients_count': len(patients),
            'admitted_count': sum(1 for patient in patients if patient.status == 'admitted'),
            'transferred_count': sum(1 for patient in patients if patient.status == 'transferred'),
            'released_count': sum(1 for patient in patients if patient.status == 'released'),
            'critical_count': sum(1 for patient in patients if patient.condition == 'critical'),
        }
    )


def patient_list(request):
    patients = Patient.objects.select_related('hospital', 'hazard').all()
    return render(request, 'patient_list.html', {'patients': patients})


def patient_detail(request, id):
    patient = get_object_or_404(
        Patient.objects.select_related('hospital', 'hazard', 'created_by').prefetch_related(
            'transfers__from_hospital',
            'transfers__to_hospital',
            'transfers__transferred_by',
        ),
        id=id,
    )
    transfers = patient.transfers.all().order_by('-created_at')
    return render(
        request,
        'patient_detail.html',
        {
            'patient': patient,
            'transfers': transfers,
        }
    )

import base64

from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import PatientForm
from .models import Patient

@login_required
@permission_required(
    "Core.add_patient",
    raise_exception=True
)
def add_patient(request, hospital_id, hazard_id):

    hospital = get_object_or_404(
        Hospital,
        id=hospital_id
    )

    hazard = get_object_or_404(
        HazardReport,
        id=hazard_id,
        hospitals=hospital
    )

    # User এই hospital-এর access আছে কিনা
    if not request.user.is_superuser:

        if not request.user.hospitals.filter(
            id=hospital.id
        ).exists():
            raise PermissionDenied

    if request.method == 'POST':

        form = PatientForm(request.POST)

        if form.is_valid():

            patient = form.save(commit=False)

            # Automatically assigned
            patient.hospital = hospital
            patient.hazard = hazard
            patient.created_by = request.user

            # Webcam image
            image_data = request.POST.get(
                'captured_image'
            )

            if image_data:

                try:

                    format, imgstr = image_data.split(
                        ';base64,'
                    )

                    ext = format.split('/')[-1]

                    patient.image = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'patient_{patient.name}.{ext}'
                    )

                except Exception as e:

                    print(
                        "Image Processing Error:",
                        e
                    )

            patient.save()

            run_ai_matching(patient)

            return redirect(
                'hospital_dashboard',
                hospital.id
            )

    else:

        form = PatientForm()

        form.fields['hospital'].initial = hospital
        form.fields['hazard'].initial = hazard

        form.fields['hospital'].disabled = True
        form.fields['hazard'].disabled = True

    return render(
        request,
        'add_patient.html',
        {
            'form': form,
            'hospital': hospital,
            'hazard': hazard,
        }
    )
from django.shortcuts import get_object_or_404

@login_required
def add_missing_complaint(request, hazard_id):

    hazard = get_object_or_404(HazardReport, id=hazard_id)

    if request.method == "POST":
        form = MissingComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            complaint = form.save(commit=False)

            complaint.user = request.user
            complaint.hazard = hazard

        

            complaint.save()
            run_ai_matching_for_complaint(complaint)

            return redirect("hazard_detail", hazard.id)

    else:
        form = MissingComplaintForm()

    return render(
        request,
        "add_missing_complaint.html",
        {
            "form": form,
            "hazard": hazard,
        },
    )
    
@login_required
def missing_complaints(request):
    complaints = MissingComplaint.objects.filter(
        user= request.user
        
    ).order_by("-created_at")
    return render(request,"my_complaints.html",{
        "complaints":complaints
    })

# Edit Hazard
def edit_hazard(request, id):
    hazard = get_object_or_404(HazardReport, id=id)
    if request.method == 'POST':
        form = HazardReportForm(request.POST, instance=hazard)
        if form.is_valid():
            form.save()
            return redirect('hazard_detail', id=hazard.id)
    else:
        form = HazardReportForm(instance=hazard)
    return render(request, 'edit_hazard.html', {'form': form, 'hazard': hazard})

# Delete Hazard
def delete_hazard(request, id):
    hazard = get_object_or_404(HazardReport, id=id)
    if request.method == 'POST':
        hazard.delete()
        return redirect('admin_dashboard')
    return render(request, 'delete_confirm.html', {'object': hazard, 'type': 'Hazard'})

# Edit Hospital
def edit_hospital(request, id):
    hospital = get_object_or_404(Hospital, id=id)
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            return redirect('hospital_list')
    else:
        form = HospitalForm(instance=hospital)
    return render(request, 'edit_hospital.html', {'form': form, 'hospital': hospital})

# Delete Hospital
def delete_hospital(request, id):
    hospital = get_object_or_404(Hospital, id=id)
    if request.method == 'POST':
        hospital.delete()
        return redirect('hospital_list')
    return render(request, 'delete_confirm.html', {'object': hospital, 'type': 'Hospital'})

# Edit Patient (Admin only)
def edit_patient(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only admins can edit patients.</p>")
    patient = get_object_or_404(Patient, id=id)
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('hazard_detail', id=patient.hazard.id)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'edit_patient.html', {'form': form, 'patient': patient})


@login_required
def transfer_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        from .forms import TransferPatientForm
        form = TransferPatientForm(request.POST)
        if form.is_valid():
            new_hospital = form.cleaned_data['hospital']
            note = form.cleaned_data.get('note')
            # record transfer
            from .models import PatientTransfer
            PatientTransfer.objects.create(
                patient=patient,
                from_hospital=patient.hospital,
                to_hospital=new_hospital,
                action='transfer',
                notes=note or '',
                transferred_by=request.user
            )
            # perform transfer
            patient.hospital = new_hospital
            patient.status = 'transferred'
            patient.save()
            if next_url:
                return redirect(next_url)
            return redirect('patient_list')
    else:
        from .forms import TransferPatientForm
        form = TransferPatientForm(initial={'hospital': patient.hospital})

    return render(
        request,
        'transfer_patient.html',
        {
            'form': form,
            'patient': patient,
            'next_url': next_url,
        }
    )


@login_required
def release_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        note = request.POST.get('note', '')
        from .models import PatientTransfer
        PatientTransfer.objects.create(
            patient=patient,
            from_hospital=patient.hospital,
            to_hospital=None,
            action='release',
            notes=note,
            transferred_by=request.user
        )
        patient.hospital = None
        patient.status = 'released'
        patient.save()
        if next_url:
            return redirect(next_url)
        return redirect('patient_list')

    # simple confirmation page
    return render(
        request,
        'confirm_release.html',
        {
            'patient': patient,
            'next_url': next_url,
        }
    )

# Delete Patient (Admin only)
def delete_patient(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only admins can delete patients.</p>")
    patient = get_object_or_404(Patient, id=id)
    hazard_id = patient.hazard.id
    if request.method == 'POST':
        patient.delete()
        return redirect('hazard_detail', id=hazard_id)
    return render(request, 'delete_confirm.html', {'object': patient, 'type': 'Patient'})

# Edit Missing Complaint (Admin only)
def edit_missing_complaint(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only admins can edit missing complaint reports.</p>")
    complaint = get_object_or_404(MissingComplaint, id=id)
    if request.method == 'POST':
        form = MissingComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            return redirect('hazard_detail', id=complaint.hazard.id)
    else:
        form = MissingComplaintForm(instance=complaint)
    return render(request, 'edit_missing_complaint.html', {'form': form, 'complaint': complaint})

# Delete Missing Complaint (Admin only)
def delete_missing_complaint(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Only admins can delete missing complaint reports.</p>")
    complaint = get_object_or_404(MissingComplaint, id=id)
    hazard_id = complaint.hazard.id
    if request.method == 'POST':
        complaint.delete()
        return redirect('hazard_detail', id=hazard_id)
    return render(request, 'delete_confirm.html', {'object': complaint, 'type': 'Missing Report'})

from django.contrib.auth.models import Group
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            group = Group.objects.get(name="General User")
            user.groups.add(group)

            Profile.objects.create(
                user=user,
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"]
            )

            return redirect("home")

        else:
            print(form.errors)

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
    
def user_login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(
                request,
                username = user_obj.username,
                password=password
            )
            if user is not None:
                login(request,user)
                return redirect('home')
            
            else:
                return HttpResponse("Invalid Password")
        except User.DoesNotExist:
            return HttpResponse("Email does not exit")
    
    return render(request,'user_login.html')

def user_logout(request):
    logout(request)
    return redirect('home')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile
from .forms import ProfileForm


@login_required
def user_profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("profile")

    else:
        form = ProfileForm(instance=profile)
        
    notifications = request.user.notifications.select_related(
        'patient'
        
    ).order_by('-created_at')
    unread_count = notifications.filter(
        is_read=False
    ).count()
    
    notifications.filter(
        is_read=False
    ).update(
        is_read=True
    )
    

    return render(request, "user_profile.html", {
        "form": form,
        "profile": profile,
        'user':request.user,
        'notifications':notifications,
        'unread_count': unread_count,
    })
    
    
    
def ai_match_dashboard(request, patient_id):
    patient=get_object_or_404(
        Patient,
        id=patient_id
    )
    matches = PatientMatch.objects.filter(
        patient=patient
    ).order_by("-similarity_score")
    
    return render(
        request,
        "ai_match_dashboard.html",
        {
            "patient":patient,
            "matches":matches,
        }
    )
    
    
def complaint_match_dashboard(request,complaint_id):
    complaint=get_object_or_404(
        MissingComplaint,
        id=complaint_id
    )
    matches= PatientMatch.objects.filter(
        complaint=complaint
    ).order_by("-similarity_score")[:5]
    verified_matches_count = PatientMatch.objects.filter(
        complaint=complaint,
        face_verified=True
    ).count()
    
    return render(
        request,
        "complaint_match_dashboard.html",
        {
            "complaint":complaint,
            "matches":matches,
            "verified_matches_count": verified_matches_count,
        }
    )
    
def matching_analysis(request, match_id):
    match = get_object_or_404(
        PatientMatch,
        id=match_id
    )

    return render(
        request,
        "analysis.html",
        {
            "match": match
        }
    )
    
from .models import Patient,Notification    
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def identify_patient(request, patient_id):

    patient = get_object_or_404(
        Patient,
        id=patient_id
    )

    if request.method == 'POST':

        if not patient.is_identified:

            patient.is_identified = True
            patient.identified_by = request.user

            patient.save(
                update_fields=[
                    'is_identified',
                    'identified_by'
                ]
            )

            Notification.objects.create(
                user=request.user,
                patient=patient,
                title='Patient Identified',
                message=(
                    f'Patient {patient.patient_id} '
                    f'has been successfully identified.'
                ),
                notification_type='identification'
            )

    return redirect('profile')





@login_required
def notifications(request):
    notifications = request.user.notifications.select_related(
        'patient'
    ).order_by('-created_at')
    notifications.filter(
        is_read=False
        
    ).update(is_read=True)
    return render(
        request,
        'notifications.html',
        {
            'notifications':notifications,
        }
    )
    
    
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method =='POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(
        request,
        'edit_user_profile.html',
        {
            'form':form
        }
    )
    
@login_required
def delete_patient(request,patient_id):
    patient=get_object_or_404(
        Patient,
        id=patient_id
    )
    if request.method=='POST':
        patient.delete()
        
        return redirect('Active_hazard')
    
    return render(
        request,
        'confirm_delete_patient.html',
        {
            'patient':patient
        }
    )
    
from .models import Hospital  
def view_hospital(request,hospital_id):
    hospital=get_object_or_404(
        Hospital,    
        id=hospital_id
    )
    return render(
        request,
        'view_hospital.html',
        {
            'hospital':hospital
        }
    )
    
    
    
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required

@permission_required("Core.change_hospital", raise_exception=True)
def edit_hospital(request, id):

    hospital = get_object_or_404(
        Hospital,
        id=id
    )

    if request.method == 'POST':

        form = HospitalForm(
            request.POST,
            request.FILES,
            instance=hospital
        )

        if form.is_valid():
            form.save()
            return redirect(
                'view_hospital',
                hospital_id=hospital.id
            )

    else:

        form = HospitalForm(
            instance=hospital
        )

    return render(
        request,
        'edit_hospital.html',
        {
            'form': form,
            'hospital': hospital
        }
    )
    
from django.contrib import messages 
import base64
import uuid

from django.core.files.base import ContentFile
@login_required
def emergency_report(request):

    if request.method == "POST":

        print("========== EMERGENCY REPORT ==========")

        print(
            "CAPTURED IMAGE EXISTS:",
            bool(request.POST.get("captured_image"))
        )

        print(
            "CAPTURED IMAGE LENGTH:",
            len(request.POST.get("captured_image", ""))
        )

        print(
            "CAPTURED VIDEO EXISTS:",
            bool(request.POST.get("captured_video"))
        )

        print(
            "CAPTURED VIDEO LENGTH:",
            len(request.POST.get("captured_video", ""))
        )

        print(
            "FILES:",
            request.FILES
        )

        print("======================================")


        # ============================================
        # CAMERA DATA
        # ============================================

        image_base64 = request.POST.get(
            "captured_image",
            ""
        )

        video_base64 = request.POST.get(
            "captured_video",
            ""
        )


        # ============================================
        # NORMAL FORM DATA
        # ============================================

        form = EmergencyReportForm(
            request.POST,
            request.FILES
        )


        if form.is_valid():

            emergency = form.save(
                commit=False
            )

            emergency.reporter = request.user

            emergency.status = "PENDING"


            # ============================================
            # SAVE CAPTURED IMAGE
            # ============================================

            if image_base64:

                try:

                    print(
                        "IMAGE DATA RECEIVED"
                    )


                    if "," in image_base64:

                        header, encoded = (
                            image_base64.split(
                                ",",
                                1
                            )
                        )

                    else:

                        encoded = image_base64


                    encoded = encoded.strip()


                    image_data = base64.b64decode(
                        encoded
                    )


                    filename = (
                        "emergency_photo_"
                        + uuid.uuid4().hex
                        + ".jpg"
                    )


                    emergency.image.save(
                        filename,
                        ContentFile(
                            image_data
                        ),
                        save=False
                    )


                    print(
                        "IMAGE SAVED:",
                        emergency.image.name
                    )


                except Exception as e:

                    print(
                        "IMAGE SAVE ERROR:",
                        repr(e)
                    )


            else:

                print(
                    "NO CAPTURED IMAGE"
                )


            # ============================================
            # SAVE CAPTURED VIDEO
            # ============================================

            if video_base64:

                try:

                    print(
                        "VIDEO DATA RECEIVED"
                    )


                    if "," in video_base64:

                        header, encoded = (
                            video_base64.split(
                                ",",
                                1
                            )
                        )

                    else:

                        encoded = video_base64


                    encoded = encoded.strip()


                    video_data = base64.b64decode(
                        encoded
                    )


                    filename = (
                        "emergency_video_"
                        + uuid.uuid4().hex
                        + ".webm"
                    )


                    emergency.video.save(
                        filename,
                        ContentFile(
                            video_data
                        ),
                        save=False
                    )


                    print(
                        "VIDEO SAVED:",
                        emergency.video.name
                    )


                except Exception as e:

                    print(
                        "VIDEO SAVE ERROR:",
                        repr(e)
                    )


            else:

                print(
                    "NO CAPTURED VIDEO"
                )


            # ============================================
            # SAVE DATABASE
            # ============================================

            emergency.save()


            print(
                "======================================"
            )

            print(
                "DATABASE SAVED:",
                emergency.id
            )

            print(
                "IMAGE DATABASE PATH:",
                emergency.image.name
                if emergency.image
                else "NO IMAGE"
            )

            print(
                "VIDEO DATABASE PATH:",
                emergency.video.name
                if emergency.video
                else "NO VIDEO"
            )

            print(
                "======================================"
            )


            messages.success(
                request,
                "Emergency report submitted successfully."
            )

            return redirect("home")


        else:

            print(
                "FORM ERRORS:",
                form.errors
            )

            messages.error(
                request,
                "Please correct the errors and submit again."
            )


    else:

        form = EmergencyReportForm()


    return render(
        request,
        "emergency_report.html",
        {
            "form": form
        }
    )

    
def emergency_report_success(request):
    
    return render(
        request,
        'emergency_report_success.html'
    )
    
@login_required
def emergency_admin(request):

    # Only staff/admin can access this page
    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to access this page."
        )

        return redirect("home")


    # Only pending reports
    reports = (
        EmergencyReport.objects
        .filter(status="PENDING")
        .select_related(
            "reporter",
            "reviewed_by"
        )
        .order_by("-created_at")
    )


    return render(
        request,
        "admin_emergency_report.html",
        {
            "reports": reports
        }
    )
    
@login_required
@login_required
def verify_emergency(request, report_id):

    if not request.user.is_staff:
        return redirect('home')

    emergency = get_object_or_404(
        EmergencyReport,
        id=report_id,
        status='PENDING'
    )

    if request.method == 'POST':

        emergency.status = 'CONFIRMED'

        emergency.reviewed_by = request.user

        emergency.reviewed_at = timezone.now()

        emergency.save()

        # Create Active Hazard
        hazard = HazardReport.objects.create(

            title='Emergency Incident',

            description=emergency.description,

            servity='High',

            user=emergency.reporter,

            # Copy emergency map location
            latitude=emergency.latitude,

            longitude=emergency.longitude,

        )

        return redirect('emergency_admin')

    return redirect('emergency_admin')



from django.utils import timezone
@login_required
@login_required
def reject_emergency(request, report_id):

    if not request.user.is_staff:
        return redirect('home')

    emergency = get_object_or_404(
        EmergencyReport,
        id=report_id
    )

    if request.method == 'POST':

        emergency.status = 'REJECTED'

        emergency.reviewed_by = request.user

        emergency.reviewed_at = timezone.now()

        emergency.save()

        return redirect('emergency_admin')

    return redirect('emergency_admin')
    
        