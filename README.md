AI-Driven Public Health Disease Awareness: Project Overview
1. Introduction
This document provides a detailed overview of an AI-driven public health application designed to raise disease awareness and provide preliminary diagnostic insights. The system leverages machine learning for disease classification, a conversational AI for a user-friendly voice interface, and a robust data management system to track and present diagnostic history.

2. Core Features and Functionality
2.1. Disease Classification and Insights
Symptom-Based Diagnosis: The system will use a Random Forest Classifier model to predict potential diseases based on user-provided symptoms.

Comprehensive Information: For each classified disease, the application will provide a detailed description, a list of precautionary measures, and the confidence level (accuracy) of the model's prediction.

2.2. Conversational Voice Assistant
Intuitive Interface: Powered by the Google Gemini API, the voice assistant will allow users to describe their symptoms naturally, making the process accessible and conversational.

Multilingual Support: The system will be capable of understanding and responding to users in multiple native languages, ensuring broad accessibility and inclusivity.

2.3. User Data and History Management
Personalized Dashboard: A personalized dashboard will be available for each user, providing a complete history of their past diagnoses.





Diagnosis History: The dashboard will maintain a log of symptoms entered, diseases classified, and the date of each interaction, offering a private health record.

2.4. Documentation and Reporting
PDF Generation: The application will enable users to generate and download a PDF report of their diagnosis details. This feature allows for easy sharing with healthcare professionals or for personal record-keeping.

3. Technology Stack
Frontend: Streamlit will be used to create an interactive and user-friendly web interface for the application. Its rapid development capabilities are ideal for building a dynamic dashboard and input forms.

Backend & Database: Python will serve as the backend language, with SQLite used as the lightweight database. SQLite will store user diagnosis history and other relevant data, providing a persistent and reliable storage solution.

Machine Learning: Key Python libraries, including NumPy for numerical operations, Pandas for data manipulation, and Scikit-learn for model building, will be used to train and implement the Random Forest Classifier.

Conversational AI: The Google Gemini API will power the voice assistant, handling natural language processing (NLP) and speech-to-text/text-to-speech conversions for the multilingual system.

4. User Interaction Flow
User Onboarding: A user accesses the Streamlit application and is greeted by the voice assistant.

Symptom Input: The user describes their symptoms in their native language through the voice assistant.

Disease Classification: The spoken symptoms are processed, and the Random Forest model analyzes the input to predict a likely disease.

Information Display: The application displays the disease's name, a detailed description, a list of precautions, and the model's accuracy.

History & Reporting: The diagnosis details are saved to the user's dashboard in the SQLite database. From the dashboard, the user can review past diagnoses or generate a PDF report.

5. Data and Model
The Random Forest Classifier model will be trained on a dataset of symptoms and corresponding diseases. The model's accuracy will be a key metric, which will be displayed to the user as part of the diagnosis results.

6. Future Enhancements
Integration with Wearables: Incorporate data from wearables (e.g., smartwatches) to provide more accurate and personalized health insights.

Telemedicine Integration: Add the ability for users to connect directly with a healthcare professional after a diagnosis.

Real-time Public Health Alerts: Use the system to push real-time alerts about local disease outbreaks or public health advisories.

<img width="1869" height="760" alt="Screenshot 2025-09-13 084013" src="https://github.com/user-attachments/assets/a7b1a354-4b49-41e0-a9b8-f99389302e8e" />
<img width="1865" height="763" alt="Screenshot 2025-09-13 084030" src="https://github.com/user-attachments/assets/523b41b2-6c14-4ac6-b473-8512d77be6df" />
<img width="1755" height="802" alt="Screenshot 2025-09-13 084116" src="https://github.com/user-attachments/assets/423ac583-8c35-48e2-84e8-cc3802ec9e54" />
<img width="1659" height="661" alt="Screenshot 2025-09-13 084126" src="https://github.com/user-attachments/assets/7f1b8142-47b5-48c5-bc94-9784624ef61c" />
<img width="1729" height="781" alt="Screenshot 2025-09-13 084137" src="https://github.com/user-attachments/assets/c030c60f-ccf8-43a1-a339-12d3eb75d01c" />
<img width="1728" height="768" alt="Screenshot 2025-09-13 084337" src="https://github.com/user-attachments/assets/418f5e30-e01a-43a2-a624-80a005f22b7f" />
<img width="1751" height="736" alt="Screenshot 2025-09-13 084359" src="https://github.com/user-attachments/assets/d38687b8-73ed-4f3f-a954-18180a5f470a" />
<img width="1734" height="789" alt="Screenshot 2025-09-13 084428" src="https://github.com/user-attachments/assets/fb1af0da-210a-4e69-af1c-984266018ff3" />
<img width="1184" height="723" alt="Screenshot 2025-09-13 084515" src="https://github.com/user-attachments/assets/13ecc67e-00fa-42be-ae0f-c22af16afbf2" />
<img width="1170" height="576" alt="Screenshot 2025-09-13 084528" src="https://github.com/user-attachments/assets/70de627e-4eb3-4ecf-b0f0-6c1307300f17" />
<img width="1741" height="712" alt="Screenshot 2025-09-13 084549" src="https://github.com/user-attachments/assets/e92e368b-9fc7-45b4-9cc3-73ff1600e9ac" />










