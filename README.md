# GraniteCare AI - AI Agent for Chronic Disease Monitoring
### Solution for Problem Statement No. 27 (IBM Cloud Lite & IBM Granite)

**GraniteCare AI** is an end-to-end intelligent assistant for proactive chronic disease management (Type 1 & 2 Diabetes, Stage 2 Hypertension, and Congestive Heart Failure). It continuously ingests and analyzes wearable biometrics (Continuous Glucose Monitors, Smartwatch ECG/HRV/Pulse Oximetry, and Connected Blood Pressure Cuffs) alongside electronic health records (EHR) and patient symptom reporting to detect early warning signs, prevent hospital readmissions, and assist clinicians with standardized documentation.

---

## 🌟 Key Features

1. **Continuous Wearable Telemetry Ingestion & Simulation**:
   - Real-time biometric streaming across key chronic biomarkers:
     - **Continuous Glucose (CGM)**: Glycemic variability, hypoglycemia (< 70 mg/dL, < 54 mg/dL), and severe hyperglycemia (> 280 mg/dL).
     - **Blood Pressure & MAP**: Systolic/Diastolic tracking, Mean Arterial Pressure, Stage 2 Hypertension, and Hypertensive Urgency/Crisis (> 180/120 mmHg).
     - **Cardiopulmonary Parameters**: Resting Heart Rate (Tachycardia / Bradycardia), Pulse Oximetry ($SpO_2$), and rapid dry weight gain / fluid retention.
   - Interactive Testing Sandbox with one-click crisis scenarios:
     - `Controlled Baseline` (Stable parameters)
     - `Acute Hypoglycemia` (Glucose 52 mg/dL, adrenergic tachycardia)
     - `Hypertensive Urgency` (BP 186/118 mmHg)
     - `Heart Failure Decompensation` ($SpO_2$ 87%, fluid retention +3.8 lbs)
     - `Postprandial Glucose Spike` (Glucose 238 mg/dL)
     - Live fine-grained telemetry adjustment sliders and automated 6-second wearable pulse stream.

2. **IBM Granite Foundation Model Intelligence (`ibm/granite-3-8b-instruct`)**:
   - **Personalized Clinical Insights**: Translates raw wearable telemetry and EHR baselines into compassionate, patient-friendly guidance on lifestyle, hydration, nutrition (DASH / low-GI), and immediate recovery actions.
   - **Automated Physician SBAR Notes**: Generates formal clinical notes adhering to the medical **SBAR** format (*Situation, Background, Assessment, Recommendation*) for instant physician review and EHR charting.
   - **Conversational Health Copilot**: Natural language symptom checking, meal planning advice, and medication guidance with clinical guardrails.
   - **Dual Execution Engine**: Connects directly to live IBM Cloud watsonx.ai via `ibm_watsonx_ai` SDK, with a seamless High-Fidelity Granite Clinical Fallback mode for offline hackathon judging.

3. **Clinician / Provider Triage Board**:
   - Population health dashboard sorting patients by multi-variate composite risk score (🔴 Critical, 🟡 Warning, 🟢 Stable).
   - 24-hour longitudinal telemetry trend charts (Chart.js) showing glycemic curves within target therapeutic bounds and hemodynamic shifts.
   - One-click SBAR generation with direct EHR copy functionality.

4. **Medication Adherence & Schedule Assistant**:
   - Multi-dose scheduling (Morning, Afternoon, Bedtime).
   - Real-time dose check-offs and 30-day compliance tracking that directly impacts the clinical risk scoring algorithm.

---

## ☁️ Mandatory IBM Cloud Lite Integration

| Service Component | IBM Cloud Lite Service | Role & Function in GraniteCare AI |
|---|---|---|
| **Foundation Models** | **IBM watsonx.ai** | Hosts `ibm/granite-3-8b-instruct` / `granite-13b-chat-v2` for reasoning, early-warning explanations, lifestyle coaching, and SBAR generation. |
| **NoSQL Database** | **IBM Cloudant (Lite Tier)** | Stores JSON documents for patient EHR baselines, time-series telemetry buckets, and alert history. Live export endpoint: `/api/export/cloudant`. |
| **Object Storage** | **IBM Cloud Object Storage (COS)** | S3-compatible cold storage for long-term continuous wearable logs, raw sensor time-series, and smartwatch ECG recordings. |
| **Microservice Runtime** | **IBM Code Engine / Cloud Foundry** | Serverless container runtime providing auto-scaling from zero for the Python/Flask API and telemetry ingestion engine. |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14.6)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Launch the Application
Simply double-click `run.bat` (on Windows) or execute:

```bash
cd C:\Users\HP\.gemini\antigravity\scratch\chronic-care-ai
python app.py
```

Open your browser to:
- **Patient Companion Portal**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Clinician Triage Board**: [http://127.0.0.1:5000/doctor](http://127.0.0.1:5000/doctor)
- **IBM Cloud Architecture Blueprint**: [http://127.0.0.1:5000/architecture](http://127.0.0.1:5000/architecture)
- **Cloudant NoSQL Schema Export**: [http://127.0.0.1:5000/api/export/cloudant](http://127.0.0.1:5000/api/export/cloudant)

### 3. (Optional) Configure Live IBM watsonx.ai Credentials
Click the **⚙️ Settings** icon in the navigation bar to enter your IBM Cloud credentials:
- **API Key**:
- **Project ID**: 
- **watsonx URL**: `https://us-south.ml.cloud.ibm.com`
- **Granite Model**: `ibm/granite-3-8b-instruct`

*Note: The application functions out-of-the-box with High-Fidelity IBM Granite Clinical Simulation if cloud credentials are not yet supplied.*

---

## 🧪 Testing & Verification

Run the automated test suite verifying risk algorithms, early warning triggers, and API routes:

```bash
python -m unittest discover tests
```

Expected result: 10 tests passed (`OK`).
