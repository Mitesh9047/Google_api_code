import json
import re
import random
from typing import List, Dict, Any, Tuple

class MedicalExpertSystem:
    def __init__(self, knowledge_base_file: str):
        # Load the original knowledge base
        with open(knowledge_base_file, 'r') as file:
            self.knowledge_base = json.load(file)

        # Extend the knowledge base with new fields
        self._extend_knowledge_base()
        
        # Build the symptom index from the knowledge base
        self.symptom_to_diseases = self._build_symptom_index()
        self.disease_symptoms = {disease: set(details['symptoms']) for disease, details in self.knowledge_base.items()}

    def _extend_knowledge_base(self) -> None:
        """Add medical specialists, parameters, and self-care steps to the knowledge base."""
        # Define specialists for each disease type (already in your code)
        specialists_map = {
            "Flu": "General Practitioner, Infectious Disease Specialist",
            "Common Cold": "General Practitioner",
            "Pneumonia": "Pulmonologist, Infectious Disease Specialist",
            "Dengue": "Infectious Disease Specialist",
            "COVID-19": "Infectious Disease Specialist, Pulmonologist",
            "Heart Disease": "Cardiologist",
            "Diabetes": "Endocrinologist",
            "Migraine": "Neurologist",
            "Asthma": "Pulmonologist, Allergist",
            "Gastroenteritis": "Gastroenterologist",
            "Tuberculosis": "Pulmonologist, Infectious Disease Specialist",
            "Malaria": "Infectious Disease Specialist",
            "Typhoid": "Infectious Disease Specialist",
            "Hypertension": "Cardiologist, Nephrologist",
            "Anemia": "Hematologist",
            "Arthritis": "Rheumatologist, Orthopedic Specialist",
            "Stroke": "Neurologist, Neurosurgeon",
            "Alzheimer's Disease": "Neurologist, Geriatrician",
            "Parkinson's Disease": "Neurologist",
            "Hepatitis": "Hepatologist, Gastroenterologist",
            "Epilepsy": "Neurologist",
            "Depression": "Psychiatrist, Psychologist",
            "Schizophrenia": "Psychiatrist"
        }
        
        # Define medical parameters to check for each disease (already in your code)
        parameters_map = {
            "Heart Disease": [
                {"name": "blood_pressure", "question": "What is your blood pressure? (e.g., 120/80 mmHg)", 
                 "normal_range": "120/80 mmHg", "abnormal": ["≥140/90 mmHg (high)", "≤90/60 mmHg (low)"]},
                {"name": "cholesterol", "question": "What is your total cholesterol level? (e.g., 180 mg/dL)", 
                 "normal_range": "<200 mg/dL", "abnormal": ["≥240 mg/dL (high)"]}
            ],
            "Diabetes": [
                {"name": "blood_glucose_fasting", "question": "What is your fasting blood glucose level? (e.g., 95 mg/dL)", 
                 "normal_range": "<100 mg/dL", "abnormal": ["100-125 mg/dL (pre-diabetic)", "≥126 mg/dL (diabetic)"]},
                {"name": "hba1c", "question": "What is your HbA1c percentage? (e.g., 5.5%)", 
                 "normal_range": "<5.7%", "abnormal": ["5.7-6.4% (pre-diabetic)", "≥6.5% (diabetic)"]}
            ],
            "Hypertension": [
                {"name": "blood_pressure", "question": "What is your blood pressure? (e.g., 120/80 mmHg)", 
                 "normal_range": "120/80 mmHg", "abnormal": ["≥140/90 mmHg (high)", "≤90/60 mmHg (low)"]}
            ],
            "Anemia": [
                {"name": "hemoglobin", "question": "What is your hemoglobin level? (e.g., 14 g/dL)", 
                 "normal_range": "Male: 13.5-17.5 g/dL, Female: 12.0-15.5 g/dL", 
                 "abnormal": ["Male: <13.5 g/dL (low)", "Female: <12.0 g/dL (low)"]}
            ],
            "Pneumonia": [
                {"name": "oxygen_saturation", "question": "What is your oxygen saturation level? (e.g., 97%)", 
                 "normal_range": "95-100%", "abnormal": ["<95% (low)"]},
                {"name": "respiratory_rate", "question": "What is your respiratory rate? (breaths per minute)", 
                 "normal_range": "12-20 breaths/min", "abnormal": [">20 breaths/min (high)"]}
            ],
            "COVID-19": [
                {"name": "oxygen_saturation", "question": "What is your oxygen saturation level? (e.g., 97%)", 
                 "normal_range": "95-100%", "abnormal": ["<95% (low)"]},
                {"name": "temperature", "question": "What is your body temperature? (e.g., 37°C or 98.6°F)", 
                 "normal_range": "36.1-37.2°C (97-99°F)", "abnormal": ["≥38°C/100.4°F (high)"]}
            ],
            "Hepatitis": [
                {"name": "liver_enzymes", "question": "What are your liver enzyme (ALT/AST) levels?", 
                 "normal_range": "≤35 U/L", "abnormal": [">35 U/L (high)"]},
                {"name": "bilirubin", "question": "What is your total bilirubin level?", 
                 "normal_range": "0.1-1.2 mg/dL", "abnormal": [">1.2 mg/dL (high)"]}
            ]
        }
        
        # Define default medical parameters for known conditions without specific parameters
        default_parameters = [
            {"name": "temperature", "question": "What is your body temperature? (e.g., 37°C or 98.6°F)", 
             "normal_range": "36.1-37.2°C (97-99°F)", "abnormal": ["≥38°C/100.4°F (high)"]},
            {"name": "blood_pressure", "question": "What is your blood pressure? (e.g., 120/80 mmHg)", 
             "normal_range": "120/80 mmHg", "abnormal": ["≥140/90 mmHg (high)", "≤90/60 mmHg (low)"]}
        ]
        
        # NEW: Define self-care steps for each disease
        self_care_steps_map = {
            "Flu": [
                "Rest and get plenty of sleep to help your body fight the infection",
                "Stay hydrated by drinking water, clear broths, or warm lemon water with honey",
                "Take over-the-counter pain relievers like acetaminophen or ibuprofen to reduce fever and aches",
                "Use a humidifier to add moisture to the air and ease congestion",
                "Avoid contact with others to prevent spreading the infection"
            ],
            "Common Cold": [
                "Rest to help your body recover faster",
                "Stay hydrated with water, juice, clear broth, or warm lemon water with honey",
                "Use saline nasal drops or sprays to relieve nasal congestion",
                "Gargle with saltwater to soothe a sore throat",
                "Use over-the-counter cold medications to relieve symptoms"
            ],
            "Pneumonia": [
                "Follow your doctor's prescribed treatment plan carefully",
                "Get plenty of rest to help your body recover",
                "Stay hydrated by drinking fluids, especially water",
                "Take all prescribed antibiotics exactly as directed, even if you start feeling better",
                "Use a humidifier to ease breathing and loosen mucus",
                "Don't smoke and avoid secondhand smoke and other lung irritants"
            ],
            "Dengue": [
                "Rest as much as possible",
                "Stay hydrated by drinking plenty of clean water or drinks with electrolytes",
                "Take acetaminophen (paracetamol) to reduce fever and pain (avoid aspirin and NSAIDs)",
                "Seek immediate medical attention if you develop severe abdominal pain, persistent vomiting, bleeding, or difficulty breathing",
                "Use mosquito repellent and nets to prevent spreading to others through mosquitoes"
            ],
            "COVID-19": [
                "Isolate yourself from others, including household members, to prevent spread",
                "Rest and stay hydrated",
                "Monitor your symptoms and oxygen levels with a pulse oximeter if available",
                "Take over-the-counter medications like acetaminophen to reduce fever and discomfort",
                "Sleep on your stomach (prone position) to improve oxygenation if breathing is difficult",
                "Seek emergency care if you experience severe symptoms like trouble breathing or persistent chest pain"
            ],
            "Heart Disease": [
                "Take all medications exactly as prescribed by your doctor",
                "Follow a heart-healthy diet low in saturated fat, trans fat, sodium, and added sugars",
                "Exercise regularly as advised by your healthcare provider",
                "Quit smoking and avoid secondhand smoke",
                "Manage stress through relaxation techniques like meditation or yoga",
                "Monitor and control your blood pressure and cholesterol",
                "Keep all follow-up appointments with your healthcare providers"
            ],
            "Diabetes": [
                "Monitor your blood sugar levels regularly",
                "Take medications or insulin as prescribed",
                "Follow a balanced diet with consistent carbohydrate intake",
                "Limit refined sugars and processed foods",
                "Exercise regularly to help control blood glucose levels",
                "Inspect your feet daily for cuts, blisters, or signs of infection",
                "Manage stress as it can affect blood sugar levels"
            ],
            "Migraine": [
                "Rest in a quiet, dark room during an attack",
                "Apply cold or hot compresses to your head or neck",
                "Practice relaxation techniques like meditation or deep breathing",
                "Maintain a regular sleep schedule",
                "Keep a migraine diary to identify and avoid triggers",
                "Stay hydrated and don't skip meals",
                "Use medications as prescribed by your doctor"
            ],
            "Asthma": [
                "Take medications as prescribed, even when you feel well",
                "Use your inhaler correctly (ask your doctor for technique guidance)",
                "Identify and avoid your asthma triggers",
                "Create an asthma action plan with your doctor",
                "Monitor your breathing and peak flow readings",
                "Keep your living environment clean and free of dust, mold, and pet dander",
                "Get vaccinated against influenza and pneumonia"
            ],
            "Gastroenteritis": [
                "Stay hydrated with small, frequent sips of water or clear fluids",
                "Try oral rehydration solutions to replace lost electrolytes",
                "Gradually reintroduce bland, easy-to-digest foods like toast, rice, and bananas",
                "Avoid dairy products, caffeine, alcohol, and fatty or spicy foods until recovery",
                "Rest to help your body fight the infection",
                "Avoid anti-diarrheal medications unless prescribed by your doctor"
            ],
            "Tuberculosis": [
                "Take all medications exactly as prescribed for the full course (often 6-9 months)",
                "Keep all doctor appointments for follow-up testing",
                "Ensure good ventilation in your living spaces",
                "Cover your mouth when coughing or sneezing and dispose of tissues properly",
                "Wear a mask when around others until your doctor says you're no longer contagious",
                "Eat a nutritious diet high in protein to support healing"
            ],
            "Malaria": [
                "Complete the full course of prescribed antimalarial medications",
                "Rest and stay hydrated",
                "Take acetaminophen (paracetamol) to reduce fever and pain",
                "Use insecticide-treated bed nets while sleeping",
                "Wear long-sleeved clothing and use insect repellent to prevent reinfection",
                "Follow up with your healthcare provider as directed"
            ],
            "Typhoid": [
                "Take antibiotics exactly as prescribed for the full course",
                "Rest and stay hydrated",
                "Eat small, frequent meals that are easy to digest",
                "Practice meticulous hand hygiene, especially after using the bathroom",
                "Avoid preparing food for others until your doctor confirms you're no longer contagious",
                "Follow up with your healthcare provider to ensure the infection is cleared"
            ],
            "Hypertension": [
                "Take blood pressure medications as prescribed",
                "Follow a low-sodium (low-salt) diet",
                "Maintain a healthy weight or lose weight if overweight",
                "Exercise regularly, aiming for at least 30 minutes most days",
                "Limit alcohol consumption",
                "Reduce stress through relaxation techniques",
                "Monitor your blood pressure at home regularly"
            ],
            "Anemia": [
                "Take iron supplements or other prescribed medications",
                "Eat iron-rich foods like lean red meat, beans, and leafy green vegetables",
                "Consume vitamin C alongside iron-rich foods to enhance absorption",
                "Avoid coffee, tea, and calcium supplements when taking iron supplements",
                "Get adequate rest and avoid excessive physical exertion until your levels improve",
                "Follow up with your healthcare provider for blood tests to monitor improvement"
            ],
            "Arthritis": [
                "Take medications as prescribed for pain and inflammation",
                "Apply hot or cold packs to affected joints",
                "Perform gentle stretching and range-of-motion exercises",
                "Use assistive devices to reduce strain on joints",
                "Maintain a healthy weight to reduce pressure on joints",
                "Practice good posture and body mechanics",
                "Consider physical therapy for targeted exercises and techniques"
            ],
            "Stroke": [
                "Follow your rehabilitation plan diligently",
                "Take all prescribed medications to prevent another stroke",
                "Attend all therapy sessions (physical, occupational, speech)",
                "Make home modifications for safety if needed",
                "Eat a heart-healthy diet low in saturated fat and sodium",
                "Exercise as recommended by your healthcare team",
                "Manage stress and attend support groups if helpful"
            ],
            "Alzheimer's Disease": [
                "Follow medication schedules carefully",
                "Establish and maintain a routine for daily activities",
                "Use memory aids like calendars, to-do lists, and phone reminders",
                "Stay physically active with appropriate exercises",
                "Engage in mentally stimulating activities like puzzles or reading",
                "Create a safe home environment by removing tripping hazards and installing handrails",
                "Join support groups for both patients and caregivers"
            ],
            "Parkinson's Disease": [
                "Take medications exactly as prescribed, following the schedule carefully",
                "Exercise regularly, focusing on balance, flexibility, and strength",
                "Work with a physical therapist to learn specific beneficial exercises",
                "Make home modifications to prevent falls (remove rugs, install grab bars)",
                "Use assistive devices recommended by your healthcare provider",
                "Join a support group to share experiences and coping strategies",
                "Practice speech exercises if experiencing speech difficulties"
            ],
            "Hepatitis": [
                "Rest adequately to help your liver heal",
                "Avoid alcohol completely",
                "Eat small, balanced meals that include plenty of fruits and vegetables",
                "Stay hydrated with water and clear fluids",
                "Avoid medications that can damage the liver (consult your doctor before taking any medications)",
                "Practice good hygiene to prevent spreading the infection",
                "Attend all follow-up appointments to monitor liver function"
            ],
            "Epilepsy": [
                "Take anti-seizure medications exactly as prescribed",
                "Keep a seizure diary to identify potential triggers",
                "Get adequate sleep and avoid sleep deprivation",
                "Manage stress with relaxation techniques",
                "Avoid alcohol, as it can interact with medications and trigger seizures",
                "Wear medical identification indicating your condition",
                "Inform close friends and family about seizure first aid"
            ],
            "Depression": [
                "Take prescribed antidepressants consistently, even when starting to feel better",
                "Attend all therapy sessions as scheduled",
                "Exercise regularly to boost mood-enhancing chemicals",
                "Maintain a regular sleep schedule",
                "Challenge negative thoughts with more balanced perspectives",
                "Stay connected with supportive friends and family",
                "Avoid alcohol and recreational drugs which can worsen depression"
            ],
            "Schizophrenia": [
                "Take antipsychotic medications exactly as prescribed",
                "Attend all therapy and support group sessions",
                "Establish and maintain a structured daily routine",
                "Learn to recognize early warning signs of relapse",
                "Avoid alcohol and recreational drugs which can worsen symptoms",
                "Get adequate sleep and manage stress effectively",
                "Stay connected with supportive family members and healthcare providers"
            ]
        }
        
        # Add these fields to each disease in the knowledge base
        for disease, details in self.knowledge_base.items():
            # Add specialists (if not already added from the JSON)
            if "specialists" not in details:
                details["specialists"] = specialists_map.get(disease, "General Practitioner")
            
            # Add medical parameters to check (if not already added from the JSON)
            if "medical_parameters" not in details:
                if disease in parameters_map:
                    details["medical_parameters"] = parameters_map[disease]
                else:
                    details["medical_parameters"] = default_parameters.copy()
                    
            # Add self-care steps
            details["self_care_steps"] = self_care_steps_map.get(disease, [
                "Rest and get plenty of sleep",
                "Stay hydrated by drinking plenty of fluids",
                "Take medications as prescribed by your doctor",
                "Follow up with your healthcare provider regularly",
                "Monitor your symptoms and seek immediate care if they worsen"
            ])

    def _build_symptom_index(self) -> Dict[str, List[str]]:
        """Build an index mapping symptoms to diseases."""
        symptom_index = {}
        for disease, details in self.knowledge_base.items():
            for symptom in details['symptoms']:
                symptom_index.setdefault(symptom, []).append(disease)
        return symptom_index

    def preprocess_symptoms(self, user_input: str) -> List[str]:
        """Extract symptoms from user input."""
        processed_input = re.sub(r'[^\w\s]', '', user_input.lower())
        return [symptom for symptom in self.symptom_to_diseases if symptom.lower() in processed_input]

    def forward_chain(self, symptoms: List[str]) -> List[str]:
        """Find possible diseases based on symptoms."""
        possible_diseases = {}
        for symptom in symptoms:
            if symptom in self.symptom_to_diseases:
                for disease in self.symptom_to_diseases[symptom]:
                    possible_diseases[disease] = possible_diseases.get(disease, 0) + 1
        return sorted(possible_diseases, key=possible_diseases.get, reverse=True)

    def backward_chain(self, disease: str, symptoms: List[str]) -> Tuple[bool, float]:
        """Check if symptoms match a specific disease."""
        if disease not in self.knowledge_base:
            return False, 0
        disease_symptoms = set(self.knowledge_base[disease]['symptoms'])
        match_percentage = len(set(symptoms) & disease_symptoms) / len(disease_symptoms) * 100
        return match_percentage >= 60, match_percentage

    def get_more_symptoms(self, current_symptoms: List[str], possible_diseases: List[str]) -> str:
        """Suggest additional symptoms to check."""
        additional_symptoms = set()
        for disease in possible_diseases:
            additional_symptoms.update(set(self.knowledge_base[disease]['symptoms']) - set(current_symptoms))
        return random.choice(list(additional_symptoms)) if additional_symptoms else None

    def get_yes_no_input(self, question: str) -> bool:
        """Get yes/no input from user."""
        while True:
            response = input(f"{question} (yes/no): ").strip().lower()
            if response in ["yes", "y"]:
                return True
            elif response in ["no", "n"]:
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    def get_medical_parameters(self, disease: str) -> Dict[str, Dict[str, Any]]:
        """Collect medical parameters relevant to the potential disease."""
        results = {}
        
        print("\nTo help with the diagnosis, please provide the following medical information if available:")
        print("(Press Enter to skip if information is not available)")
        
        for param in self.knowledge_base[disease]["medical_parameters"]:
            param_name = param["name"]
            value = input(f"{param['question']}: ").strip()
            
            if value:
                results[param_name] = {
                    "value": value,
                    "normal_range": param["normal_range"],
                    "abnormal_ranges": param["abnormal"]
                }
        
        return results

    def analyze_parameters(self, parameters: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Analyze the medical parameters against normal ranges."""
        analysis = {}
        
        for param_name, param_data in parameters.items():
            value = param_data["value"].lower()
            status = "normal"
            
            # Blood pressure analysis
            if param_name == "blood_pressure" and "/" in value:
                try:
                    systolic, diastolic = map(int, re.findall(r'\d+', value)[:2])
                    if systolic >= 140 or diastolic >= 90:
                        status = "high"
                    elif systolic <= 90 or diastolic <= 60:
                        status = "low"
                except (ValueError, IndexError):
                    status = "unanalyzed"
            
            # Numeric value analysis
            elif any(char.isdigit() for char in value):
                numeric_val = float(re.search(r'\d+(\.\d+)?', value).group())
                
                # Blood glucose
                if param_name == "blood_glucose_fasting":
                    if numeric_val >= 126:
                        status = "high (diabetic)"
                    elif numeric_val >= 100:
                        status = "elevated (pre-diabetic)"
                
                # HbA1c
                elif param_name == "hba1c" and "%" in value:
                    if numeric_val >= 6.5:
                        status = "high (diabetic)"
                    elif numeric_val >= 5.7:
                        status = "elevated (pre-diabetic)"
                
                # Oxygen saturation
                elif param_name == "oxygen_saturation" and "%" in value:
                    if numeric_val < 95:
                        status = "low"
                
                # Temperature
                elif param_name == "temperature":
                    if "c" in value or "celsius" in value:
                        if numeric_val >= 38:
                            status = "high (fever)"
                    elif "f" in value or "fahrenheit" in value:
                        if numeric_val >= 100.4:
                            status = "high (fever)"
            
            # Save the analysis result
            analysis[param_name] = status
        
        return analysis

    def diagnose(self, user_input: str) -> Dict[str, Any]:
        """Main diagnostic function to determine possible diseases based on symptoms."""
        # Extract symptoms from user input
        symptoms = self.preprocess_symptoms(user_input)
        if not symptoms:
            return {"status": "error", "message": "No recognizable symptoms detected. Please describe your symptoms more clearly."}

        # Identify possible diseases
        possible_diseases = self.forward_chain(symptoms)
        if not possible_diseases:
            return {"status": "error", "message": "Could not identify any potential diseases based on the symptoms."}

        # Check for matches with all possible diseases
        confirmed_diseases = []
        match_percentages = {}
        
        for disease in possible_diseases:
            is_match, percentage = self.backward_chain(disease, symptoms)
            match_percentages[disease] = percentage
            if is_match:
                confirmed_diseases.append(disease)

        # If we have a potential match
        if confirmed_diseases:
            primary_disease = confirmed_diseases[0]
            
            # Collect additional medical information for this disease
            parameters = self.get_medical_parameters(primary_disease)
            parameter_analysis = self.analyze_parameters(parameters)
            
            return {
                "status": "diagnosed",
                "disease": primary_disease,
                "match_percentage": match_percentages[primary_disease],
                "summary": self.knowledge_base[primary_disease]['summary'],
                "prognosis": self.knowledge_base[primary_disease]['prognosis'],
                "specialists": self.knowledge_base[primary_disease]['specialists'],
                "current_symptoms": symptoms,
                "parameters": parameters,
                "parameter_analysis": parameter_analysis,
                "self_care_steps": self.knowledge_base[primary_disease]['self_care_steps']  # Include self-care steps in the diagnosis result
            }

        # If no clear match, continue gathering symptoms
        while possible_diseases:
            follow_up_symptom = self.get_more_symptoms(symptoms, possible_diseases)
            if not follow_up_symptom:
                break

            if self.get_yes_no_input(f"Do you also have {follow_up_symptom}?"):
                symptoms.append(follow_up_symptom)
                possible_diseases = self.forward_chain(symptoms)
            else:
                possible_diseases = [d for d in possible_diseases if follow_up_symptom not in self.knowledge_base[d]['symptoms']]

            # Recalculate matches
            confirmed_diseases = []
            match_percentages = {}
            for disease in possible_diseases:
                is_match, percentage = self.backward_chain(disease, symptoms)
                match_percentages[disease] = percentage
                if is_match:
                    confirmed_diseases.append(disease)
            
            # If we found a match after more symptoms
            if confirmed_diseases:
                primary_disease = confirmed_diseases[0]
                
                # Collect additional medical information
                parameters = self.get_medical_parameters(primary_disease)
                parameter_analysis = self.analyze_parameters(parameters)
                
                return {
                    "status": "diagnosed",
                    "disease": primary_disease,
                    "match_percentage": match_percentages[primary_disease],
                    "summary": self.knowledge_base[primary_disease]['summary'],
                    "prognosis": self.knowledge_base[primary_disease]['prognosis'],
                    "specialists": self.knowledge_base[primary_disease]['specialists'],
                    "current_symptoms": symptoms,
                    "parameters": parameters,
                    "parameter_analysis": parameter_analysis,
                    "self_care_steps": self.knowledge_base[primary_disease]['self_care_steps']  # Include self-care steps in the diagnosis result
                }

        # If we get here, we couldn't make a definitive diagnosis
        top_diseases = sorted(match_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        return {
            "status": "suggestions", 
            "diseases": [d[0] for d in top_diseases],
            "match_percentages": {d[0]: d[1] for d in top_diseases},
            "current_symptoms": symptoms,
            # Include potential self-care steps for the top disease as general advice
            "general_self_care": self.knowledge_base[top_diseases[0][0]]['self_care_steps'] if top_diseases else []
        }

    def save_extended_knowledge_base(self, output_file: str) -> None:
        """Save the extended knowledge base to a new file."""
        with open(output_file, 'w') as file:
            json.dump(self.knowledge_base, file, indent=4)

def main():
    expert_system = MedicalExpertSystem('medical_knowledge_base.json')
    
    # Optionally save the extended knowledge base
    # expert_system.save_extended_knowledge_base('extended_medical_knowledge_base.json')
    
    print("=" * 60)
    print("Medical Expert System - Preliminary Diagnosis")
    print("=" * 60)
    print("\nDISCLAIMER: This system provides preliminary information only.")
    print("Results are not foolproof and should not replace professional medical advice.")
    print("Always consult with a qualified healthcare provider for proper diagnosis and treatment.")
    print("\nDescribe your symptoms (or type 'exit' to quit)")

    while True:
        user_input = input("\nEnter your symptoms: ")
        if user_input.lower() == 'exit':
            break

        diagnosis = expert_system.diagnose(user_input)
        
        if diagnosis['status'] == 'diagnosed':
            match_percentage = diagnosis.get('match_percentage', 0)
            print("\n" + "=" * 60)
            print(f"Preliminary Diagnosis: {diagnosis['disease']}")
            print(f"Confidence: {match_percentage:.1f}%")
            print("=" * 60)
            
            print(f"\nSymptoms Matched: {', '.join(diagnosis['current_symptoms'])}")
            
            # Display medical parameters if provided
            if diagnosis.get('parameters'):
                print("\nMedical Parameters:")
                for param_name, param_data in diagnosis['parameters'].items():
                    status = diagnosis.get('parameter_analysis', {}).get(param_name, "")
                    status_info = f" ({status})" if status else ""
                    print(f"- {param_name.replace('_', ' ').title()}: {param_data['value']}{status_info}")
                    print(f"  Normal Range: {param_data['normal_range']}")
            
            print(f"\nSummary: {diagnosis['summary']}")
            print(f"\nPrognosis: {diagnosis['prognosis']}")
            
            print(f"\nRecommended Specialists: {diagnosis['specialists']}")
            
            # Display self-care steps
            if diagnosis.get('self_care_steps'):
                print("\nRecommended Self-Care Steps:")
                for i, step in enumerate(diagnosis['self_care_steps'], 1):
                    print(f"{i}. {step}")
            
            # Add strong disclaimer for low confidence
            if match_percentage < 75:
                print("\nCAUTION: This is a low-confidence diagnosis based on limited information.")
            
            print("\nREMINDER: This assessment is preliminary.")
            print("Please consult with a medical professional for proper diagnosis and treatment.")
            
        elif diagnosis['status'] == 'suggestions':
            print("\n" + "=" * 60)
            print("Could not conclusively diagnose. Possible conditions:")
            print("=" * 60)
            
            for disease in diagnosis['diseases']:
                match_pct = diagnosis['match_percentages'][disease]
                print(f"- {disease} (Match: {match_pct:.1f}%)")
                print(f"  Summary: {expert_system.knowledge_base[disease]['summary']}")
                print(f"  Recommended Specialists: {expert_system.knowledge_base[disease]['specialists']}")
                print()
            
            # Display general self-care advice
            if diagnosis.get('general_self_care'):
                print("\nGeneral Self-Care Recommendations:")
                for i, step in enumerate(diagnosis['general_self_care'], 1):
                    print(f"{i}. {step}")
            
            print("\nIMPORTANT These are only possibilities based on the symptoms provided.")
            print("The system could not find a strong match. Please consult with a healthcare provider.")
          
        else:
            print("\n" + "=" * 60)
            print("Diagnostic Error")
            print("=" * 60)
            print(diagnosis['message'])
            print("\nPlease try describing your symptoms differently or consult with a healthcare provider.")

if __name__ == "__main__":
    main()
   