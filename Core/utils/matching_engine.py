from .face_ai import verify_face
from .text_ai import name_similarity
from Core.models import Patient, MissingComplaint, PatientMatch
from .face_ai import verify_face
from .text_ai import name_similarity


def _normalized_text(value):
    return str(value or "").strip().lower()


def calculate_match(patient, complaint):

    # ---------- Gender Filter ----------
    patient_gender = _normalized_text(patient.gender)
    complaint_gender = _normalized_text(complaint.missing_person_gender)

    if not patient_gender or not complaint_gender or patient_gender != complaint_gender:
        return {
            "score": 0,

            "name_similarity": 0,

            "gender_match": False,

            "age_match": False,
            "age_difference": 0,

            "blood_group_match": False,

            "height_match": False,
            "height_difference": 0,

            "face_verified": False,
            "face_distance": 1.0,
        }

    score = 0

    # ---------- Name Matching (30%) ----------
    name = name_similarity(
    _normalized_text(patient.name),
    _normalized_text(complaint.missing_person_name)
)

    score += name * 0.30

    # ---------- Age (15%) ----------
    age_difference = abs(
    int(patient.age or 0)
    -
    int(complaint.missing_person_age or 0)
)

    age_match = age_difference <= 2

    if age_match:
        score += 15

    # ---------- Gender (15%) ----------
    gender_match = (
    patient_gender
    ==
    complaint_gender
)

    if gender_match:
        score += 15

    # ---------- Blood Group (10%) ----------
    blood_group_match = (
    str(patient.blood_group or "").strip().upper()
    ==
    str(complaint.blood_group or "").strip().upper()
)

    if blood_group_match:
        score += 10

    # ---------- Height (10%) ----------
    height_match = False
    height_difference = 0

    try:
        height_difference = abs(
    float(patient.height or 0)
    -
    float(complaint.height or 0)
)

        if height_difference <= 0.1:
            height_match = True
            score += 10

    except (ValueError, TypeError, AttributeError):
        pass

    # ---------- Face ----------
# ---------- Face ----------
    face = {
        "verified": False,
        "distance": 1.0
    }

    try:

        if patient.image and complaint.image:

            face = verify_face(
                patient.image.path,
                complaint.image.path
            )

            if face["verified"]:
                score += 20

    except Exception:
        pass



    score = min(score, 100)

    return {

        "score": round(score, 2),

        "name_similarity": round(name, 2),

        "gender_match": gender_match,

        "age_match": age_match,
        "age_difference": age_difference,

        "blood_group_match": blood_group_match,

        "height_match": height_match,
        "height_difference": round(height_difference, 2),

        "face_verified": face["verified"],
        "face_distance": round(face["distance"], 3),

    }
    

def create_patient_match(patient, complaint):
    
    result = calculate_match(
        patient,
        complaint
    )

    PatientMatch.objects.update_or_create(
        patient=patient,
        complaint=complaint,
        defaults={
            "similarity_score": result["score"],
            "name_similarity": result["name_similarity"],

            "gender_match": result["gender_match"],

            "age_match": result["age_match"],
            "age_difference": result["age_difference"],

            "blood_group_match": result["blood_group_match"],

            "height_match": result["height_match"],
            "height_difference": result["height_difference"],

            "face_verified": result["face_verified"],
            "face_distance": result["face_distance"],
        }
    )


def run_ai_matching(patient):

    complaints = MissingComplaint.objects.filter(
        hazard=patient.hazard
    )

    for complaint in complaints:

        create_patient_match(
            patient,
            complaint
        )


def run_ai_matching_for_complaint(complaint):

    patients = Patient.objects.filter(
        hazard=complaint.hazard
    )

    for patient in patients:

        create_patient_match(
            patient,
            complaint
        )