import streamlit as st
import re
import random
import pandas as pd
import numpy as np
import csv
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from difflib import get_close_matches
import warnings
import requests
import json
import base64
import time
import sqlite3
import hashlib

# --- DATABASE SETUP (डेटाबेस सेटअप) ---
def init_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # यदि 'users' तालिका मौजूद नहीं है तो बनाएँ
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- PASSWORD HASHING (पासवर्ड हैशिंग) ---
def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password_hash, provided_password):
    """Verifies a provided password against a stored hash."""
    return stored_password_hash == hashlib.sha256(provided_password.encode()).hexdigest()

# --- USER MANAGEMENT FUNCTIONS (उपयोगकर्ता प्रबंधन फ़ंक्शन) ---
def add_user(username, password):
    """Adds a new user to the database."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    """Verifies user credentials against the database."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and verify_password(result[0], password):
        return True
    return False

# Call init_db at the start of the app (ऐप की शुरुआत में init_db को कॉल करें)
init_db()


# Suppress deprecation warnings for scikit-learn
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Supported languages
LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Japanese (日本語)": "ja",
    "Russian (русский)": "ru",
    "Arabic (العربية)": "ar",
    "Chinese (中文)": "zh",
    "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Marathi (मराठी)": "mr",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
}

# Translations for UI text with added login/signup fields
UI_TEXT = {
    "en": {
        "title": "HealthCare Chatbot",
        "intro": "Hello! I am a chatbot designed to help you with preliminary symptom analysis. Please answer a few questions so I can understand your condition better.",
        "name_label": "What is your name?",
        "age_label": "Please enter your age:",
        "gender_label": "What is your gender?",
        "gender_options": ["Male", "Female", "Other"],
        "symptoms_label": "Describe your symptoms (any language):",
        "submit_button": "Submit",
        "warning_fill_fields": "Please enter your name and symptoms to continue.",
        "thinking": "Thinking...",
        "detected_symptoms": "✅ Detected symptoms: {}",
        "error_no_symptoms": "❌ Sorry, I could not detect valid symptoms. Please try again with more details.",
        "guided_questions_header": "🤔 Guided Questions",
        "guided_info": "Based on your initial symptoms, you may have **{}** (Confidence: {}%).",
        "guided_prompt": "To get a more accurate diagnosis, please answer a few more questions related to this condition.",
        "guided_symptom_prompt": "Do you also have **{}**?",
        "guided_button": "Get Final Prediction",
        "no_more_questions": "No further questions to ask. Click below for your final diagnosis.",
        "result_header": "✨ Diagnosis Result",
        "diagnosis_sub": "🩺 Based on your answers, you may have **{}**",
        "confidence_label": "Confidence Level",
        "about_sub": "📖 About",
        "precautions_sub": "🛡️ Suggested Precautions",
        "no_description": "No description available.",
        "start_over": "Start Over",
        "thank_you": "Thank you for using the chatbot. Wishing you good health, **{}**!",
        "login_header": "Login",
        "username_label": "Username",
        "password_label": "Password",
        "login_button": "Login",
        "login_error": "Invalid username or password. Please try again.",
        "logout_button": "Logout",
        "play_audio": "🔊 Play Diagnosis Audio",
        "signup_header": "Sign Up",
        "signup_button": "Sign Up",
        "signup_success": "Account created successfully! Please log in.",
        "signup_error_exists": "This username already exists. Please choose another.",
        "signup_error_fields": "Please enter both a username and password.",
        "nav_to_signup": "Don't have an account? Sign Up",
        "nav_to_login": "Already have an account? Login",
    },
    "hi": {
        "title": "हेल्थकेयर चैटबॉट",
        "intro": "नमस्ते! मैं एक चैटबॉट हूँ जो आपको प्रारंभिक लक्षण विश्लेषण में मदद करने के लिए बनाया गया है। कृपया कुछ प्रश्नों के उत्तर दें ताकि मैं आपकी स्थिति को बेहतर ढंग से समझ सकूं।",
        "name_label": "आपका नाम क्या है?",
        "age_label": "कृपया अपनी उम्र दर्ज करें:",
        "gender_label": "आपका लिंग क्या है?",
        "gender_options": ["पुरुष", "महिला", "अन्य"],
        "symptoms_label": "अपने लक्षणों का वर्णन करें (किसी भी भाषा में):",
        "submit_button": "जमा करें",
        "warning_fill_fields": "जारी रखने के लिए कृपया अपना नाम और लक्षण दर्ज करें।",
        "thinking": "सोच रहा है...",
        "detected_symptoms": "✅ पहचाने गए लक्षण: {}",
        "error_no_symptoms": "❌ क्षमा करें, मैं वैध लक्षणों का पता नहीं लगा सका। कृपया अधिक विवरण के साथ पुनः प्रयास करें।",
        "guided_questions_header": "🤔 निर्देशित प्रश्न",
        "guided_info": "आपके प्रारंभिक लक्षणों के आधार पर, आपको **{}** हो सकता है (विश्वास: {}%)।",
        "guided_prompt": "अधिक सटीक निदान प्राप्त करने के लिए, कृपया इस स्थिति से संबंधित कुछ और प्रश्नों के उत्तर दें।",
        "guided_symptom_prompt": "क्या आपको **{}** भी है?",
        "guided_button": "अंतिम निदान प्राप्त करें",
        "no_more_questions": "पूछने के लिए और कोई प्रश्न नहीं हैं। अपने अंतिम निदान के लिए नीचे क्लिक करें।",
        "result_header": "✨ निदान परिणाम",
        "diagnosis_sub": "🩺 आपके उत्तरों के आधार पर, आपको **{}** हो सकता है",
        "confidence_label": "विश्वास स्तर",
        "about_sub": "📖 के बारे में",
        "precautions_sub": "🛡️ सुझाए गए सावधानियां",
        "no_description": "कोई विवरण उपलब्ध नहीं है।",
        "start_over": "शुरू करें",
        "thank_you": "चैटबॉट का उपयोग करने के लिए धन्यवाद। आपके अच्छे स्वास्थ्य की कामना करता हूँ, **{}**!",
        "login_header": "लॉगिन",
        "username_label": "उपयोगकर्ता नाम",
        "password_label": "पासवर्ड",
        "login_button": "लॉगिन",
        "login_error": "गलत उपयोगकर्ता नाम या पासवर्ड। कृपया पुनः प्रयास करें।",
        "logout_button": "लॉगआउट",
        "play_audio": "🔊 निदान सुनें",
        "signup_header": "साइन अप करें",
        "signup_button": "साइन अप करें",
        "signup_success": "खाता सफलतापूर्वक बनाया गया! कृपया लॉगिन करें।",
        "signup_error_exists": "यह उपयोगकर्ता नाम पहले से मौजूद है। कृपया दूसरा चुनें।",
        "signup_error_fields": "कृपया उपयोगकर्ता नाम और पासवर्ड दोनों दर्ज करें।",
        "nav_to_signup": "खाता नहीं है? साइन अप करें",
        "nav_to_login": "पहले से ही खाता है? लॉगिन करें",
    },
    # Other language translations remain the same
}

