from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    HazardReport,
    Hospital,
    Patient,
    MissingComplaint,
    Profile,
    PatientTransfer,
    PatientMatch,
    EmergencyReport,
    FireStation,
)


# ============================================================
# HAZARD REPORT
# ============================================================

@admin.register(HazardReport)
class HazardReportAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "servity",
        "status",
        "user",
        "created_at",
    )

    list_filter = (
        "status",
        "servity",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# PATIENT
# ============================================================

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "patient_id",
        "age",
        "gender",
        "condition",
        "hospital",
        "created_at",
    )

    list_filter = (
        "gender",
        "condition",
        "hospital",
        "created_at",
    )

    search_fields = (
        "name",
        "patient_id",
        "hospital__name",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# MISSING COMPLAINT
# ============================================================
# ============================================================
# MISSING COMPLAINT
# ============================================================

@admin.register(MissingComplaint)
class MissingComplaintAdmin(admin.ModelAdmin):

    list_display = (
        "missing_person_name",
        "missing_person_age",
        "missing_person_gender",
        "relationship",
        "contact_number",
        "status",
        "missing_date",
        "created_at",
    )

    list_filter = (
        "status",
        "missing_person_gender",
        "relationship",
        "blood_group",
        "missing_date",
        "created_at",
    )

    search_fields = (
        "missing_person_name",
        "contact_number",
        "last_seen_location",
        "identifying_marks",
        "user__username",
        "user__email",
        "hazard__title",
        "patient__name",
        "patient__patient_id",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (

        # ----------------------------------------------------
        # Reporter Information
        # ----------------------------------------------------
        (
            "👤 Reporter Information",
            {
                "fields": (
                    "user",
                    "relationship",
                    "contact_number",
                )
            },
        ),

        # ----------------------------------------------------
        # Victim Information
        # ----------------------------------------------------
        (
            "🚨 Missing Person Information",
            {
                "fields": (
                    "missing_person_name",
                    "missing_person_age",
                    "missing_person_gender",
                    "image",
                    "height",
                    "blood_group",
                    "identifying_marks",
                )
            },
        ),

        # ----------------------------------------------------
        # Missing Details
        # ----------------------------------------------------
        (
            "📍 Missing Details",
            {
                "fields": (
                    "missing_date",
                    "missing_time",
                    "last_seen_location",
                    "clothing_description",
                    "description",
                )
            },
        ),

        # ----------------------------------------------------
        # Incident / Hazard
        # ----------------------------------------------------
        (
            "🔥 Incident Information",
            {
                "fields": (
                    "hazard",
                )
            },
        ),

        # ----------------------------------------------------
        # Patient Information
        # ----------------------------------------------------
        (
            "🏥 Patient / Identification",
            {
                "fields": (
                    "patient",
                )
            },
        ),

        # ----------------------------------------------------
        # Complaint Status
        # ----------------------------------------------------
        (
            "📋 Complaint Status",
            {
                "fields": (
                    "status",
                    "created_at",
                )
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25
# ============================================================
# PROFILE
# ============================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "email",
        "phone",
        "date_of_birth",
        "gender",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
        "address",
    )

    list_filter = (
        "gender",
        "date_of_birth",
    )

    fieldsets = (
        (
            "👤 User Information",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "📞 Personal Information",
            {
                "fields": (
                    "phone",
                    "date_of_birth",
                    "gender",
                    "address",
                )
            },
        ),
        (
            "🖼️ Profile Image",
            {
                "fields": (
                    "profile_image",
                )
            },
        ),
    )

    ordering = (
        "user__username",
    )

    @admin.display(description="Email")
    def email(self, obj):
        return obj.user.email

# ============================================================
# PATIENT TRANSFER
# ============================================================

@admin.register(PatientTransfer)
class PatientTransferAdmin(admin.ModelAdmin):

    list_display = (
        "patient",
        "from_hospital",
        "to_hospital",
    )

    list_filter = (
        "from_hospital",
        "to_hospital",
    )

    search_fields = (
        "patient__name",
        "patient__patient_id",
        "from_hospital__name",
        "to_hospital__name",
    )


# ============================================================
# PATIENT MATCH
# ============================================================

@admin.register(PatientMatch)
class PatientMatchAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "patient",
    )

    search_fields = (
        "patient__name",
        "patient__patient_id",
    )

    ordering = (
        "-id",
    )


# ============================================================
# EMERGENCY REPORT
# ============================================================

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# HOSPITAL
# ============================================================

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "location",
        "phone",
        "capacity",
        "established_year",
    )

    search_fields = (
        "name",
        "location",
        "phone",
        "emergency_phone",
    )

    list_filter = (
        "location",
        "established_year",
    )

    fieldsets = (
        (
            "🏥 Basic Information",
            {
                "fields": (
                    "name",
                    "location",
                    "description",
                    "image",
                )
            },
        ),
        (
            "📞 Contact Information",
            {
                "fields": (
                    "phone",
                    "emergency_phone",
                    "official_website",
                )
            },
        ),
        (
            "📊 Hospital Statistics",
            {
                "fields": (
                    "capacity",
                    "established_year",
                )
            },
        ),
        (
            "📍 Geographic Location",
            {
                "fields": (
                    "latitude",
                    "longitude",
                )
            },
        ),
    )

    ordering = (
        "name",
    )


# ============================================================
# CUSTOM USER
# ============================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "gender",
    )

    search_fields = (
        "username",
        "email",
        "phone",
        "volunteer_id",
    )

    ordering = (
        "username",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "👤 Additional Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "date_of_birth",
                    "gender",
                    "volunteer_id",
                    "profile_image",
                )
            },
        ),
        (
            "🏥 Hospital Access",
            {
                "fields": (
                    "hospitals",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "👤 Additional Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "date_of_birth",
                    "gender",
                    "volunteer_id",
                    "profile_image",
                )
            },
        ),
        (
            "🏥 Hospital Access",
            {
                "fields": (
                    "hospitals",
                )
            },
        ),
    )


# ============================================================
# FIRE STATION
# ============================================================

@admin.register(FireStation)
class FireStationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "district",
        "upazila",
        "phone",
        "is_active",
    )

    list_filter = (
        "district",
        "upazila",
        "is_active",
    )

    search_fields = (
        "name",
        "district",
        "upazila",
        "phone",
        "address",
    )

    list_editable = (
        "is_active",
    )

    ordering = (
        "name",
    )