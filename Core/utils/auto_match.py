from Core.models import MissingComplaint,PatientMatch
from.matching_engine import calculate_match

def run_ai_matching(patient):
    
    complaints = MissingComplaint.objects.filter(
        hazard=patient.hazard
    )
    
    for complaint in complaints:
        result = calculate_match(patient,complaint)
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
        