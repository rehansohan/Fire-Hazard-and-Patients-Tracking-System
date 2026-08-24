from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.conf import settings
import re

# Create your models here.
class User(AbstractUser):
    
    hospitals = models.ManyToManyField(
        'Hospital',
        blank=True,
        related_name='staff_members'
    )
    
    GENDER_CHOICES=(
        ('Male','male'),
        ('Female','female')
    )
    phone = models.CharField(
    max_length=20,
    blank=True,
    default=""
)
    date_of_birth = models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=100,choices=GENDER_CHOICES)
    volunteer_id = models.CharField(max_length=50,unique=True,null=True,blank=True)
    profile_image = models.ImageField(upload_to='profiles/',null=True,blank=True)
    def __str__(self):
        return self.username


    
    
class Hospital(models.Model):
    name=models.CharField(max_length=100)
    location =models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='hospitals/',
        null = True,
        blank = True
    )
    description = models.TextField(blank=True,default="")
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        default=""
    )
    established_year = models.IntegerField(
        null=True,
        blank= True
    )
    total_doctors = models.IntegerField(
        default=0
    )
    total_nurses = models.IntegerField(
        default=0
    )
    total_departments= models.IntegerField( default=0)
    ambulances=models.IntegerField(default=0)
    
    class Meta:
        permissions = [
            (
                "view_hospital_dashboard",
                "Can view hospital dashboard"
            ),
        ]

    def __str__(self):
        return self.name
    
    
class HazardReport(models.Model):
    SEVRITY_CHOICES=[
        ('Low','low'),
        ('Medimu','medium'),
        ('High','high')
    ]
    latitude=models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    
    hospitals = models.ManyToManyField(
    Hospital,
    blank=True,
    related_name='hazards'
)
    
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    servity = models.CharField(max_length=100,choices=SEVRITY_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
           ('resolved', 'Resolved')
            
        ],
        default='active',
    )
    def __str__(self):
        return f"{self.title}-{self.servity}"
    

class Patient(models.Model):
    
    is_identified = models.BooleanField(default=False)
    identified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='identified_patients'
        
        
    )
    
    STATUS_CHOICES=[
        ('admitted','Admitted'),
        ('transferred','Transferred'),
        ('released','Released'),
        ('deceased','Deceased')
    ]
    name = models.CharField(max_length=100,null=True,blank=True)
    patient_id = models.CharField(max_length=20, unique=True, blank=True,null=True)

    age = models.IntegerField(null=True,blank=True)
    GENDER_CHOICES = [
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,blank=True
)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='admitted',null=True,blank=True)
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    
    blood_group = models.CharField(
    max_length=3,
    choices=BLOOD_GROUP_CHOICES,
    blank=True,
    null=True
)
    
    condition = models.CharField(
        max_length=20,
        null=True,blank=True,
        choices=[
            ('stable', 'Stable'),
            ('critical', 'Critical')
        ]
        
    )
    
    identifying_marks = models.TextField(
            blank=True,
            default="",
            null=True
        )

    hospital = models.ForeignKey(
        'Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Better use ForeignKey instead of OneToOneField
    hazard = models.ForeignKey(
        'HazardReport',
        on_delete=models.CASCADE,
        related_name='patients',
        null=True,blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    
    height = models.DecimalField(
     max_digits=3,
    decimal_places=1,
    blank=True,
    null=True,
    help_text="Height in feet (e.g. 5.6)"
)
    
    clothing_description = models.TextField(
            blank=True,
            default="",
            null = True,
          
        )
    
    description = models.TextField(
            default="",
            null = True,
                    blank=True,
        )

    def save(self, *args, **kwargs):

        if not self.patient_id:
            hazard_id = self.hazard_id
            prefix = f"PAT-{hazard_id}-"
            last_num = 0

            for existing_patient_id in Patient.objects.filter(
                patient_id__startswith=prefix
            ).values_list('patient_id', flat=True):
                match = re.search(rf'^PAT-{hazard_id}-(\d+)$', existing_patient_id or '')
                if match:
                    last_num = max(last_num, int(match.group(1)))

            self.patient_id = f"{prefix}{last_num + 1}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} --> {self.name}"
    
    
class PatientTransfer(models.Model):
    ACTION_CHOICES=[
        ('transfer','Transfer'),
        ('release','Release'),
    ]
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='transfers'
    )
    from_hospital=models.ForeignKey(
        'Hospital',
        on_delete=models.SET_NULL,
        null = True,
        related_name='outgoing_transfers'
    )
    to_hospital = models.ForeignKey(
        'Hospital',
        on_delete=models.SET_NULL,
        null = True,
        blank=True,
        related_name='incoming_transfers'
    )
    action = models.CharField(
        max_length=20,
        choices = ACTION_CHOICES
    )
    
    notes = models.TextField(
        blank = True
    )
    
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null = True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"(self.patient.patient_id)"
    
    

from django.db import models
from django.conf import settings
import datetime


class MissingComplaint(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    RELATION_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Spouse', 'Spouse'),
        ('Relative', 'Relative'),
        ('Friend', 'Friend'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Searching', 'Searching'),
        ('Found', 'Found'),
        ('Closed', 'Closed'),
    ]

    # Login User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="missing_complaints",
        null=True,
        blank=True,
    )

   
    hazard = models.ForeignKey(
        'HazardReport',
        on_delete=models.CASCADE,
        related_name='missing_complaints',
        null=True,
        blank=True,
    )

    # If later victim is found
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.SET_NULL,
        related_name='missing_complaints',
        null=True,
        blank=True,
    )

    # Victim Information
    missing_person_name = models.CharField(
        max_length=100,
        default="",
        null = True,
        blank=True,
    )

    missing_person_age = models.PositiveIntegerField(
        default=0,
        null = True,
        blank=True,
    )

    missing_person_gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default="male",
        null = True,
        blank=True,
    )

    image = models.ImageField(
        upload_to='missing_people/',
        null=True,
        blank=True
    )

    height = models.DecimalField(
     max_digits=3,
    decimal_places=1,
    blank=True,
    null=True,
    help_text="Height in feet (e.g. 5.6)"
)

    BLOOD_GROUP_CHOICES = [
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
    ("O+", "O+"),
    ("O-", "O-"),
]

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True
    )

    identifying_marks = models.TextField(
        blank=True,
        default="",
        null = True,
       
    )

    # Missing Details
    missing_date = models.DateField(
        default=datetime.date.today,
        null = True,
        blank=True,
        
    )

    missing_time = models.TimeField(
        default=datetime.time(0, 0),
        null = True,
        blank=True,
    )

    last_seen_location = models.CharField(
        max_length=200,
        default="",
        null = True,
                blank=True,
    )

    clothing_description = models.TextField(
        blank=True,
        default="",
        null = True,
      
    )

    description = models.TextField(
        default="",
        null = True,
                blank=True,
    )

    # Reporter Information
    relationship = models.CharField(
        max_length=20,
        choices=RELATION_CHOICES,
        default="Other",
        null = True,
                blank=True,
    )

    contact_number = models.CharField(
        max_length=20,
        default="",
        null = True,
        blank=True,
    )

    # Complaint Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        null = True,
                blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.missing_person_name
    
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    phone = models.CharField(
    max_length=20,
    blank=True,
    default=""
)
    address = models.TextField()

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
    
    

