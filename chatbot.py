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

# Translations for UI text
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
    },
    "es": {
        "title": "Chatbot de Salud",
        "intro": "¡Hola! Soy un chatbot diseñado para ayudarte con el análisis preliminar de síntomas. Por favor, responde algunas preguntas para que pueda entender mejor tu condición.",
        "name_label": "¿Cuál es tu nombre?",
        "age_label": "Por favor, ingresa tu edad:",
        "gender_label": "¿Cuál es tu género?",
        "gender_options": ["Masculino", "Femenino", "Otro"],
        "symptoms_label": "Describe tus síntomas (en cualquier idioma):",
        "submit_button": "Enviar",
        "warning_fill_fields": "Por favor, ingresa tu nombre y síntomas para continuar.",
        "thinking": "Pensando...",
        "detected_symptoms": "✅ Síntomas detectados: {}",
        "error_no_symptoms": "❌ Lo siento, no pude detectar síntomas válidos. Por favor, inténtalo de nuevo con más detalles.",
        "guided_questions_header": "🤔 Preguntas guiadas",
        "guided_info": "Basado en tus síntomas iniciales, podrías tener **{}** (Confianza: {}%).",
        "guided_prompt": "Para obtener un diagnóstico más preciso, por favor, responde algunas preguntas más relacionadas con esta condición.",
        "guided_symptom_prompt": "¿También tienes **{}**?",
        "guided_button": "Obtener diagnóstico final",
        "no_more_questions": "No hay más preguntas que hacer. Haz clic a continuación para tu diagnóstico final.",
        "result_header": "✨ Resultado del diagnóstico",
        "diagnosis_sub": "🩺 Basado en tus respuestas, podrías tener **{}**",
        "confidence_label": "Nivel de confianza",
        "about_sub": "📖 Acerca de",
        "precautions_sub": "🛡️ Precauciones sugeridas",
        "no_description": "No hay descripción disponible.",
        "start_over": "Empezar de nuevo",
        "thank_you": "Gracias por usar el chatbot. ¡Te deseo buena salud, **{}**!",
        "login_header": "Iniciar sesión",
        "username_label": "Nombre de usuario",
        "password_label": "Contraseña",
        "login_button": "Iniciar sesión",
        "login_error": "Nombre de usuario o contraseña no válidos. Inténtalo de nuevo.",
        "logout_button": "Cerrar sesión",
        "play_audio": "🔊 Reproducir diagnóstico",
    },
    "bn": {
        "title": "স্বাস্থ্যসেবা চ্যাটবট",
        "intro": "নমস্কার! আমি একটি চ্যাটবট যা আপনাকে প্রাথমিক লক্ষণ বিশ্লেষণে সহায়তা করার জন্য ডিজাইন করা হয়েছে। আমি আপনার অবস্থা আরও ভালোভাবে বুঝতে পারি, তাই অনুগ্রহ করে কয়েকটি প্রশ্নের উত্তর দিন।",
        "name_label": "আপনার নাম কি?",
        "age_label": "আপনার বয়স লিখুন:",
        "gender_label": "আপনার লিঙ্গ কি?",
        "gender_options": ["পুরুষ", "মহিলা", "অন্যান্য"],
        "symptoms_label": "আপনার লক্ষণগুলি বর্ণনা করুন (যে কোনো ভাষায়):",
        "submit_button": "জমা দিন",
        "warning_fill_fields": "চালিয়ে যেতে, আপনার নাম এবং লক্ষণ লিখুন।",
        "thinking": "চিন্তা করা হচ্ছে...",
        "detected_symptoms": "✅ সনাক্ত করা লক্ষণ: {}",
        "error_no_symptoms": "❌ দুঃখিত, আমি কোনো বৈধ লক্ষণ সনাক্ত করতে পারিনি। দয়া করে আরও বিস্তারিত তথ্য দিয়ে আবার চেষ্টা করুন।",
        "guided_questions_header": "🤔 নির্দেশিত প্রশ্নাবলী",
        "guided_info": "আপনার প্রাথমিক লক্ষণের উপর ভিত্তি করে, আপনার **{}** থাকতে পারে (আত্মবিশ্বাস: {}%)।",
        "guided_prompt": "আরও নির্ভুল রোগ নির্ণয়ের জন্য, দয়া করে এই অবস্থা সম্পর্কিত আরও কিছু প্রশ্নের উত্তর দিন।",
        "guided_symptom_prompt": "আপনার কি **{}**ও আছে?",
        "guided_button": "চূড়ান্ত নির্ণয় পান",
        "no_more_questions": "আর কোনো প্রশ্ন করার নেই। আপনার চূড়ান্ত নির্ণয়ের জন্য নিচে ক্লিক করুন।",
        "result_header": "✨ রোগ নির্ণয়ের ফলাফল",
        "diagnosis_sub": "🩺 আপনার উত্তরের উপর ভিত্তি করে, আপনার **{}** থাকতে পারে",
        "confidence_label": "আত্মবিশ্বাসের স্তর",
        "about_sub": "📖 সম্পর্কে",
        "precautions_sub": "🛡️ প্রস্তাবিত সতর্কতা",
        "no_description": "কোনো বর্ণনা নেই।",
        "start_over": "আবার শুরু করুন",
        "thank_you": "চ্যাটবট ব্যবহার করার জন্য আপনাকে ধন্যবাদ। আপনার সুস্বাস্থ্য কামনা করি, **{}**!",
        "login_header": "লগইন",
        "username_label": "ব্যবহারকারীর নাম",
        "password_label": "পাসওয়ার্ড",
        "login_button": "লগইন",
        "login_error": "ভুল ব্যবহারকারীর নাম বা পাসওয়ার্ড। আবার চেষ্টা করুন।",
        "logout_button": "লগআউট",
        "play_audio": "🔊 রোগ নির্ণয় শোনান",
    },
    "kn": {
        "title": "ಆರೋಗ್ಯ ರಕ್ಷಣಾ ಚಾಟ್‌ಬಾಟ್",
        "intro": "ನಮಸ್ಕಾರ! ನಾನು ಪ್ರಾಥಮಿಕ ರೋಗಲಕ್ಷಣಗಳ ವಿಶ್ಲೇಷಣೆಯಲ್ಲಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಒಂದು ಚಾಟ್‌ಬಾಟ್. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸ್ಥಿತಿಯನ್ನು ನಾನು ಉತ್ತಮವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ.",
        "name_label": "ನಿಮ್ಮ ಹೆಸರೇನು?",
        "age_label": "ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸನ್ನು ನಮೂದಿಸಿ:",
        "gender_label": "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು?",
        "gender_options": ["ಪುರುಷ", "ಮಹಿಳೆ", "ಇತರ"],
        "symptoms_label": "ನಿಮ್ಮ ರೋಗಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ (ಯಾವುದೇ ಭಾಷೆಯಲ್ಲಿ):",
        "submit_button": "ಸಲ್ಲಿಸು",
        "warning_fill_fields": "ಮುಂದುವರಿಯಲು ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರು ಮತ್ತು ರೋಗಲಕ್ಷಣಗಳನ್ನು ನಮೂದಿಸಿ.",
        "thinking": "ಆಲೋಚಿಸುತ್ತಿದೆ...",
        "detected_symptoms": "✅ ಪತ್ತೆಯಾದ ರೋಗಲಕ್ಷಣಗಳು: {}",
        "error_no_symptoms": "❌ ಕ್ಷಮಿಸಿ, ನಾನು ಸರಿಯಾದ ರೋಗಲಕ್ಷಣಗಳನ್ನು ಪತ್ತೆಹಚ್ಚಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಹೆಚ್ಚಿನ ವಿವರಗಳೊಂದಿಗೆ ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.",
        "guided_questions_header": "🤔 ಮಾರ್ಗದರ್ಶಿ ಪ್ರಶ್ನೆಗಳು",
        "guided_info": "ನಿಮ್ಮ ಆರಂಭಿಕ ರೋಗಲಕ್ಷಣಗಳ ಆಧಾರದ ಮೇಲೆ, ನಿಮಗೆ **{}** ಇರಬಹುದು (ವಿಶ್ವಾಸಾರ್ಹತೆ: {}%).",
        "guided_prompt": "ಹೆಚ್ಚು ನಿಖರವಾದ ರೋಗನಿರ್ಣಯವನ್ನು ಪಡೆಯಲು, ದಯವಿಟ್ಟು ಈ ಸ್ಥಿತಿಗೆ ಸಂಬಂಧಿಸಿದ ಕೆಲವು ಹೆಚ್ಚುವರಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ.",
        "guided_symptom_prompt": "ನಿಮಗೆ **{}** ಕೂಡ ಇದೆಯೇ?",
        "guided_button": "ಅಂತಿಮ ಭವಿಷ್ಯ ಪಡೆಯಿರಿ",
        "no_more_questions": "ಕೇಳಲು ಯಾವುದೇ ಹೆಚ್ಚಿನ ಪ್ರಶ್ನೆಗಳಿಲ್ಲ. ನಿಮ್ಮ ಅಂತಿಮ ರೋಗನಿರ್ಣಯಕ್ಕಾಗಿ ಕೆಳಗೆ ಕ್ಲಿಕ್ ಮಾಡಿ.",
        "result_header": "✨ ರೋಗನಿರ್ಣಯದ ಫಲಿತಾಂಶ",
        "diagnosis_sub": "🩺 ನಿಮ್ಮ ಉತ್ತರಗಳ ಆಧಾರದ ಮೇಲೆ, ನಿಮಗೆ **{}** ಇರಬಹುದು",
        "confidence_label": "ವಿಶ್ವಾಸಾರ್ಹತೆಯ ಮಟ್ಟ",
        "about_sub": "📖 ಬಗ್ಗೆ",
        "precautions_sub": "🛡️ ಸೂಚಿಸಿದ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು",
        "no_description": "ಯಾವುದೇ ವಿವರಣೆ ಲಭ್ಯವಿಲ್ಲ.",
        "start_over": "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸು",
        "thank_you": "ಚಾಟ್‌ಬಾಟ್ ಬಳಸಿದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನಿಮಗೆ ಉತ್ತಮ ಆರೋಗ್ಯ ಹಾರೈಸುತ್ತೇನೆ, **{}**!",
        "login_header": "ಲಾಗ್ ಇನ್ ಮಾಡಿ",
        "username_label": "ಬಳಕೆದಾರ ಹೆಸರು",
        "password_label": "ಪಾಸ್ವರ್ಡ್",
        "login_button": "ಲಾಗ್ ಇನ್ ಮಾಡಿ",
        "login_error": "ಅಮಾನ್ಯ ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಪಾಸ್ವರ್ಡ್. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.",
        "logout_button": "ಲಾಗ್ ಔಟ್ ಮಾಡಿ",
        "play_audio": "🔊 ರೋಗನಿರ್ಣಯ ಕೇಳಿ",
    },
    "gu": {
        "title": "હેલ્થકેર ચેટબોટ",
        "intro": "નમસ્કાર! હું એક ચેટબોટ છું જે તમને પ્રાથમિક લક્ષણ વિશ્લેષણમાં મદદ કરવા માટે ડિઝાઇન કરવામાં આવ્યો છે. કૃપા કરીને થોડા પ્રશ્નોના જવાબ આપો જેથી હું તમારી સ્થિતિને વધુ સારી રીતે સમજી શકું.",
        "name_label": "તમારું નામ શું છે?",
        "age_label": "કૃપા કરીને તમારી ઉંમર દાખલ કરો:",
        "gender_label": "તમારું લિંગ શું છે?",
        "gender_options": ["પુરુષ", "સ્ત્રી", "અન્ય"],
        "symptoms_label": "તમારા લક્ષણોનું વર્ણન કરો (કોઈપણ ભાષામાં):",
        "submit_button": "સબમિટ કરો",
        "warning_fill_fields": "કૃપા કરીને ચાલુ રાખવા માટે તમારું નામ અને લક્ષણો દાખલ કરો.",
        "thinking": "વિચારણા કરી રહ્યું છે...",
        "detected_symptoms": "✅ મળેલા લક્ષણો: {}",
        "error_no_symptoms": "❌ માફ કરશો, હું માન્ય લક્ષણો શોધી શક્યો નથી. કૃપા કરીને વધુ વિગતો સાથે ફરીથી પ્રયાસ કરો.",
        "guided_questions_header": "🤔 માર્ગદર્શિત પ્રશ્નો",
        "guided_info": "તમારા પ્રારંભિક લક્ષણોના આધારે, તમને **{}** હોઈ શકે છે (વિશ્વાસ: {}%).",
        "guided_prompt": "વધુ સચોટ નિદાન મેળવવા માટે, કૃપા કરીને આ સ્થિતિ સંબંધિત થોડા વધુ પ્રશ્નોના જવાબ આપો.",
        "guided_symptom_prompt": "શું તમને **{}** પણ છે?",
        "guided_button": "અંતિમ નિદાન મેળવો",
        "no_more_questions": "પૂછવા માટે અન્ય કોઈ પ્રશ્નો નથી. તમારા અંતિમ નિદાન માટે નીચે ક્લિક કરો.",
        "result_header": "✨ નિદાન પરિણામ",
        "diagnosis_sub": "🩺 તમારા જવાબોના આધારે, તમને **{}** હોઈ શકે છે",
        "confidence_label": "વિશ્વાસ સ્તર",
        "about_sub": "📖 વિશે",
        "precautions_sub": "🛡️ સૂચવેલ સાવચેતીઓ",
        "no_description": "કોઈ વર્ણન ઉપલબ્ધ નથી.",
        "start_over": "ફરી શરૂ કરો",
        "thank_you": "ચેટબોટનો ઉપયોગ કરવા બદલ આભાર. તમારા સારા સ્વાસ્થ્યની શુભેચ્છા, **{}**!",
        "login_header": "લૉગિન",
        "username_label": "વપરાશકર્તા નામ",
        "password_label": "પાસવર્ડ",
        "login_button": "લૉગિન",
        "login_error": "અમાન્ય વપરાશકર્તા નામ અથવા પાસવર્ડ. કૃપા કરીને ફરીથી પ્રયાસ કરો.",
        "logout_button": "લૉગઆઉટ",
        "play_audio": "🔊 નિદાન સાંભળો",
    },
    "ml": {
        "title": "ആരോഗ്യ സംരക്ഷണം ചാറ്റ്ബോട്ട്",
        "intro": "നമസ്കാരം! പ്രാഥമിക രോഗനിർണയ വിശകലനത്തിന് നിങ്ങളെ സഹായിക്കാൻ രൂപകൽപ്പന ചെയ്ത ഒരു ചാറ്റ്ബോട്ടാണ് ഞാൻ. നിങ്ങളുടെ അവസ്ഥ നന്നായി മനസ്സിലാക്കാൻ ദയവായി കുറച്ച് ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകുക.",
        "name_label": "നിങ്ങളുടെ പേരെന്താണ്?",
        "age_label": "ദയവായി നിങ്ങളുടെ പ്രായം നൽകുക:",
        "gender_label": "നിങ്ങളുടെ ലിംഗം എന്താണ്?",
        "gender_options": ["പുരുഷൻ", "സ്ത്രീ", "മറ്റുള്ളവ"],
        "symptoms_label": "നിങ്ങളുടെ ലക്ഷണങ്ങൾ വിവരിക്കുക (ഏത് ഭാഷയിലും):",
        "submit_button": "സമർപ്പിക്കുക",
        "warning_fill_fields": "തുടരാൻ, നിങ്ങളുടെ പേരും ലക്ഷണങ്ങളും നൽകുക.",
        "thinking": "ചിന്തിക്കുന്നു...",
        "detected_symptoms": "✅ കണ്ടെത്തിയ ലക്ഷണങ്ങൾ: {}",
        "error_no_symptoms": "❌ ക്ഷമിക്കണം, എനിക്ക് സാധുവായ ലക്ഷണങ്ങൾ കണ്ടെത്താൻ കഴിഞ്ഞില്ല. കൂടുതൽ വിവരങ്ങൾ നൽകി വീണ്ടും ശ്രമിക്കുക.",
        "guided_questions_header": "🤔 മാർഗ്ഗനിർദ്ദേശ ചോദ്യങ്ങൾ",
        "guided_info": "നിങ്ങളുടെ പ്രാഥമിക ലക്ഷണങ്ങളെ അടിസ്ഥാനമാക്കി, നിങ്ങൾക്ക് **{}** ഉണ്ടാകാൻ സാധ്യതയുണ്ട് (വിശ്വാസ്യത: {}%).",
        "guided_prompt": "കൂടുതൽ കൃത്യമായ രോഗനിർണയം ലഭിക്കുന്നതിന്, ഈ അവസ്ഥയുമായി ബന്ധപ്പെട്ട കൂടുതൽ ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകുക.",
        "guided_symptom_prompt": "നിങ്ങൾക്ക് **{}**ഉം ഉണ്ടോ?",
        "guided_button": "അന്തിമ രോഗനിർണയം നേടുക",
        "no_more_questions": "ചോദിക്കാൻ കൂടുതൽ ചോദ്യങ്ങളില്ല. നിങ്ങളുടെ അന്തിമ രോഗനിർണയത്തിനായി താഴെ ക്ലിക്ക് ചെയ്യുക.",
        "result_header": "✨ രോഗനിർണയ ഫലം",
        "diagnosis_sub": "🩺 നിങ്ങളുടെ ഉത്തരങ്ങളെ അടിസ്ഥാനമാക്കി, നിങ്ങൾക്ക് **{}** ഉണ്ടാകാം",
        "confidence_label": "വിശ്വാസ്യത നില",
        "about_sub": "📖 കുറിച്ച്",
        "precautions_sub": "🛡️ നിർദ്ദേശിക്കപ്പെട്ട മുൻകരുതലുകൾ",
        "no_description": "വിവരണം ലഭ്യമല്ല.",
        "start_over": "വീണ്ടും ആരംഭിക്കുക",
        "thank_you": "ചാറ്റ്ബോട്ട് ഉപയോഗിച്ചതിന് നന്ദി. നിങ്ങൾക്ക് നല്ല ആരോഗ്യം നേരുന്നു, **{}**!",
        "login_header": "ലോഗിൻ ചെയ്യുക",
        "username_label": "ഉപയോക്തൃനാമം",
        "password_label": "പാസ്‌വേഡ്",
        "login_button": "ലോഗിൻ ചെയ്യുക",
        "login_error": "അസാധുവായ ഉപയോക്തൃനാമം അല്ലെങ്കിൽ പാസ്‌വേഡ്. വീണ്ടും ശ്രമിക്കുക.",
        "logout_button": "പുറത്തുകടക്കുക",
        "play_audio": "🔊 രോഗനിർണയം കേൾക്കുക",
    },
    "mr": {
        "title": "आरोग्यसेवा चॅटबॉट",
        "intro": "नमस्कार! मी एक चॅटबॉट आहे, जो तुम्हाला प्राथमिक लक्षणांचे विश्लेषण करण्यास मदत करण्यासाठी डिझाइन केला आहे। कृपया काही प्रश्नांची उत्तरे द्या जेणेकरून मी तुमची स्थिती अधिक चांगल्या प्रकारे समजू शकेन।",
        "name_label": "तुमचे नाव काय आहे?",
        "age_label": "कृपया तुमचे वय प्रविष्ट करा:",
        "gender_label": "तुमचे लिंग काय आहे?",
        "gender_options": ["पुरुष", "महिला", "इतर"],
        "symptoms_label": "तुमच्या लक्षणांचे वर्णन करा (कोणत्याही भाषेत):",
        "submit_button": "सादर करा",
        "warning_fill_fields": "पुढे चालू ठेवण्यासाठी कृपया तुमचे नाव आणि लक्षणे प्रविष्ट करा.",
        "thinking": "विचार करत आहे...",
        "detected_symptoms": "✅ आढळलेली लक्षणे: {}",
        "error_no_symptoms": "❌ माफ करा, मला वैध लक्षणे आढळली नाहीत। कृपया अधिक तपशील देऊन पुन्हा प्रयत्न करा।",
        "guided_questions_header": "🤔 मार्गदर्शित प्रश्न",
        "guided_info": "तुमच्या सुरुवातीच्या लक्षणांवर आधारित, तुम्हाला **{}** असू शकतो (आत्मविश्वास: {}%)।",
        "guided_prompt": "अधिक अचूक निदान मिळवण्यासाठी, कृपया या स्थितीशी संबंधित आणखी काही प्रश्नांची उत्तरे द्या।",
        "guided_symptom_prompt": "तुम्हाला **{}** देखील आहे का?",
        "guided_button": "अंतिम निदान मिळवा",
        "no_more_questions": "विचारण्यासाठी आणखी प्रश्न नाहीत। तुमच्या अंतिम निदानासाठी खालील बटणावर क्लिक करा।",
        "result_header": "✨ निदानाचा निकाल",
        "diagnosis_sub": "🩺 तुमच्या उत्तरांवर आधारित, तुम्हाला **{}** असू शकतो",
        "confidence_label": "आत्मविश्वास पातळी",
        "about_sub": "📖 बद्दल",
        "precautions_sub": "🛡️ सुचवलेले प्रतिबंध",
        "no_description": "कोणतेही वर्णन उपलब्ध नाही।",
        "start_over": "पुन्हा सुरू करा",
        "thank_you": "चॅटबॉट वापरल्याबद्दल धन्यवाद। तुमच्या चांगल्या आरोग्यासाठी शुभेच्छा, **{}**!",
        "login_header": "लॉगिन",
        "username_label": "वापरकर्ता नाव",
        "password_label": "पासवर्ड",
        "login_button": "लॉगिन",
        "login_error": "अवैध वापरकर्ता नाव किंवा पासवर्ड। कृपया पुन्हा प्रयत्न करा।",
        "logout_button": "लॉगआउट",
        "play_audio": "🔊 निदान ऐका",
    },
    "or": {
        "title": "ହେଲ୍ଥକେୟାର ଚାଟବୋଟ୍",
        "intro": "ନମସ୍କାର! ମୁଁ ଏକ ଚାଟବୋଟ୍ ଅଟେ ଯାହା ଆପଣଙ୍କୁ ପ୍ରାଥମିକ ରୋଗ ଲକ୍ଷଣ ବିଶ୍ଳେଷଣରେ ସାହାଯ୍ୟ କରିବା ପାଇଁ ଡିଜାଇନ୍ କରାଯାଇଛି। ମୁଁ ଆପଣଙ୍କ ଅବସ୍ଥାକୁ ଭଲ ଭାବରେ ବୁଝିପାରିବା ପାଇଁ ଦୟାକରି କିଛି ପ୍ରଶ୍ନର ଉତ୍ତର ଦିଅନ୍ତୁ।",
        "name_label": "ଆପଣଙ୍କ ନାମ କ'ଣ?",
        "age_label": "ଦୟାକରି ଆପଣଙ୍କ ବୟସ ଦିଅନ୍ତୁ:",
        "gender_label": "ଆପଣଙ୍କ ଲିଙ୍ଗ କ'ଣ?",
        "gender_options": ["ପୁରୁଷ", "ମହିଳା", "ଅନ୍ୟ"],
        "symptoms_label": "ଆପଣଙ୍କ ରୋଗଲକ୍ଷଣ ବର୍ଣ୍ଣନା କରନ୍ତୁ (ଯେକୌଣସି ଭାଷାରେ):",
        "submit_button": "ଦାଖଲ କରନ୍ତୁ",
        "warning_fill_fields": "ଆଗକୁ ବଢିବା ପାଇଁ ଦୟାକରି ଆପଣଙ୍କ ନାମ ଏବଂ ରୋଗଲକ୍ଷଣ ଦାଖଲ କରନ୍ତୁ।",
        "thinking": "ଭାବୁଛି...",
        "detected_symptoms": "✅ ଚିହ୍ନଟ ହୋଇଥିବା ରୋଗଲକ୍ଷଣ: {}",
        "error_no_symptoms": "❌ ଦୁଃଖିତ, ମୁଁ ବୈଧ ରୋଗଲକ୍ଷଣ ଚିହ୍ନଟ କରିପାରିଲି ନାହିଁ। ଦୟାକରି ଅଧିକ ବିବରଣୀ ସହିତ ପୁନର୍ବାର ଚେଷ୍ଟା କରନ୍ତୁ।",
        "guided_questions_header": "🤔 ମାର୍ଗଦର୍ଶକ ପ୍ରଶ୍ନ",
        "guided_info": "ଆପଣଙ୍କ ପ୍ରାରମ୍ଭିକ ରୋଗଲକ୍ଷଣ ଉପରେ ଆଧାର କରି, ଆପଣଙ୍କୁ **{}** ହୋଇପାରେ (ଆତ୍ମବିଶ୍ୱାସ: {}%)।",
        "guided_prompt": "ଅଧିକ ସଠିକ୍ ରୋଗନିର୍ଣ୍ଣୟ ପାଇଁ, ଦୟାକରି ଏହି ଅବସ୍ଥା ସମ୍ବନ୍ଧୀୟ ଆଉ କିଛି ପ୍ରଶ୍ନର ଉତ୍ତର ଦିଅନ୍ତୁ।",
        "guided_button": "ଅନ୍ତିମ ରୋଗନିର୍ଣ୍ଣୟ ପାଆନ୍ତୁ",
        "no_more_questions": "କୌଣସି ଅଧିକ ପ୍ରଶ୍ନ ନାହିଁ। ଆପଣଙ୍କ ଅନ୍ତିମ ରୋଗନିର୍ଣ୍ଣୟ ପାଇଁ ତଳେ କ୍ଲିକ୍ କରନ୍ତୁ।",
        "result_header": "✨ ରୋଗନିର୍ଣ୍ଣୟ ଫଳାଫଳ",
        "diagnosis_sub": "🩺 ଆପଣଙ୍କ ଉତ୍ତର ଉପରେ ଆଧାର କରି, ଆପଣଙ୍କୁ **{}** ହୋଇପାରେ",
        "confidence_label": "ଆତ୍ମବିଶ୍ୱାସ ସ୍ତର",
        "about_sub": "📖 ବିଷୟରେ",
        "precautions_sub": "🛡️ ସୁଝାଯାଇଥିବା ସାବଧାନତା",
        "no_description": "କୌଣସି ବର୍ଣ୍ଣନା ଉପଲବ୍ଧ ନାହିଁ।",
        "start_over": "ପୁନର୍ବାର ଆରମ୍ଭ କରନ୍ତୁ",
        "thank_you": "ଚାଟବୋଟ୍ ବ୍ୟବହାର କରିଥିବାରୁ ଧନ୍ୟବାଦ। ଆପଣଙ୍କୁ ଭଲ ସ୍ୱାସ୍ଥ୍ୟ କାମନା କରୁଛି, **{}**!",
        "login_header": "ଲଗ୍ ଇନ୍",
        "username_label": "ଉପଭୋକ୍ତା ନାମ",
        "password_label": "ପାସୱାର୍ଡ",
        "login_button": "ଲଗ୍ ଇନ୍",
        "login_error": "ଅବୈଧ ଉପଭୋକ୍ତା ନାମ କିମ୍ବା ପାସୱାର୍ଡ। ଦୟାକରି ପୁନର୍ବାର ଚେଷ୍ଟା କରନ୍ତୁ।",
        "logout_button": "ଲଗ୍ ଆଉଟ୍",
        "play_audio": "🔊 ରୋଗନିର୍ଣ୍ଣୟ ଶୁଣନ୍ତୁ",
    },
    "pa": {
        "title": "ਸਿਹਤ ਸੰਭਾਲ ਚੈਟਬੋਟ",
        "intro": "ਹੈਲੋ! ਮੈਂ ਇੱਕ ਚੈਟਬੋਟ ਹਾਂ ਜੋ ਤੁਹਾਨੂੰ ਸ਼ੁਰੂਆਤੀ ਲੱਛਣਾਂ ਦੇ ਵਿਸ਼ਲੇਸ਼ਣ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਤਿਆਰ ਕੀਤਾ ਗਿਆ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਕੁਝ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ ਤਾਂ ਜੋ ਮੈਂ ਤੁਹਾਡੀ ਸਥਿਤੀ ਨੂੰ ਬਿਹਤਰ ਢੰਗ ਨਾਲ ਸਮਝ ਸਕਾਂ।",
        "name_label": "ਤੁਹਾਡਾ ਨਾਮ ਕੀ ਹੈ?",
        "age_label": "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਉਮਰ ਦਾਖਲ ਕਰੋ:",
        "gender_label": "ਤੁਹਾਡਾ ਲਿੰਗ ਕੀ ਹੈ?",
        "gender_options": ["ਪੁਰਸ਼", "ਇਸਤਰੀ", "ਹੋਰ"],
        "symptoms_label": "ਆਪਣੇ ਲੱਛਣਾਂ ਦਾ ਵਰਣਨ ਕਰੋ (ਕਿਸੇ ਵੀ ਭਾਸ਼ਾ ਵਿੱਚ):",
        "submit_button": "ਦਾਖਲ ਕਰੋ",
        "warning_fill_fields": "ਕਿਰਪਾ ਕਰਕੇ ਜਾਰੀ ਰੱਖਣ ਲਈ ਆਪਣਾ ਨਾਮ ਅਤੇ ਲੱਛਣ ਦਾਖਲ ਕਰੋ।",
        "thinking": "ਸੋਚ ਰਿਹਾ ਹੈ...",
        "detected_symptoms": "✅ ਪਛਾਣੇ ਗਏ ਲੱਛਣ: {}",
        "error_no_symptoms": "❌ ਮਾਫ ਕਰਨਾ, ਮੈਂ ਕੋਈ ਵੈਧ ਲੱਛਣ ਪਛਾਣ ਨਹੀਂ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਹੋਰ ਵੇਰਵਿਆਂ ਨਾਲ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "guided_questions_header": "🤔 ਗਾਈਡਡ ਸਵਾਲ",
        "guided_info": "ਤੁਹਾਡੇ ਸ਼ੁਰੂਆਤੀ ਲੱਛਣਾਂ ਦੇ ਆਧਾਰ 'ਤੇ, ਤੁਹਾਨੂੰ **{}** ਹੋ ਸਕਦਾ ਹੈ (ਭਰੋਸਾ: {}%)।",
        "guided_prompt": "ਵਧੇਰੇ ਸਹੀ ਨਿਦਾਨ ਪ੍ਰਾਪਤ ਕਰਨ ਲਈ, ਕਿਰਪਾ ਕਰਕੇ ਇਸ ਸਥਿਤੀ ਨਾਲ ਸੰਬੰਧਿਤ ਕੁਝ ਹੋਰ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ।",
        "guided_symptom_prompt": "ਕੀ ਤੁਹਾਨੂੰ **{}** ਵੀ ਹੈ?",
        "guided_button": "ਅੰਤਿਮ ਨਿਦਾਨ ਪ੍ਰਾਪਤ ਕਰੋ",
        "no_more_questions": "ਪੁੱਛਣ ਲਈ ਹੋਰ ਕੋਈ ਸਵਾਲ ਨਹੀਂ ਹਨ। ਆਪਣੇ ਅੰਤਿਮ ਨਿਦਾਨ ਲਈ ਹੇਠਾਂ ਕਲਿੱਕ ਕਰੋ।",
        "result_header": "✨ ਨਿਦਾਨ ਦਾ ਨਤੀਜਾ",
        "diagnosis_sub": "🩺 ਤੁਹਾਡੇ ਜਵਾਬਾਂ ਦੇ ਆਧਾਰ 'ਤੇ, ਤੁਹਾਨੂੰ **{}** ਹੋ ਸਕਦਾ ਹੈ",
        "confidence_label": "ਭਰੋਸੇ ਦਾ ਪੱਧਰ",
        "about_sub": "📖 ਬਾਰੇ",
        "precautions_sub": "🛡️ ਸੁਝਾਏ ਗਏ ਸਾਵਧਾਨੀਆਂ",
        "no_description": "ਕੋਈ ਵੇਰਵਾ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
        "start_over": "ਦੁਬਾਰਾ ਸ਼ੁਰੂ ਕਰੋ",
        "thank_you": "ਚੈਟਬੋਟ ਦੀ ਵਰਤੋਂ ਕਰਨ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ। ਤੁਹਾਡੀ ਚੰਗੀ ਸਿਹਤ ਦੀ ਕਾਮਨਾ, **{}**!",
        "login_header": "ਲੌਗਇਨ",
        "username_label": "ਯੂਜ਼ਰਨੇਮ",
        "password_label": "ਪਾਸਵਰਡ",
        "login_button": "ਲੌਗਇਨ",
        "login_error": "ਗਲਤ ਯੂਜ਼ਰਨੇਮ ਜਾਂ ਪਾਸਵਰਡ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "logout_button": "ਲੌਗਆਉਟ",
        "play_audio": "🔊 ਨਿਦਾਨ ਸੁਣੋ",
    },
    "ta": {
        "title": "சுகாதார அரட்டை பொட்டி",
        "intro": "வணக்கம்! நான் ஒரு அரட்டை பொட்டி. ஆரம்பகால நோயறிதலுக்கு உங்களுக்கு உதவ நான் வடிவமைக்கப்பட்டுள்ளேன். உங்கள் நிலையை நான் சிறப்பாகப் புரிந்துகொள்ள சில கேள்விகளுக்குப் பதிலளிக்கவும்.",
        "name_label": "உங்கள் பெயர் என்ன?",
        "age_label": "உங்கள் வயதை உள்ளிடவும்:",
        "gender_label": "உங்கள் பாலினம் என்ன?",
        "gender_options": ["ஆண்", "பெண்", "மற்றவை"],
        "symptoms_label": "உங்கள் அறிகுறிகளை விவரிக்கவும் (ஏதேனும் மொழியில்):",
        "submit_button": "சமர்ப்பி",
        "warning_fill_fields": "தொடர, உங்கள் பெயர் மற்றும் அறிகுறிகளை உள்ளிடவும்.",
        "thinking": "சிந்தித்துக்கொண்டிருக்கிறது...",
        "detected_symptoms": "✅ கண்டறியப்பட்ட அறிகுறிகள்: {}",
        "error_no_symptoms": "❌ மன்னிக்கவும், சரியான அறிகுறிகளைக் கண்டறிய முடியவில்லை. மேலும் விவரங்களுடன் மீண்டும் முயற்சிக்கவும்.",
        "guided_questions_header": "🤔 வழிகாட்டப்பட்ட கேள்விகள்",
        "guided_info": "உங்கள் ஆரம்ப அறிகுறிகளின் அடிப்படையில், உங்களுக்கு **{}** இருக்கலாம் (நம்பிக்கை: {}%).",
        "guided_prompt": "மேலும் துல்லியமான நோயறிதலைப் பெற, இந்த நிலை தொடர்பான இன்னும் சில கேள்விகளுக்குப் பதிலளிக்கவும்.",
        "guided_symptom_prompt": "உங்களுக்கு **{}**ம் உள்ளதா?",
        "guided_button": "இறுதி நோயறிதலைப் பெறு",
        "no_more_questions": "கேட்பதற்கு வேறு கேள்விகள் இல்லை. உங்கள் இறுதி நோயறிதலுக்கு கீழே கிளிக் செய்யவும்.",
        "result_header": "✨ நோயறிதல் முடிவு",
        "diagnosis_sub": "🩺 உங்கள் பதில்களின் அடிப்படையில், உங்களுக்கு **{}** இருக்கலாம்",
        "confidence_label": "நம்பிக்கை நிலை",
        "about_sub": "📖 பற்றி",
        "precautions_sub": "🛡️ பரிந்துரைக்கப்பட்ட முன்னெச்சரிக்கைகள்",
        "no_description": "விளக்கம் இல்லை.",
        "start_over": "மீண்டும் தொடங்கு",
        "thank_you": "அரட்டை பொட்டியைப் பயன்படுத்தியதற்கு நன்றி. உங்கள் நல்ல ஆரோக்கியத்திற்கு வாழ்த்துக்கள், **{}**!",
        "login_header": "உள்நுழைவு",
        "username_label": "பயனர் பெயர்",
        "password_label": "கடவுச்சொல்",
        "login_button": "உள்நுழைவு",
        "login_error": "சரியான பயனர் பெயர் அல்லது கடவுச்சொல்லை உள்ளிடவும். மீண்டும் முயற்சிக்கவும்.",
        "logout_button": "வெளியேறு",
        "play_audio": "🔊 நோயறிதலைக் கேட்கவும்",
    },
    "te": {
        "title": "ఆరోగ్య సంరక్షణ చాట్‌బాట్",
        "intro": "నమస్కారం! నేను ప్రాథమిక లక్షణాల విశ్లేషణలో మీకు సహాయపడటానికి రూపొందించిన చాట్‌బాట్. మీ పరిస్థితిని బాగా అర్థం చేసుకోవడానికి దయచేసి కొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి.",
        "name_label": "మీ పేరు ఏమిటి?",
        "age_label": "దయచేసి మీ వయస్సును నమోదు చేయండి:",
        "gender_label": "మీ లింగం ఏమిటి?",
        "gender_options": ["పురుషుడు", "స్త్రీ", "ఇతర"],
        "symptoms_label": "మీ లక్షణాలను వివరించండి (ఏదైనా భాషలో):",
        "submit_button": "సమర్పించు",
        "warning_fill_fields": "తొడగడానికి, దయచేసి మీ పేరు మరియు లక్షణాలను నమోదు చేయండి.",
        "thinking": "ఆలోచిస్తున్నాను...",
        "detected_symptoms": "✅ కనుగొన్న లక్షణాలు: {}",
        "error_no_symptoms": "❌ క్షమించండి, నేను సరైన లక్షణాలను కనుగొనలేకపోయాను. దయచేసి మరింత సమాచారంతో మళ్ళీ ప్రయత్నించండి.",
        "guided_questions_header": "🤔 మార్గదర్శక ప్రశ్నలు",
        "guided_info": "మీరు ఇచ్చిన లక్షణాల ఆధారంగా, మీకు **{}** ఉండవచ్చు (విశ్వసనీయత: {}%).",
        "guided_prompt": "మరింత ఖచ్చితమైన నిర్ధారణ కోసం, దయచేసి ఈ పరిస్థితికి సంబంధించిన మరికొన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి.",
        "guided_symptom_prompt": "మీకు **{}** కూడా ఉందా?",
        "guided_button": "చివరి నిర్ధారణ పొందండి",
        "no_more_questions": "అడగడానికి ఇంకా ప్రశ్నలు లేవు. మీ చివరి నిర్ధారణ కోసం కింద క్లిక్ చేయండి.",
        "result_header": "✨ నిర్ధారణ ఫలితం",
        "diagnosis_sub": "🩺 మీ సమాధానాల ఆధారంగా, మీకు **{}** ఉండవచ్చు",
        "confidence_label": "విశ్వసనీయత స్థాయి",
        "about_sub": "📖 గురించి",
        "precautions_sub": "🛡️ సూచించిన జాగ్రత్తలు",
        "no_description": "వివరణ అందుబాటులో లేదు.",
        "start_over": "మళ్ళీ ప్రారంభించు",
        "thank_you": "చాట్‌బాట్‌ను ఉపయోగించినందుకు ధన్యవాదాలు. మీకు మంచి ఆరోగ్యం ఉండాలని కోరుకుంటున్నాను, **{}**!",
        "login_header": "లాగిన్",
        "username_label": "వినియోగదారు పేరు",
        "password_label": "పాస్వర్డ్",
        "login_button": "లాగిన్",
        "login_error": "తప్పుడు వినియోగదారు పేరు లేదా పాస్‌వర్డ్. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "logout_button": "నిష్క్రమించు",
        "play_audio": "🔊 నిర్ధారణ వినండి",
    },
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
        # Corrected file paths
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
        # Corrected file path
        with open('MasterData/symptom_Description.csv') as csv_file:
            for row in csv.reader(csv_file):
                if len(row) > 1:
                    description_list[row[0]] = row[1]
    except FileNotFoundError:
        st.warning("Warning: symptom_Description.csv not found.")
    try:
        # Corrected file path
        with open('MasterData/Symptom_severity.csv') as csv_file:
            for row in csv.reader(csv_file):
                if len(row) > 1:
                    try:
                        severity_dict[row[0]] = int(row[1])
                    except ValueError:
                        pass
    except FileNotFoundError:
        st.warning("Warning: Symptom_severity.csv not found.")
    try:
        # Corrected file path
        with open('MasterData/symptom_precaution.csv') as csv_file:
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
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

