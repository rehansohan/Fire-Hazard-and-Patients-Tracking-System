import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from deepface import DeepFace


def verify_face(image1, image2):

    if not image1 or not image2:
        return {
            "verified": False,
            "distance": 1.5
        }

    # Check whether image files actually exist
    if not os.path.isfile(image1):
        return {
            "verified": False,
            "distance": 1.0
        }

    if not os.path.isfile(image2):
        return {
            "verified": False,
            "distance": 1.0
        }

    try:

        result = DeepFace.verify(
            img1_path=image1,
            img2_path=image2,
            model_name="Facenet512",
            detector_backend="skip",
            enforce_detection=False
        )

        distance = float(result["distance"])
        verified = bool(result["verified"])

        return {
            "verified": verified,
            "distance": distance
        }

    except Exception as e:

        return {
            "verified": False,
            "distance": 1.0
        }