from django.contrib import admin
from .models import User,HazardReport,Hospital,Patient,MissingComplaint,Profile,PatientTransfer,PatientMatch

admin.site.register(User)
admin.site.register(HazardReport)
admin.site.register(Hospital)
admin.site.register(Patient)
admin.site.register(MissingComplaint)
admin.site.register(Profile)
admin.site.register(PatientTransfer)
admin.site.register(PatientMatch)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


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