


from flask import Flask, request, jsonify, render_template
import subprocess
import uuid
import os
import datetime
import zipfile
import tempfile
from threading import Semaphore

app = Flask(__name__)

# -----------------------------------
# SETTINGS
# -----------------------------------
MAX_PARALLEL_CONTAINERS = 5
sema = Semaphore(MAX_PARALLEL_CONTAINERS)

# Create logs folder
if not os.path.exists("logs"):
    os.makedirs("logs")


# -----------------------------------
# LOGGING FUNCTION
# -----------------------------------
def write_log(status, code, return_code, output, errors):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
----------------------------
TIME: {timestamp}
STATUS: {status}
RETURN CODE: {return_code}

USER CODE:
{code}

OUTPUT:
{output}

ERROR:
{errors}
----------------------------
"""
    with open("logs/executions.log", "a", encoding="utf-8") as f:
        f.write(log_entry)



# -----------------------------------
# HOME UI ROUTE
# -----------------------------------
@app.get("/")
def home():
    return render_template("index.html")



# -----------------------------------
# RUN SINGLE FILE (Python + JS)
# -----------------------------------
@app.post("/run")
def run_code():
    with sema:  
        body = request.get_json()
        code = body.get("code", "")
        language = body.get("language", "python")

        if len(code) > 5000:
            return jsonify({"error": "Code too long. Max 5000 chars allowed."})

        file_id = uuid.uuid4().hex
        ext = "py" if language == "python" else "js"
        filename = f"temp_{file_id}.{ext}"

        with open(filename, "w") as f:
            f.write(code)

        print("\n\n---- EXECUTION START ----")
        print("Language:", language)
        print("Code:\n", code)

        if language == "javascript":
            docker_image = "node:18-slim"
            run_cmd = ["node", f"/app/{filename}"]
        else:
            docker_image = "python:3.11-slim"
            run_cmd = ["python", f"/app/{filename}"]

        docker_command = [
            "docker", "run",
            "--read-only",
            "--network", "none",
            "--memory=128m",
            "--cpus=0.5",
            "--ulimit", "cpu=10",
            "-v", f"{os.getcwd()}:/app",
            docker_image,
            *run_cmd
        ]

        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True
            )

            output = result.stdout
            errors = result.stderr
            return_code = result.returncode

            print("RETURN CODE:", return_code)
            print("STDOUT:", output)
            print("STDERR:", errors)

            os.remove(filename)

            if return_code != 0 and output == "" and errors == "":
                status = "EXECUTION STOPPED (Killed by Docker)"
                write_log(status, code, return_code, output, errors)
                return jsonify({"output": "", "error": "Execution stopped: CPU or memory exceeded"})

            if return_code != 0:
                status = "RUNTIME ERROR"
                write_log(status, code, return_code, output, errors)
                return jsonify({"output": output, "error": errors})

            status = "SUCCESS"
            write_log(status, code, return_code, output, errors)
            return jsonify({"output": output, "error": ""})

        except Exception as e:
            status = "SYSTEM ERROR"
            write_log(status, code, -1, "", str(e))
            return jsonify({"error": str(e)})



# -----------------------------------
# EXECUTION HISTORY
# -----------------------------------
@app.get("/history")
def history():
    try:
        with open("logs/executions.log", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "No history available."



# -----------------------------------
# RUN MULTIPLE FILES (.ZIP UPLOAD)
# -----------------------------------
@app.post("/upload_zip")
def upload_zip():
    with sema:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        zip_file = request.files["file"]

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "project.zip")
        zip_file.save(zip_path)

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(temp_dir)
        except:
            return jsonify({"error": "Invalid ZIP file"})

        main_py = os.path.join(temp_dir, "main.py")
        main_js = os.path.join(temp_dir, "index.js")

        if os.path.exists(main_py):
            docker_image = "python:3.11-slim"
            run_cmd = ["python", "/app/main.py"]
        elif os.path.exists(main_js):
            docker_image = "node:18-slim"
            run_cmd = ["node", "/app/index.js"]
        else:
            return jsonify({"error": "ZIP must contain main.py or index.js"})

        docker_command = [
            "docker", "run",
            "--read-only",
            "--network", "none",
            "--memory=128m",
            "--cpus=0.5",
            "--ulimit", "cpu=10",
            "-v", f"{temp_dir}:/app",
            docker_image,
            *run_cmd
        ]

        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True
        )

        return jsonify({
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        })



# -----------------------------------
# START SERVER
# -----------------------------------
app.run(host="0.0.0.0", port=5000)