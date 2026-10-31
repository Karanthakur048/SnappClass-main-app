import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st


# # Database se saare students laane ke liye
from src.database.db import get_all_students


@st.cache_resource
# # Face Detector: image mein face kahan hai, ye detect karta hai.
# # Shape Predictor: face ke important points locate karta hai.
# # Face Recognition Model: face ko 128-dimensional embedding mein convert karta hai.
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    # # Ye facial landmarks detect karne wala model hai
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # # Ye actual face recognition model hai
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    # # Image mein faces detect kar rahe hain
    faces = detector(image_np, 2)

    encodings = []

    for face in faces:

        # # Face ke landmarks nikal rahe hain
        shape = sp(image_np, face)

        # # Face ko 128-number embedding mein convert kar rahe hain
        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        # # Descriptor ko NumPy array mein convert kar rahe hain
        encodings.append(np.array(face_descriptor))

    return encodings


@st.cache_resource
def get_trained_model():

    X = []
    Y = []

    # # Supabase se students ka data la rahe hain
    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:

        # # Database mein saved face embedding nikal rahe hain
        embedding = student.get("face_embedding")

        # # Embedding available hai ya nahi
        if embedding is not None:

            # # Training features
            X.append(np.array(embedding))

            # # Student ki ID
            Y.append(student.get("student_id"))

    # # Agar kisi student ka face embedding nahi mila
    if len(X) == 0:
        return None

    # # SVM classifier create kar rahe hain
    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:

        # # X = face embeddings
        # # Y = corresponding student IDs
        clf.fit(X, Y)

    except ValueError as e:

        st.error(f"Model training error: {e}")
        return None

    return {
        "clf": clf,
        "X": X,
        "Y": Y
    }


def train_classifier():

    # # Purana cached model clear kar rahe hain
    st.cache_resource.clear()

    # # Database ke latest face embeddings se model dobara train kar rahe hain
    model_data = get_trained_model()

    return bool(model_data)


def predict_attendance(class_image_np):

    # # Camera image se face embeddings nikal rahe hain
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    # # Trained SVM model load kar rahe hain
    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    clf = model_data["clf"]
    X_train = model_data["X"]
    Y_train = model_data["Y"]

    # # Database mein available student IDs
    all_students = list(set(Y_train))

    for encoding in encodings:

        # # Agar multiple students training mein hain,
        # # SVM prediction karega ki face kis student ka hai.
        if len(all_students) >= 2:

            predicted_id = clf.predict([encoding])[0]

        else:

            # # Sirf ek student hai toh wahi student hoga
            predicted_id = all_students[0]

        # # Predicted student ki saved face embedding find kar rahe hain
        student_index = Y_train.index(predicted_id)

        student_embedding = X_train[student_index]

        # # Camera se aaye face aur database face ke beech distance
        best_match_score = np.linalg.norm(
            student_embedding - encoding
        )

        # # Distance jitni kam hogi, face utna similar hoga
        resemblance_threshold = 0.5

        if best_match_score <= resemblance_threshold:

            # # Student ko recognized mark kar rahe hain
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)