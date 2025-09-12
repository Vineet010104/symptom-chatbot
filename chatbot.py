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
from datetime import datetime
from fpdf import FPDF
import io
import wave

# --- DATABASE SETUP ---
def init_db():
    """Initializes the SQLite database and creates users and history tables."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    # NEW: Create diagnosis history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            symptoms TEXT,
            disease TEXT,
            confidence REAL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# --- PASSWORD HASHING ---
def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password_hash, provided_password):
    """Verifies a provided password against a stored hash."""
    return stored_password_hash == hashlib.sha256(provided_password.encode()).hexdigest()

# --- USER & HISTORY MANAGEMENT FUNCTIONS ---
def add_user(username, password):
    """Adds a new user to the database."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
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

# NEW: Functions to save and retrieve health history
def save_diagnosis_to_history(username, symptoms, disease, confidence):
    """Saves a diagnosis record to the user's history."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symptoms_str = ", ".join(symptoms).replace("_", " ")
    c.execute("INSERT INTO diagnosis_history (username, date, symptoms, disease, confidence) VALUES (?, ?, ?, ?, ?)",
              (username, date_str, symptoms_str, disease, confidence))
    conn.commit()
    conn.close()

def get_diagnosis_history(username):
    """Retrieves all diagnosis records for a given user."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT date, symptoms, disease, confidence FROM diagnosis_history WHERE username = ? ORDER BY date DESC", (username,))
    history = c.fetchall()
    conn.close()
    return history

init_db()

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- CONFIGURATIONS & DICTIONARIES ---
LANGUAGES = {
    "English": "en", "Hindi (हिंदी)": "hi", "Spanish (Español)": "es", "French (Français)": "fr",
    "German (Deutsch)": "de", "Japanese (日本語)": "ja", "Russian (русский)": "ru",
    "Arabic (العربية)": "ar", "Chinese (中文)": "zh", "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu", "Kannada (ಕನ್ನಡ)": "kn", "Malayalam (മലയാളം)": "ml",
    "Marathi (मराठी)": "mr", "Odia (ଓଡ଼ିଆ)": "or", "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Tamil (தமிழ்)": "ta", "Telugu (తెలుగు)": "te",
}