# Supported TTS voices
TTS_VOICES = {
    "en": "Kore", "hi": "Kore", "es": "Kore", "fr": "Kore", "de": "Kore", "ja": "Kore",
    "ru": "Kore", "ar": "Kore", "zh": "Kore", "bn": "Kore", "gu": "Kore", "kn": "Kore",
    "ml": "Kore", "mr": "Kore", "or": "Kore", "pa": "Kore", "ta": "Kore", "te": "Kore"
}

# ------------------ Global Dictionaries & Data Loading (Cached for Performance) ------------------
@st.cache_data
def load_data():
    """Loads and preprocesses the training and testing data."""
    try:
        training = pd.read_csv('Data/Training.csv')
        testing = pd.read_csv('Data/Testing.csv')
        training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
        testing.columns = testing.columns.str.replace(r"\.\d+$", "", regex=True)
        training = training.loc[:, ~training.columns.duplicated()]
        testing = testing.loc[:, ~testing.columns.duplicated()]
        return training, testing
    except FileNotFoundError:
        st.error("Error: CSV files not found. Please make sure 'Training.csv' and 'Testing.csv' are in the 'Data' directory.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        st.stop()

@st.cache_data
def load_dictionaries():
    """Loads all supplementary data dictionaries."""
    severity_dict = {}
    description_list = {}
    precaution_dict = {}
    try:
        with open('MasterData/symptom_Description.csv', encoding="utf-8") as csv_file:
            for row in csv.reader(csv_file):
                if len(row) > 1:
                    description_list[row[0]] = row[1]
    except FileNotFoundError:
        st.warning("Warning: symptom_Description.csv not found.")
    try:
        with open('MasterData/Symptom_severity.csv', encoding="utf-8") as csv_file:
            for row in csv.reader(csv_file):
                if len(row) > 1:
                    try:
                        severity_dict[row[0]] = int(row[1])
                    except ValueError:
                        pass
    except FileNotFoundError:
        st.warning("Warning: Symptom_severity.csv not found.")
    try:
        with open('MasterData/symptom_precaution.csv', encoding="utf-8") as csv_file:
            for row in csv.reader(csv_file):
                if len(row) > 4:
                    precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]
    except FileNotFoundError:
        st.warning("Warning: symptom_precaution.csv not found.")
    return severity_dict, description_list, precaution_dict

