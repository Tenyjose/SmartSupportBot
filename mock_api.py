from flask import Flask, jsonify, request

app = Flask(__name__)

doctor_data = {
    "Dr. Smith": "Dr. Smith is a cardiologist with 10 years of experience.",
    "Dr. Adams": "Dr. Adams is a dermatologist known for patient care.",
    "Dr. Johnson": "Dr. Johnson is a neurologist and researcher.",
    "Dr. Brown": "Dr. Brown specializes in orthopedics.",
    "Dr. Taylor": "Dr. Taylor is a pediatrician with a friendly approach.",
    "Dr. White": "Dr. White is an experienced general physician."
}

@app.route("/api/doctors/<name>")
def get_doctor_info(name):
    # Normalize: Dr.Taylor -> Dr. Taylor
    name = name.replace("Dr.", "Dr. ").strip()
    name = name.title()

    info = doctor_data.get(name)
    if info:
        return jsonify({"info": info})
    else:
        return jsonify({"info": f"Sorry, I couldn't find details for {name}."}), 404

if __name__ == "__main__":
    app.run(port=8000)
