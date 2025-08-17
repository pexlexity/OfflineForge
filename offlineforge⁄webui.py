from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>OfflineForge UI (dev)</title>
<style>body{background:#07120b;color:#bfffd8;font-family:monospace;padding:16px}</style>
<h1>OfflineForge (dev UI)</h1>
<p>Минимальный интерфейс для наблюдения. MVP.</p>
<pre id="status">ready</pre>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/status")
def status():
    return jsonify({"status":"ready"})

if __name__ == "__main__":
    app.run(port=8080)
