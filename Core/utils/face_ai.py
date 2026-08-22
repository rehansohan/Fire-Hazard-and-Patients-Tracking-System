from deepface import DeepFace
import traceback
import os

FACE_THRESHOLD = 0.35


def verify_face(image1, image2):

    if not image1 or not image2:
        return {
            "verified": False,
            "distance": 1.0
        }

    # Check whether image files actually exist
    if not os.path.isfile(image1):
        print("Image 1 not found:", image1)

        return {
            "verified": False,
            "distance": 1.0
        }

    if not os.path.isfile(image2):
        print("Image 2 not found:", image2)

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

        verified = result["distance"] <= FACE_THRESHOLD

        return {
            "verified": verified,
            "distance": result["distance"]
        }

    except Exception:

        traceback.print_exc()

        return {
            "verified": False,
            "distance": 1.0
        }