training, testing = load_data()
severityDictionary, description_list, precautionDictionary = load_dictionaries()
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)
x_train, _, y_train, _ = train_test_split(x, y, test_size=0.33, random_state=42)

@st.cache_resource
def train_model(_x_train, _y_train):
    """Trains the Random Forest model."""
    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(_x_train, _y_train)
    return model

model = train_model(x_train, y_train)
symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}

# ------------------ Symptom Synonyms & Translation ------------------
symptom_synonyms = {
    "stomach ache": "stomach_pain", "belly pain": "stomach_pain", "tummy pain": "stomach_pain",
    "abdominal pain": "stomach_pain", "belly ache": "stomach_pain", "gastric pain": "stomach_pain",
    "body ache": "muscle_pain", "muscle ache": "muscle_pain", "head ache": "headache",
    "head pain": "headache", "migraine": "headache", "chest pain": "chest_pain",
    "feaver": "fever", "loose motion": "diarrhea", "motions": "diarrhea", "khansi": "cough",
    "throat pain": "sore_throat", "runny nose": "chills", "sneezing": "chills",
    "shortness of breath": "breathlessness", "skin rash": "skin_rash", "itchy": "itching",
    "tiredness": "fatigue", "vomiting": "vomit", "nausea": "nausea", "dizzy": "dizziness",
    "sad": "depression", "anxiety": "anxiety",
}

def call_gemini_api(prompt, target_lang="en"):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {"translated_text": {"type": "STRING"}}
            }
        },
    }
    apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={apiKey}"
    try:
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        json_text = result['candidates'][0]['content']['parts'][0]['text']
        parsed_json = json.loads(json_text)
        return parsed_json.get('translated_text', '')
    except requests.exceptions.RequestException as e:
        st.error(f"Translation network error: {e}")
        return ""
    except (KeyError, json.JSONDecodeError) as e:
        st.error(f"Translation parsing error: {e}")
        return ""

@st.cache_data(show_spinner=False)
def translate_to_english(text):
    if not text: return ""
    prompt = f"Translate the following text to English and provide only the translated text in a JSON format with the key 'translated_text': '{text}'"
    return call_gemini_api(prompt)

@st.cache_data(show_spinner=False)
def translate_from_english(text, target_lang):
    if not text or target_lang == "en": return text
    prompt = f"Translate the following text to {target_lang} and provide only the translated text in a JSON format with the key 'translated_text': '{text}'"
    return call_gemini_api(prompt, target_lang)

def extract_symptoms(user_input, all_symptoms):
    extracted = []
    text = user_input.lower().replace("-", " ")
    for phrase, mapped in symptom_synonyms.items():
        if phrase in text:
            extracted.append(mapped)
    for symptom in all_symptoms:
        if symptom.replace("_", " ") in text:
            extracted.append(symptom)
    words = re.findall(r"\w+", text)
    for word in words:
        close = get_close_matches(word, [s.replace("_", " ") for s in all_symptoms], n=1, cutoff=0.8)
        if close:
            for sym in all_symptoms:
                if sym.replace("_", " ") == close[0]:
                    extracted.append(sym)
    return list(set(extracted))

def predict_disease(symptoms_list):
    input_vector = np.zeros(len(symptoms_dict))
    for symptom in symptoms_list:
        if symptom in symptoms_dict:
            input_vector[symptoms_dict[symptom]] = 1
    input_df = pd.DataFrame([input_vector], columns=symptoms_dict.keys())
    pred_proba = model.predict_proba(input_df)[0]
    pred_class = np.argmax(pred_proba)
    disease = le.inverse_transform([pred_class])[0]
    confidence = round(pred_proba[pred_class] * 100, 2)
    return disease, confidence, pred_proba

def call_tts_api(text, lang_code):
    voice_name = TTS_VOICES.get(lang_code, "Kore")
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
            },
        },
    }
    apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={apiKey}"
    response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    response.raise_for_status()
    result = response.json()
    audio_data = result['candidates'][0]['content']['parts'][0]['inlineData']['data']
    return base64.b64decode(audio_data)

def generate_tts_with_backoff(api_call_function):
    max_retries = 5
    delay = 1.0
    for i in range(max_retries):
        try:
            return api_call_function()
        except Exception as e:
            if "429" in str(e):
                st.warning(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
            else:
                st.error(f"An unexpected TTS error occurred: {e}")
                return None
    st.error("Failed to get TTS response after several retries.")
    return None

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="HealthCare Chatbot", page_icon="🩺")

# Initialize session state variables
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "home"
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
if "name" not in st.session_state: st.session_state.name = ""
if "symptoms_list" not in st.session_state: st.session_state.symptoms_list = []
if "initial_prediction" not in st.session_state: st.session_state.initial_prediction = None
if "final_prediction" not in st.session_state: st.session_state.final_prediction = None
if "guided_symptoms" not in st.session_state: st.session_state.guided_symptoms = []
if "lang" not in st.session_state: st.session_state.lang = "en"

# Language selection
st.sidebar.title("Language")
selected_lang_name = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
st.session_state.lang = LANGUAGES[selected_lang_name]

lang_texts = UI_TEXT.get(st.session_state.lang, UI_TEXT["en"])

# --- LOGIN/SIGNUP FLOW ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{lang_texts['title']}</h1>", unsafe_allow_html=True)

    if st.session_state.auth_page == "login":
        st.markdown(f"<h3 style='text-align: center;'>{lang_texts['login_header']}</h3>", unsafe_allow_html=True)
        with st.form(key="login_form"):
            username = st.text_input(lang_texts["username_label"])
            password = st.text_input(lang_texts["password_label"], type="password")
            login_button = st.form_submit_button(lang_texts["login_button"])

            if login_button:
                if verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.name = username
                    st.rerun()
                else:
                    st.error(lang_texts["login_error"])
        
        if st.button(lang_texts["nav_to_signup"]):
            st.session_state.auth_page = "signup"
            st.rerun()

    elif st.session_state.auth_page == "signup":
        st.markdown(f"<h3 style='text-align: center;'>{lang_texts['signup_header']}</h3>", unsafe_allow_html=True)
        with st.form(key="signup_form"):
            new_username = st.text_input(lang_texts["username_label"])
            new_password = st.text_input(lang_texts["password_label"], type="password")
            signup_button = st.form_submit_button(lang_texts["signup_button"])

            if signup_button:
                if not new_username or not new_password:
                    st.warning(lang_texts["signup_error_fields"])
                else:
                    if add_user(new_username, new_password):
                        st.success(lang_texts["signup_success"])
                        st.session_state.auth_page = "login"
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(lang_texts["signup_error_exists"])

        if st.button(lang_texts["nav_to_login"]):
            st.session_state.auth_page = "login"
            st.rerun()
else:
    # --- MAIN CHATBOT UI ---
    st.title(lang_texts["title"])
    st.markdown(lang_texts["intro"])
    
    if st.sidebar.button(lang_texts["logout_button"]):
        st.session_state.clear()
        st.rerun()

    if st.session_state.page == "home":
        with st.form(key="user_info_form"):
            st.session_state.name = st.text_input(lang_texts["name_label"], value=st.session_state.get('name', ''))
            age = st.text_input(lang_texts["age_label"])
            gender = st.selectbox(lang_texts["gender_label"], lang_texts["gender_options"])
            symptoms_input_raw = st.text_area(lang_texts["symptoms_label"], height=100)
            submit_button = st.form_submit_button(lang_texts["submit_button"])

        if submit_button:
            if not st.session_state.name or not symptoms_input_raw:
                st.warning(lang_texts["warning_fill_fields"])
            else:
                with st.spinner(lang_texts["thinking"]):
                    symptoms_input_en = translate_to_english(symptoms_input_raw)
                    detected_symptoms = extract_symptoms(symptoms_input_en, cols)
                    if not detected_symptoms:
                        st.error(lang_texts["error_no_symptoms"])
                    else:
                        st.session_state.symptoms_list = detected_symptoms
                        st.success(lang_texts["detected_symptoms"].format(', '.join(st.session_state.symptoms_list).replace('_', ' ')))
                        initial_disease, confidence, _ = predict_disease(st.session_state.symptoms_list)
                        st.session_state.initial_prediction = {"disease": initial_disease, "confidence": confidence}
                        disease_symptoms = list(training[training['prognosis'] == initial_disease].iloc[0][:-1].index[training[training['prognosis'] == initial_disease].iloc[0][:-1] == 1])
                        st.session_state.guided_symptoms = [sym for sym in disease_symptoms if sym not in st.session_state.symptoms_list][:8]
                        st.session_state.page = "guided_questions"
                        st.rerun()

    elif st.session_state.page == "guided_questions":
        st.header(lang_texts["guided_questions_header"])
        initial_pred = st.session_state.initial_prediction
        st.info(lang_texts["guided_info"].format(initial_pred['disease'], initial_pred['confidence']))
        st.write(lang_texts["guided_prompt"])

        if st.session_state.guided_symptoms:
            with st.form(key="guided_questions_form"):
                new_symptoms = []
                for symptom in st.session_state.guided_symptoms:
                    if st.checkbox(lang_texts["guided_symptom_prompt"].format(symptom.replace('_', ' ')), key=symptom):
                        new_symptoms.append(symptom)
                submit_guided = st.form_submit_button(lang_texts["guided_button"])

            if submit_guided:
                with st.spinner(lang_texts["thinking"]):
                    st.session_state.symptoms_list.extend(new_symptoms)
                    final_disease, final_confidence, _ = predict_disease(st.session_state.symptoms_list)
                    st.session_state.final_prediction = {"disease": final_disease, "confidence": final_confidence}
                    st.session_state.page = "result"
                    st.rerun()
        else:
            st.info(lang_texts["no_more_questions"])
            if st.button(lang_texts["guided_button"]):
                final_disease, final_confidence, _ = predict_disease(st.session_state.symptoms_list)
                st.session_state.final_prediction = {"disease": final_disease, "confidence": final_confidence}
                st.session_state.page = "result"
                st.rerun()

    elif st.session_state.page == "result":
        st.header(lang_texts["result_header"])
        final_pred = st.session_state.final_prediction
        disease = final_pred["disease"]
        confidence = final_pred["confidence"]
        
        translated_disease = translate_from_english(disease, st.session_state.lang)
        st.subheader(lang_texts["diagnosis_sub"].format(translated_disease))
        st.metric(label=lang_texts["confidence_label"], value=f"{confidence}%")
        st.markdown("---")

        st.subheader(lang_texts["about_sub"])
        description = description_list.get(disease, lang_texts["no_description"])
        translated_description = translate_from_english(description, st.session_state.lang)
        st.write(translated_description)

        if disease in precautionDictionary:
            st.subheader(lang_texts["precautions_sub"])
            precautions = precautionDictionary[disease]
            for i, prec in enumerate(precautions, 1):
                translated_prec = translate_from_english(prec, st.session_state.lang)
                st.write(f"{i}. {translated_prec}")
        
        st.markdown("---")
        if st.button(lang_texts["play_audio"]):
            full_text = f"{lang_texts['diagnosis_sub'].format(translated_disease)}. {lang_texts['about_sub']}: {translated_description}."
            if disease in precautionDictionary:
                full_text += f" {lang_texts['precautions_sub']}: " + " ".join(translate_from_english(p, st.session_state.lang) for p in precautionDictionary[disease])
            
            audio_bytes = generate_tts_with_backoff(lambda: call_tts_api(full_text, st.session_state.lang))
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")

        st.info("💡 " + random.choice([
            "🌸 Health is wealth, take care of yourself.",
            "💪 A healthy outside starts from the inside.",
            "☀️ Every day is a chance to get stronger and healthier."
        ]))
        
        st.markdown(lang_texts["thank_you"].format(st.session_state.name))
        
        if st.button(lang_texts["start_over"]):
            # Keep user logged in but reset the chatbot state
            for key in list(st.session_state.keys()):
                if key not in ['logged_in', 'name', 'lang', 'auth_page']:
                    del st.session_state[key]
            st.session_state.page = "home"
            st.rerun()
