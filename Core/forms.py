from django import forms 
from.models import HazardReport,Hospital,Patient,MissingComplaint,Profile,PatientTransfer,User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class HazardReportForm(forms.ModelForm):
    class Meta:
        model = HazardReport
        fields=['title','description','servity']
        
        widgets ={
            'title':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Enter hazard title'
            }),
            'description':forms.Textarea(attrs={
                'class':'form-control',
                'placeholder':'Describe the hazard',
                'rows':4
            }),
            'servity':forms.Select(attrs={
                'class':'form-select'
            })
        }
        
class HospitalForm(forms.ModelForm):
    class Meta:
        model= Hospital
        fields = ['name','location','phone','capacity','image','description','emergency_phone','established_year','total_doctors','total_nurses','total_departments','ambulances']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hospital name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, district, or area'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bed capacity'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class':'form-control'
        }),
            'descripiton': forms.Textarea(attrs={
                'class':'form-control','rows':4,
                'placeholder':'hospital Description',
                
            }),
            
            'emergency_phone':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder': 'emergency_phone'
            }),
            
            
              'total_doctors': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Doctors'
            }),

            'total_nurses': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Nurses'
            }),

            'total_departments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Departments'
            }),

            'ambulances': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of Ambulances'
            }),
            
        }
        



class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient

        fields = [
            "name",
            "age",
            "gender",
            "blood_group",
            "height",
            "condition",
            "identifying_marks",
            "clothing_description",
            "description",
            "hospital",
            "hazard",
            "status",
            "image",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter patient name"
            }),

            "age": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "blood_group": forms.Select(attrs={
                "class": "form-select"
            }),

            "height": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.1",
                "placeholder": "Example: 5.6"
            }),

            "condition": forms.Select(attrs={
                "class": "form-select"
            }),

            "status": forms.Select(attrs={
                "class": "form-select"
            }),

            "hospital": forms.Select(attrs={
                "class": "form-select"
            }),

            "hazard": forms.Select(attrs={
                "class": "form-select"
            }),

            "identifying_marks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Any identifying marks"
            }),

            "clothing_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Patient clothing description"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Additional information"
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
        
class PatientTransferForm(forms.ModelForm):
    class Meta:
        model = PatientTransfer
        fields=[
            'to_hospital',
            'action',
            'notes'
        ]
        widgets ={
            'to_hospital':forms.Select(
                attrs={
                    'class':'form-Select'
                }
            ),
            'action':forms.Select(
                attrs={
                    'class':'form-select'
                }
            ),
            'notes':forms.Textarea(
                attrs={
                    'class':'form-control',
                    'rows':3
                }
            )
        }
        
        
class MissingComplaintForm(forms.ModelForm):
    
    class Meta:
        model = MissingComplaint

        exclude = [
            "user",
            "status",
            "created_at",
        ]

        widgets = {
            "missing_date": forms.DateInput(attrs={"type": "date"}),
            "missing_time": forms.TimeInput(attrs={"type": "time"}),
        }
        
class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = User
        fields =[
            'username',
            'email',
            'password1',
            'password2',
            'phone',
            'address'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # apply consistent Bootstrap classes to all fields
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            classes = (existing + ' form-control').strip()
            field.widget.attrs.update({'class': classes})
        # make address textarea a bit shorter
        if 'address' in self.fields:
            self.fields['address'].widget.attrs.update({'rows': 3})


class TransferPatientForm(forms.Form):
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='New hospital'
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Note (optional)'
    )
    
    
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            "profile_image",
            "phone",
            "address",
        ]

        widgets = {

            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Phone Number"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter Address"
                }
            ),
        }

        

        