# --- UPDATED UI TEXT ---
UI_TEXT = {
    "en": {
        "title": "HealthCare Chatbot", "intro": "Hello! I am a chatbot designed to help you with preliminary symptom analysis...",
        "name_label": "What is your name?", "age_label": "Please enter your age:", "gender_label": "What is your gender?",
        "gender_options": ["Male", "Female", "Other"], "symptoms_label": "Describe your symptoms (any language):",
        "submit_button": "Submit", "warning_fill_fields": "Please enter your name and symptoms to continue.",
        "thinking": "Analyzing and translating results...", "detected_symptoms": "✅ Detected symptoms: {}",
        "error_no_symptoms": "❌ Sorry, I could not detect valid symptoms. Please try again with more details.",
        "guided_questions_header": "🤔 Guided Questions", "guided_info": "Based on your initial symptoms, you may have **{}** (Confidence: {}%).",
        "guided_prompt": "To get a more accurate diagnosis, please answer a few more questions...",
        "guided_symptom_prompt": "Do you also have **{}**?", "guided_button": "Get Final Prediction",
        "no_more_questions": "No further questions to ask. Click below for your final diagnosis.",
        "result_header": "✨ Diagnosis Result", "diagnosis_sub": "🩺 Based on your answers, you may have **{}**",
        "confidence_label": "Confidence Level", "about_sub": "📖 About", "precautions_sub": "🛡️ Suggested Precautions",
        "no_description": "No description available.", "start_over": "Start Over",
        "thank_you": "Thank you for using the chatbot. Wishing you good health, **{}**!",
        "login_header": "Login", "username_label": "Username", "password_label": "Password",
        "login_button": "Login", "login_error": "Invalid username or password. Please try again.",
        "logout_button": "Logout", "play_audio": "🔊 Play Diagnosis Audio", "signup_header": "Sign Up",
        "signup_button": "Sign Up", "signup_success": "Account created successfully! Please log in.",
        "signup_error_exists": "This username already exists. Please choose another.",
        "signup_error_fields": "Please enter both a username and password.",
        "nav_to_signup": "Don't have an account? Sign Up", "nav_to_login": "Already have an account? Login",
        "health_history_button": "📜 My Health History", "health_history_header": "My Health History",
        "no_history": "You have no saved diagnosis history.", "back_to_chatbot": "⬅️ Back to Chatbot",
        "download_pdf": "📄 Download Report as PDF", "report_title": "Health Diagnosis Report",
        "generating_audio": "Generating audio...",
        "audio_summary": "The diagnosis suggests you may have {}. Please read the description and precautions listed on the page for more details.",
        "audio_error": "Sorry, the audio could not be generated at this time due to high traffic. Please try again later."
    },
    "hi": {
        "title": "हेल्थकेयर चैटबॉट",
        "intro": "नमस्ते! मैं एक चैटबॉट हूँ जो आपको प्रारंभिक लक्षण विश्लेषण में मदद करने के लिए बनाया गया है।",
        "name_label": "आपका नाम क्या है?",
        "age_label": "कृपया अपनी उम्र दर्ज करें:",
        "gender_label": "आपका लिंग क्या है?",
        "gender_options": ["पुरुष", "महिला", "अन्य"],
        "symptoms_label": "अपने लक्षणों का वर्णन करें (किसी भी भाषा में):",
        "submit_button": "जमा करें",
        "warning_fill_fields": "जारी रखने के लिए कृपया अपना नाम और लक्षण दर्ज करें।",
        "thinking": "परिणामों का विश्लेषण और अनुवाद किया जा रहा है...", "detected_symptoms": "✅ पहचाने गए लक्षण: {}",
        "error_no_symptoms": "❌ क्षमा करें, मैं वैध लक्षणों का पता नहीं लगा सका।",
        "guided_questions_header": "🤔 निर्देशित प्रश्न",
        "guided_info": "आपके प्रारंभिक लक्षणों के आधार पर, आपको **{}** हो सकता है (विश्वास: {}%)।",
        "guided_prompt": "अधिक सटीक निदान प्राप्त करने के लिए, कृपया कुछ और प्रश्नों के उत्तर दें।",
        "guided_symptom_prompt": "क्या आपको **{}** भी है?",
        "guided_button": "अंतिम निदान प्राप्त करें",
        "no_more_questions": "पूछने के लिए और कोई प्रश्न नहीं हैं।",
        "result_header": "✨ निदान परिणाम",
        "diagnosis_sub": "🩺 आपके उत्तरों के आधार पर, आपको **{}** हो सकता है",
        "confidence_label": "विश्वास स्तर",
        "about_sub": "📖 के बारे में",
        "precautions_sub": "🛡️ सुझाए गए सावधानियां",
        "no_description": "कोई विवरण उपलब्ध नहीं है।",
        "start_over": "शुरू करें",
        "thank_you": "चैटबॉट का उपयोग करने के लिए धन्यवाद, **{}**!",
        "login_header": "लॉगिन",
        "username_label": "उपयोगकर्ता नाम",
        "password_label": "पासवर्ड",
        "login_button": "लॉगिन",
        "login_error": "गलत उपयोगकर्ता नाम या पासवर्ड।",
        "logout_button": "लॉगआउट",
        "play_audio": "🔊 निदान सुनें",
        "signup_header": "साइन अप करें",
        "signup_button": "साइन अप करें",
        "signup_success": "खाता सफलतापूर्वक बनाया गया! कृपया लॉगिन करें।",
        "signup_error_exists": "यह उपयोगकर्ता नाम पहले से मौजूद है।",
        "signup_error_fields": "कृपया उपयोगकर्ता नाम और पासवर्ड दोनों दर्ज करें।",
        "nav_to_signup": "खाता नहीं है? साइन अप करें",
        "nav_to_login": "पहले से ही खाता है? लॉगिन करें",
        "health_history_button": "📜 मेरा स्वास्थ्य इतिहास",
        "health_history_header": "मेरा स्वास्थ्य इतिहास",
        "no_history": "आपका कोई सहेजा हुआ निदान इतिहास नहीं है।",
        "back_to_chatbot": "⬅️ चैटबॉट पर वापस जाएं",
        "download_pdf": "📄 रिपोर्ट को पीडीएफ के रूप में डाउनलोड करें",
        "report_title": "स्वास्थ्य निदान रिपोर्ट",
        "generating_audio": "ऑडियो बना रहा है...",
        "audio_summary": "निदान से पता चलता है कि आपको {} हो सकता है। अधिक जानकारी के लिए कृपया पृष्ठ पर दिए गए विवरण और सावधानियों को पढ़ें।",
        "audio_error": "क्षमा करें, इस समय अधिक ट्रैफिक के कारण ऑडियो उत्पन्न नहीं किया जा सका। कृपया बाद में पुनः प्रयास करें।"
    },
}