class PatientMatch(models.Model):
    MATCH_STATUS = [
    ("Pending", "pending"),
    ("Confirmed", "Confirmed"),
    ("Rejected", "Rejected"),
]
    complaint = models.ForeignKey(
        MissingComplaint,
        on_delete=models.CASCADE,
        related_name="ai_matches"
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="ai_matches"
    )
    similarity_score = models.FloatField(default=0)
    face_verified = models.BooleanField(default=False)
    face_distance = models.FloatField(default=1.0)
    confirmed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null = True,
        blank=True
    )
    confirmed_at = models.DateTimeField(
        null = True,
        blank=True
    )
    
    match_status = models.CharField(
        max_length=20,
        choices=MATCH_STATUS,
        default="Pending"
    )
    
    name_similarity = models.FloatField(default=0)
    age_match=models.BooleanField(default=False)
    age_difference = models.IntegerField(default=0)
    gender_match= models.BooleanField(default=False)
    blood_group_match = models.BooleanField(default=False)
    height_match = models.BooleanField(default=False)
    height_difference = models.FloatField(default=0)
    
    created_at= models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-similarity_score"]

    constraints = [
        models.UniqueConstraint(
            fields=["patient", "complaint"],
            name="unique_patient_complaint_match"
        )
    ]
        
    def __str__(self):
        return f"{self.complaint} -> {self.patient}"
    
    
class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ('identification','Patient Identification'),
        ('status','Patient Status'),
        ('contidion','Patient Condition'),
        ('transfer','Patient Transfer'),
        ('release','Patient Release'),
        ('match','AI Match'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
        
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
        
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}-{self.title}"
    
    
class EmergencyReport(models.Model):
    STATUS_CHOICES=[
        ('PENDING','Pending'),
        ('CONFIRMED','Confirmed'),
        ('REJECTED','Rejected')
        
    ]
    reporter=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_reports'
        
    )
    description=models.TextField(
        null=True,blank=True
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    image = models.ImageField(
        upload_to='emergency_reports/images/',
        null=True,
        blank=True
    )

    video = models.FileField(
        upload_to='emergency_reports/videos/',
        null=True,
        blank=True
    )

    estimated_injured = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    contact_number = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    admin_note = models.TextField(
        blank=True,
        null=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_emergency_reports'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )