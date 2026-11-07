"""Flask Web Application & API Server for AI Agent for Chronic Disease Monitoring.
Powered by IBM Granite & IBM Cloud Lite Services.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from config import Config
from services import db, RiskAnalyzer, granite_agent, TelemetryStreamer

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# ----------------- Page Routes -----------------

@app.route("/")
def index():
    """Patient companion web application."""
    patients = db.get_all_patients()
    default_patient = patients[0] if patients else None
    return render_template(
        "index.html",
        patients=patients,
        current_patient=default_patient,
        granite_status=granite_agent.get_status()
    )

@app.route("/doctor")
def doctor():
    """Clinician / Healthcare Provider Triage & Longitudinal Portal."""
    patients = db.get_all_patients()
    # Enrich patients with risk evaluation
    enriched = []
    for p in patients:
        risk = RiskAnalyzer.calculate_risk(p, p["current_vitals"])
        enriched.append({**p, "risk": risk})
    
    # Sort by risk score descending (critical first)
    enriched.sort(key=lambda x: x["risk"]["score"], reverse=True)
    return render_template(
        "doctor.html",
        patients=enriched,
        granite_status=granite_agent.get_status()
    )

@app.route("/architecture")
def architecture():
    """IBM Cloud Lite Services & IBM Granite Technical Architecture Blueprint."""
    return render_template(
        "architecture.html",
        granite_status=granite_agent.get_status()
    )

@app.route("/download-zip")
def download_zip():
    """Direct download for project zip archive."""
    import os
    from flask import send_file
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "chronic-care-ai.zip")
    return send_file(zip_path, mimetype="application/zip", as_attachment=True, download_name="chronic-care-ai.zip")

# ----------------- API Endpoints -----------------

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "healthy",
        "service": "Chronic Disease AI Agent",
        "granite": granite_agent.get_status()
    })

@app.route("/api/patients", methods=["GET"])
def api_patients():
    patients = db.get_all_patients()
    result = []
    for p in patients:
        risk = RiskAnalyzer.calculate_risk(p, p["current_vitals"])
        result.append({
            "id": p["id"],
            "name": p["name"],
            "age": p["age"],
            "gender": p["gender"],
            "conditions": p["conditions"],
            "current_vitals": p["current_vitals"],
            "risk": risk
        })
    return jsonify(result)

@app.route("/api/patients/<patient_id>", methods=["GET"])
def api_patient_detail(patient_id):
    patient = db.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    history = db.get_vitals_history(patient_id)
    risk = RiskAnalyzer.calculate_risk(patient, patient["current_vitals"], history=history)
    insight = granite_agent.generate_clinical_insight(patient, patient["current_vitals"], risk)
    alerts = db.get_recent_alerts(patient_id=patient_id, limit=10)

    return jsonify({
        "patient": patient,
        "history": history,
        "risk": risk,
        "insight": insight,
        "alerts": alerts,
        "scenarios": TelemetryStreamer.get_scenarios(),
        "granite_status": granite_agent.get_status()
    })

@app.route("/api/patients/<patient_id>/telemetry", methods=["POST"])
def api_update_telemetry(patient_id):
    data = request.get_json() or {}
    patient = db.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    current = dict(patient["current_vitals"])
    for k in ["glucose", "systolic", "diastolic", "heart_rate", "spo2", "weight_lbs"]:
        if k in data and data[k] is not None:
            try:
                current[k] = float(data[k]) if k in ["glucose", "weight_lbs"] else int(data[k])
            except ValueError:
                pass

    updated_patient = db.update_patient_vitals(patient_id, current)
    history = db.get_vitals_history(patient_id)
    risk = RiskAnalyzer.calculate_risk(updated_patient, updated_patient["current_vitals"], history=history)

    # Log alerts if any triggered
    if risk.get("alerts"):
        db.log_alerts(patient_id, risk["alerts"])

    insight = granite_agent.generate_clinical_insight(updated_patient, updated_patient["current_vitals"], risk)

    return jsonify({
        "success": True,
        "current_vitals": updated_patient["current_vitals"],
        "risk": risk,
        "insight": insight,
        "history": history[-20:]
    })

@app.route("/api/patients/<patient_id>/scenario", methods=["POST"])
def api_inject_scenario(patient_id):
    data = request.get_json() or {}
    scenario_key = data.get("scenario", "STABLE")
    patient = db.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    baseline_wt = patient.get("baseline_ehr", {}).get("weight_lbs", 160.0)
    new_vitals = TelemetryStreamer.apply_scenario(scenario_key, patient["current_vitals"], baseline_wt)
    updated_patient = db.update_patient_vitals(patient_id, new_vitals)

    history = db.get_vitals_history(patient_id)
    risk = RiskAnalyzer.calculate_risk(updated_patient, updated_patient["current_vitals"], history=history)

    if risk.get("alerts"):
        db.log_alerts(patient_id, risk["alerts"])

    insight = granite_agent.generate_clinical_insight(updated_patient, updated_patient["current_vitals"], risk)

    return jsonify({
        "success": True,
        "scenario": scenario_key,
        "current_vitals": updated_patient["current_vitals"],
        "risk": risk,
        "insight": insight,
        "history": history[-20:]
    })

@app.route("/api/patients/<patient_id>/medication/<med_id>/toggle", methods=["POST"])
def api_toggle_medication(patient_id, med_id):
    data = request.get_json() or {}
    slot_index = data.get("slot_index", 0)
    med = db.toggle_medication(patient_id, med_id, slot_index)
    if not med:
        return jsonify({"error": "Medication not found"}), 404
    return jsonify({"success": True, "medication": med})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    patient_id = data.get("patient_id", "P101")
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message required"}), 400

    patient = db.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    db.log_chat(patient_id, "user", message)
    history = db.get_chat_history(patient_id)
    reply = granite_agent.chat(patient, message, patient["current_vitals"], history)
    db.log_chat(patient_id, "assistant", reply)

    return jsonify({
        "reply": reply,
        "patient_id": patient_id,
        "granite_status": granite_agent.get_status()
    })

@app.route("/api/doctor/sbar/<patient_id>", methods=["GET"])
def api_doctor_sbar(patient_id):
    patient = db.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    history = db.get_vitals_history(patient_id)
    risk = RiskAnalyzer.calculate_risk(patient, patient["current_vitals"], history=history)
    sbar = granite_agent.generate_sbar_summary(patient, patient["current_vitals"], risk, history=history)

    return jsonify({
        "patient_id": patient_id,
        "patient_name": patient["name"],
        "sbar_report": sbar,
        "risk": risk,
        "granite_status": granite_agent.get_status()
    })

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.get_json() or {}
        api_key = data.get("apikey", "")
        project_id = data.get("project_id", "")
        url = data.get("url")
        model_id = data.get("model_id")
        status = granite_agent.update_credentials(api_key, project_id, url=url, model_id=model_id)
        return jsonify({"success": True, "status": status})
    return jsonify(granite_agent.get_status())

@app.route("/api/export/cloudant", methods=["GET"])
def api_export_cloudant():
    """Generates IBM Cloudant NoSQL lite tier compatible documents."""
    docs = []
    for p in db.get_all_patients():
        docs.append({
            "_id": f"patient_{p['id']}",
            "type": "patient_profile",
            "name": p["name"],
            "conditions": p["conditions"],
            "current_vitals": p["current_vitals"],
            "cloud_sync_service": "IBM Cloudant Lite",
            "watsonx_agent_model": Config.GRANITE_MODEL_ID
        })
    return jsonify({
        "database": "ibm_cloudant_lite_chronic_care",
        "docs_count": len(docs),
        "docs": docs
    })

if __name__ == "__main__":
    print(f"Starting AI Agent for Chronic Disease Monitoring on http://127.0.0.1:{Config.PORT}")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
