from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# DEIN DISCORD WEBHOOK
WEBHOOK_URL = "https://discord.com/api/webhooks/1529571642022560025/mxoBq18yGw7Vwp1Mu2ZJHsApOQsEHAKfmTUEMsBQgqgKk-fVN9fAJ7-3AKS3lBVXS5Ex"

@app.route('/preview')
def preview():
    return render_template('preview.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/einwilligung')
def einwilligung():
    return render_template('einwilligung.html')

@app.route('/send-ip', methods=['POST'])
def send_ip():
    try:
        ip = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0]
        
        user_agent = request.headers.get('User-Agent', 'Unbekannt')
        zeit = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        data = {
            "content": f"**🆕 Neuer Besucher hat eingewilligt!**\n\n"
                       f"🌐 **IP-Adresse:** `{ip}`\n"
                       f"🕐 **Zeit:** {zeit}\n"
                       f"📱 **Gerät:** {user_agent[:50]}..."
        }
        
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code == 204:
            return jsonify({"status": "success", "message": "IP wurde gesendet"})
        else:
            return jsonify({"status": "error", "message": "Fehler beim Senden"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
