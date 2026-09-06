from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,HazardReport,Hospital,Patient,MissingComplaint,Profile,PatientTransfer,PatientMatch,EmergencyReport,FireStation

admin.site.register(HazardReport)
admin.site.register(Patient)
admin.site.register(MissingComplaint)
admin.site.register(Profile)
admin.site.register(PatientTransfer)
admin.site.register(PatientMatch)
admin.site.register(EmergencyReport)



@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "location",
        "phone",
        "capacity",
        "total_doctors",
        "total_nurses",
        "total_departments",
        "ambulances",
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
            "Basic Information",
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
            "Contact Information",
            {
                "fields": (
                    "phone",
                    "emergency_phone",
                    "official_website",
                )
            },
        ),
        (
            "Hospital Statistics",
            {
                "fields": (
                    "capacity",
                    "total_doctors",
                    "total_nurses",
                    "total_departments",
                    "ambulances",
                    "established_year",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "latitude",
                    "longitude",
                )
            },
        ),
    )

    ordering = ("name",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "phone",
                    "date_of_birth",
                    "gender",
                    "volunteer_id",
                    "profile_image",
                )
            }
        ),
        (
            "Hospital Access",
            {
                "fields": (
                    "hospitals",
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "phone",
                    "date_of_birth",
                    "gender",
                    "volunteer_id",
                    "profile_image",
                )
            }
        ),
        (
            "Hospital Access",
            {
                "fields": (
                    "hospitals",
                )
            }
        ),
    )
    
    
@admin.register(FireStation)
class FireStationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "district",
        "upazila",
        "phone",
        "image",
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