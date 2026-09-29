from deepface import DeepFace
import traceback
import os


def verify_face(image1, image2):

    if not image1 or not image2:
        return {
            "verified": False,
            "distance": 1.5
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

        distance = float(result["distance"])
        verified = bool(result["verified"])

        print("================================")
        print("Face Distance:", distance)
        print("DeepFace Verified:", verified)
        print("================================")

        return {
            "verified": verified,
            "distance": distance
        }

    except Exception as e:

        print("Face verification error:", e)
        traceback.print_exc()

        return {
            "verified": False,
            "distance": 1.0
        }