TTS_VOICES = {
    "en": "Kore", "hi": "Kore", "es": "Kore", "fr": "Kore", "de": "Kore", "ja": "Kore",
    "ru": "Kore", "ar": "Kore", "zh": "Kore", "bn": "Kore", "gu": "Kore", "kn": "Kore",
    "ml": "Kore", "mr": "Kore", "or": "Kore", "pa": "Kore", "ta": "Kore", "te": "Kore"
}

# ------------------ Data Loading and Model Training ------------------
@st.cache_data
def load_data():
    try:
        training = pd.read_csv('Data/Training.csv')
        testing = pd.read_csv('Data/Testing.csv')
        training.columns = training.columns.str.strip().str.replace('_', ' ')
        testing.columns = testing.columns.str.strip().str.replace('_', ' ')
        training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
        testing.columns = testing.columns.str.replace(r"\.\d+$", "", regex=True)
        training = training.loc[:,~training.columns.duplicated()]
        testing = testing.loc[:,~testing.columns.duplicated()]
        return training, testing
    except FileNotFoundError:
        st.error("Error: CSV files not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()


@st.cache_data
def load_dictionaries():
    description_list = {}
    precaution_dict = {}
    try:
        with open('MasterData/symptom_Description.csv', encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) > 1:
                    description_list[row[0]] = row[1]
    except Exception:
        pass
    try:
        with open('MasterData/symptom_precaution.csv', encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) > 4:
                    precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]
    except Exception:
        pass
    return description_list, precaution_dict

training, _ = load_data()
description_list, precautionDictionary = load_dictionaries()
cols = list(training.columns)
cols.remove('prognosis')
x = training[cols]
y = training['prognosis']
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)
x_train, _, y_train, _ = train_test_split(x, y, test_size=0.33, random_state=42)

@st.cache_resource
def train_model(_x_train, _y_train):
    model = RandomForestClassifier(n_estimators=100)
    model.fit(_x_train, _y_train)
    return model

model = train_model(x_train, y_train)
symptoms_dict = {symptom: index for index, symptom in enumerate(x.columns)}


# ------------------ Core Chatbot Functions ------------------
def call_gemini_api(payload):
    try:
        apiKey = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"

    if not apiKey:
        st.error("Gemini API key is not configured.")
        return None
        
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={apiKey}"
    try:
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        json_text = result['candidates'][0]['content']['parts'][0]['text']
        return json.loads(json_text)
    except Exception as e:
        st.error(f"API call error: {e}")
        return None

@st.cache_data(show_spinner=False)
def translate_to_english(text):
    if not text: return ""
    prompt = f"Translate the following text to English and provide only the translated text in a JSON format with the key 'translated_text': '{text}'"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json","responseSchema": {"type": "OBJECT", "properties": {"translated_text": {"type": "STRING"}}}},}
    result = call_gemini_api(payload)
    return result.get('translated_text', '') if result else ""

@st.cache_data(show_spinner=False)
def translate_result_texts(disease, description, precautions, target_lang):
    if target_lang == 'en':
        return disease, description, precautions

    precaution_json_str = json.dumps(precautions)
    prompt = f"""Translate the values in this JSON object to the language with code '{target_lang}'. Return a JSON object with the same structure. Input: {{ "disease": "{disease}", "description": "{description}", "precautions": {precaution_json_str} }}"""
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "disease": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "precautions": {"type": "ARRAY", "items": {"type": "STRING"}}
                }
            }
        },
    }
    
    translated_data = call_gemini_api(payload)
    if translated_data:
        return translated_data.get('disease', disease), translated_data.get('description', description), translated_data.get('precautions', precautions)
    return disease, description, precautions


def extract_symptoms(user_input, all_symptoms):
    extracted = []
    text = user_input.lower().replace("_", " ")
    for symptom in all_symptoms:
        if symptom in text:
            extracted.append(symptom)
    for word in text.split():
        matches = get_close_matches(word, all_symptoms, n=1, cutoff=0.8)
        if matches:
            extracted.append(matches[0])
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
    return disease, confidence