@st.cache_resource
def train_model(x_train, y_train):
    """Trains the Random Forest model."""
    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(x_train, y_train)
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
    """
    Calls the Gemini API to get a translation.
    Uses a custom JSON schema to get a structured response.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "translated_text": {"type": "STRING"}
                }
            }
        },
    }
    # Replace with your actual key
    apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={apiKey}"
    try:
        response = requests.post(apiUrl, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
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
    """Translates text to English for symptom extraction."""
    if not text:
        return ""
    prompt = f"Translate the following text to English and provide only the translated text in a JSON format with the key 'translated_text': '{text}'"
    return call_gemini_api(prompt)

@st.cache_data(show_spinner=False)
def translate_from_english(text, target_lang):
    """Translates text from English to the target language for output display."""
    if not text or target_lang == "en":
        return text
    prompt = f"Translate the following text to {target_lang} and provide only the translated text in a JSON format with the key 'translated_text': '{text}'"
    return call_gemini_api(prompt, target_lang)

def extract_symptoms(user_input, all_symptoms):
    """Extracts symptoms from user input using synonyms, exact, and fuzzy matching."""
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
        close = get_close_matches(
            word, [s.replace("_", " ") for s in all_symptoms], n=1, cutoff=0.8
        )
        if close:
            for sym in all_symptoms:
                if sym.replace("_", " ") == close[0]:
                    extracted.append(sym)
    return list(set(extracted))

def predict_disease(symptoms_list):
    """Predicts a disease based on a list of symptoms."""
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
    """Calls the Gemini API to get a TTS response."""
    voice_name = TTS_VOICES.get(lang_code, "Kore")
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            },
        },
    }
    apiKey = "AIzaSyDkqVld6HrzudICqVjgw7Q79S8SBSNLn1s"
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={apiKey}"
    try:
        response = requests.post(apiUrl, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        audio_data = result['candidates'][0]['content']['parts'][0]['inlineData']['data']
        return base64.b64decode(audio_data)
    except requests.exceptions.RequestException as e:
        st.error(f"TTS network error: {e}")
        return None
    except KeyError:
        st.error("TTS API returned an unexpected response.")
        return None

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="HealthCare Chatbot", page_icon="🩺")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "name" not in st.session_state:
    st.session_state.name = ""
if "symptoms_list" not in st.session_state:
    st.session_state.symptoms_list = []
if "initial_prediction" not in st.session_state:
    st.session_state.initial_prediction = None
if "final_prediction" not in st.session_state:
    st.session_state.final_prediction = None
if "guided_symptoms" not in st.session_state:
    st.session_state.guided_symptoms = []
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Language selection
st.sidebar.title("Language")
selected_lang_name = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
st.session_state.lang = LANGUAGES[selected_lang_name]

# Get current UI text
lang_texts = UI_TEXT.get(st.session_state.lang, UI_TEXT["en"])

# Login Page
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>HealthCare Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Login</h3>", unsafe_allow_html=True)
    
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username == "admin" and password == "password":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

# Main Chatbot Pages (visible only after login)
else:
    st.title(lang_texts["title"])
    st.markdown(lang_texts["intro"])
    
    # Logout button in the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.page == "home":
        with st.form(key="user_info_form"):
            st.session_state.name = st.text_input(lang_texts["name_label"])
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
                        disease_symptoms = list(training[training['prognosis'] == initial_disease].iloc[0][:-1].index[
                            training[training['prognosis'] == initial_disease].iloc[0][:-1] == 1])
                        st.session_state.guided_symptoms = [
                            sym for sym in disease_symptoms if sym not in st.session_state.symptoms_list
                        ][:8]
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
                full_text += f" {lang_texts['precautions_sub']}: " + " ".join(
                    translate_from_english(p, st.session_state.lang) for p in precautionDictionary[disease]
                )
            
            audio_bytes = call_tts_api(full_text, st.session_state.lang)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")

        st.info("💡 " + random.choice([
            "🌸 Health is wealth, take care of yourself.",
            "💪 A healthy outside starts from the inside.",
            "☀️ Every day is a chance to get stronger and healthier.",
            "🌿 Take a deep breath, your health matters the most.",
            "🌺 Remember, self-care is not selfish.",
        ]))
        
        st.markdown(lang_texts["thank_you"].format(st.session_state.name))
        
        if st.button(lang_texts["start_over"]):
            st.session_state.clear()
            st.rerun()