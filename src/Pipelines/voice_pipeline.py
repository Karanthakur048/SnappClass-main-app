# Resemblyzer se VoiceEncoder aur preprocess_wav import kar rahe hain
# VoiceEncoder -> voice ko numerical embedding mein convert karta hai
# preprocess_wav -> audio ko Resemblyzer ke liye prepare karta hai
from resemblyzer import VoiceEncoder, preprocess_wav

# NumPy numerical calculations aur arrays ke liye use hota hai
import numpy as np

# io.BytesIO audio bytes ko memory mein file-like object banane ke liye use hota hai
import io

# Librosa audio ko read aur process karne ke liye use hota hai
import librosa

# Streamlit UI aur caching ke liye use ho raha hai
import streamlit as st


# ---------------------------------------------------------
# VOICE ENCODER LOAD KARNE KA FUNCTION
# ---------------------------------------------------------

# @st.cache_resource ka purpose:
# VoiceEncoder model ko baar-baar load hone se bachana.
# Pehli baar model load hoga aur Streamlit usse cache mein rakhega.
# Next time same model ko dobara load nahi karna padega.
@st.cache_resource
def load_voice_encoder():

    # Resemblyzer ka VoiceEncoder model create/load kar rahe hain
    return VoiceEncoder()


# ---------------------------------------------------------
# VOICE KO EMBEDDING MEIN CONVERT KARNE KA FUNCTION
# ---------------------------------------------------------

def get_voice_embedding(audio_bytes):

    # Voice processing mein agar koi error aaye,
    # to application crash hone ke bajaye error handle hoga.
    try:

        # Resemblyzer ka voice encoder model load kar rahe hain.
        # Agar model pehle load ho chuka hai to cached model milega.
        encoder = load_voice_encoder()


        # audio_bytes = user ki recorded voice ka raw audio data.
        #
        # io.BytesIO(audio_bytes):
        # Raw audio bytes ko memory mein ek file-like object bana raha hai,
        # taaki librosa is audio ko read kar sake.
        #
        # sr=16000:
        # Audio ko 16,000 Hz sampling rate par load kar rahe hain.
        # Matlab 1 second audio mein 16,000 samples honge.
        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )


        # Raw audio ko Resemblyzer ke liye preprocess/prepare kar rahe hain.
        # Isse audio model ke expected format mein aa jata hai.
        wav = preprocess_wav(audio)

        embedding = encoder.embed_utterance(wav)


        # Resemblyzer embedding NumPy array hoti hai.
        # .tolist() usse normal Python list mein convert karta hai,
        # jo database mein store karna easier hota hai.
        return embedding.tolist()


    # Agar upar ke kisi step mein error aa jaye
    except Exception as e:

        # Actual error ko screen par show karenge,
        # taaki debugging easy ho.
        st.error(f"Voice recognition error: {e}")

        # Voice embedding create nahi hui,
        # isliye None return kar rahe hain.
        return None



# ---------------------------------------------------------
# SPEAKER IDENTIFICATION FUNCTION
# ---------------------------------------------------------

def identify_speaker(new_embedding, candidate_dict, threshold=0.65):

    if new_embedding is None or not candidate_dict:
        return None


    # Abhi tak koi student best match nahi mila,
    # isliye best student ID initially None hai.
    best_sid = None


    # Similarity score ko -1 se start kar rahe hain.
    # Cosine similarity generally -1 se 1 ke beech hoti hai.
    # Isliye pehla actual score isse greater hoga.
    best_score = -1.0

    # candidate_dict ke andar har student ko one-by-one check karenge.
    #
    # Example:
    #
    # ST001 -> Student 1 ki voice embedding
    # ST002 -> Student 2 ki voice embedding
    # ST003 -> Student 3 ki voice embedding
    #
    # sid = Student ID
    # stored_embedding = database mein stored voice embedding
    for sid, stored_embedding in candidate_dict.items():


        # Agar is student ki voice embedding available hai,
        # tabhi usko compare karenge.
        if stored_embedding is not None:

            new_emb = np.array(new_embedding)
            stored_emb = np.array(stored_embedding)
            similarity = np.dot(new_emb, stored_emb) / (
                np.linalg.norm(new_emb) *
                np.linalg.norm(stored_emb)
            )

            if similarity > best_score:

                # Highest similarity score save kar rahe hain.
                best_score = similarity

                # Us highest score wale student ki ID save kar rahe hain.
                best_sid = sid


    # Ab check karenge ki best match threshold ko cross karta hai ya nahi.
    #
    # Example:
    # best_score = 0.87
    # threshold = 0.65
    #
    # 0.87 >= 0.65
    # YES -> Student identified
    if best_score >= threshold:

        # Student ID aur similarity score return karenge.
        return best_sid, best_score


    # Agar best score threshold se bhi kam hai,
    # to hum voice ko kisi student se match nahi maanenge.
    #
    # Example:
    # best_score = 0.42
    # threshold = 0.65
    #
    # 0.42 < 0.65
    # -> No reliable match
    return None,best_score



def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        segments = librosa.effects.split(
            audio,
            top_db=30
        )

        identified_results = {}

        for start, end in segments:

            if (end - start) < sr * 0.5:
                continue

            segment_audio = audio[start:end]

            wav = preprocess_wav(segment_audio)

            embedding = encoder.embed_utterance(wav)

            sid, score = identify_speaker(
                embedding,
                candidates_dict,
                threshold
            )

            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results

    except Exception as e:
        st.error('Bulk process error')