def call_tts_api(text, lang_code):
    try:
        apiKey = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"
    
    voice_name = TTS_VOICES.get(lang_code, "Kore")
    payload = { "contents": [{"parts": [{"text": text}]}], "generationConfig": { "responseModalities": ["AUDIO"], "speechConfig": { "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}}},}
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
                st.error(f"An unexpected TTS error: {e}")
                return None
    st.error("Failed to get TTS response after several retries.")
    return None

def pcm_to_wav(pcm_data, channels=1, sample_width=2, frame_rate=24000):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(frame_rate)
        wf.writeframes(pcm_data)
    return buffer.getvalue()

class PDF(FPDF):
    def header(self):
        try:
            self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
            self.set_font("DejaVu", "", 12)
        except RuntimeError:
            self.set_font("Arial", "", 12)
        self.cell(0, 10, st.session_state.lang_texts.get('report_title', 'Health Diagnosis Report'), 1, 1, 'C')

    def chapter_title(self, title):
        try:
            self.set_font("DejaVu", "B", 12)
        except RuntimeError:
            self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)

    def chapter_body(self, body):
        try:
            self.set_font("DejaVu", "", 12)
        except RuntimeError:
            self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf_report(data):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Patient Information")
    pdf.chapter_body(f"Name: {data['name']}\nDate of Report: {datetime.now().strftime('%Y-%m-%d')}")
    pdf.chapter_title("Reported Symptoms")
    pdf.chapter_body(", ".join(data['symptoms']).replace("_", " "))
    pdf.chapter_title("Diagnosis Result")
    pdf.chapter_body(f"Condition: {data['disease']} (Confidence: {data['confidence']}%)")
    pdf.chapter_title("About the Condition")
    pdf.chapter_body(data['description'])
    if data['precautions']:
        pdf.chapter_title("Suggested Precautions")
        prec_text = "\n".join(f"{i}. {p}" for i, p in enumerate(data['precautions'], 1))
        pdf.chapter_body(prec_text)
    return bytes(pdf.output())

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="HealthCare Chatbot", page_icon="🩺")

# Initialize session state
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "home"
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
if "name" not in st.session_state: st.session_state.name = ""
if "symptoms_list" not in st.session_state: st.session_state.symptoms_list = []
if "initial_prediction" not in st.session_state: st.session_state.initial_prediction = None
if "final_prediction" not in st.session_state: st.session_state.final_prediction = None
if "guided_symptoms" not in st.session_state: st.session_state.guided_symptoms = []
if "lang" not in st.session_state: st.session_state.lang = "en"
if "result_saved" not in st.session_state: st.session_state.result_saved = False
if "audio_bytes" not in st.session_state: st.session_state.audio_bytes = None

st.sidebar.title("Language")
selected_lang_name = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
st.session_state.lang = LANGUAGES[selected_lang_name]
st.session_state.lang_texts = UI_TEXT.get(st.session_state.lang, UI_TEXT["en"])
lang_texts = st.session_state.lang_texts

# --- LOGIN/SIGNUP FLOW ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{lang_texts['title']}</h1>", unsafe_allow_html=True)
    if st.session_state.auth_page == "login":
        # ... (Login form UI remains the same)
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
        # ... (Signup form UI remains the same)
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
    if st.sidebar.button(lang_texts["health_history_button"]):
        st.session_state.page = "history"
        st.rerun()
    if st.sidebar.button(lang_texts["logout_button"]):
        st.session_state.clear()
        st.rerun()

    if st.session_state.page == "home":
        # ... (Home page UI is the same)
        st.markdown(lang_texts["intro"])
        with st.form(key="user_info_form"):
            st.text_input(lang_texts["name_label"], value=st.session_state.name, disabled=True)
            age = st.text_input(lang_texts["age_label"])
            gender = st.selectbox(lang_texts["gender_label"], lang_texts["gender_options"])
            symptoms_input_raw = st.text_area(lang_texts["symptoms_label"], height=100)
            submit_button = st.form_submit_button(lang_texts["submit_button"])
        if submit_button:
            if not symptoms_input_raw:
                st.warning(lang_texts["warning_fill_fields"].replace("name and ", ""))
            else:
                with st.spinner(lang_texts["thinking"]):
                    symptoms_input_en = translate_to_english(symptoms_input_raw)
                    detected_symptoms = extract_symptoms(symptoms_input_en, cols)
                    if not detected_symptoms:
                        st.error(lang_texts["error_no_symptoms"])
                    else:
                        st.session_state.symptoms_list = detected_symptoms
                        st.success(lang_texts["detected_symptoms"].format(', '.join(st.session_state.symptoms_list).replace('_', ' ')))
                        initial_disease, confidence = predict_disease(st.session_state.symptoms_list)
                        st.session_state.initial_prediction = {"disease": initial_disease, "confidence": confidence}
                        disease_symptoms = list(training[training['prognosis'] == initial_disease].iloc[0][:-1].index[training[training['prognosis'] == initial_disease].iloc[0][:-1] == 1])
                        st.session_state.guided_symptoms = [sym for sym in disease_symptoms if sym not in st.session_state.symptoms_list][:8]
                        st.session_state.page = "guided_questions"
                        st.session_state.result_saved = False
                        st.session_state.audio_bytes = None
                        st.rerun()
    
    elif st.session_state.page == "guided_questions":
        # ... (Guided questions page is the same)
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
                    final_disease, final_confidence = predict_disease(st.session_state.symptoms_list)
                    st.session_state.final_prediction = {"disease": final_disease, "confidence": final_confidence}
                    st.session_state.page = "result"
                    st.rerun()
        else:
            st.info(lang_texts["no_more_questions"])
            if st.button(lang_texts["guided_button"]):
                final_disease, final_confidence = predict_disease(st.session_state.symptoms_list)
                st.session_state.final_prediction = {"disease": final_disease, "confidence": final_confidence}
                st.session_state.page = "result"
                st.rerun()

    elif st.session_state.page == "result":
        st.header(lang_texts["result_header"])
        final_pred = st.session_state.final_prediction
        disease = final_pred["disease"]
        confidence = final_pred["confidence"]
        
        if not st.session_state.get('result_saved', False):
            save_diagnosis_to_history(st.session_state.name, st.session_state.symptoms_list, disease, confidence)
            st.session_state.result_saved = True

        # --- BATCH TRANSLATION AND PROACTIVE AUDIO GENERATION ---
        with st.spinner(lang_texts["thinking"]):
            precautions_en = precautionDictionary.get(disease, [])
            description_en = description_list.get(disease, lang_texts["no_description"])
            
            translated_disease, translated_description, translated_precautions = translate_result_texts(
                disease, description_en, precautions_en, st.session_state.lang
            )
            
            # --- PROACTIVELY GENERATE AND CACHE AUDIO HERE ---
            if st.session_state.audio_bytes is None:
                audio_summary_text = lang_texts.get("audio_summary", "...").format(translated_disease)
                pcm_audio_bytes = generate_tts_with_backoff(lambda: call_tts_api(audio_summary_text, st.session_state.lang))
                if pcm_audio_bytes:
                    st.session_state.audio_bytes = pcm_to_wav(pcm_audio_bytes)

        # Display results AFTER everything is ready
        st.subheader(lang_texts["diagnosis_sub"].format(translated_disease))
        st.metric(label=lang_texts["confidence_label"], value=f"{confidence}%")
        st.markdown("---")
        st.subheader(lang_texts["about_sub"])
        st.write(translated_description)

        if translated_precautions:
            st.subheader(lang_texts["precautions_sub"])
            for i, prec in enumerate(translated_precautions, 1):
                st.write(f"{i}. {prec}")
        
        st.markdown("---")
        
        pdf_data = {
            "name": st.session_state.name, "symptoms": st.session_state.symptoms_list,
            "disease": translated_disease, "confidence": confidence,
            "description": translated_description, "precautions": translated_precautions
        }
        st.download_button(
            label=lang_texts["download_pdf"], data=generate_pdf_report(pdf_data),
            file_name=f"Health_Report_{st.session_state.name}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        
        # --- SIMPLIFIED AUDIO DISPLAY ---
        audio_placeholder = st.empty()
        if st.button(lang_texts["play_audio"]):
            if st.session_state.audio_bytes:
                audio_placeholder.audio(st.session_state.audio_bytes, format="audio/wav")
            else:
                # This message will show if the proactive generation failed
                audio_placeholder.error(lang_texts["audio_error"])
        
        st.info("💡 " + random.choice(["🌸 Health is wealth...", "💪 A healthy outside starts from the inside..."]))
        st.markdown(lang_texts["thank_you"].format(st.session_state.name))
        if st.button(lang_texts["start_over"]):
            for key in list(st.session_state.keys()):
                if key not in ['logged_in', 'name', 'lang', 'auth_page', 'audio_bytes']: del st.session_state[key]
            st.session_state.page = "home"
            st.rerun()

    elif st.session_state.page == "history":
        # ... (History page is the same)
        st.header(lang_texts["health_history_header"])
        history = get_diagnosis_history(st.session_state.name)
        if not history:
            st.info(lang_texts["no_history"])
        else:
            for record in history:
                date, symptoms, disease, confidence = record
                with st.expander(f"**{disease}** - {date} ({confidence}%)"):
                    st.write(f"**Symptoms Reported:** {symptoms}")
        if st.button(lang_texts["back_to_chatbot"]):
            st.session_state.page = "home"
            st.rerun()