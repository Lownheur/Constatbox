#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 00:14:38 2026

@author: benbruno
"""
from flask import Flask, jsonify
from flask_cors import CORS
from scapy.all import rdpcap, IP
import os
import json
from collections import Counter
import geoip2.database  # Bibliothèque pour la géolocalisation

app = Flask(__name__)
CORS(app)

ARCHIVE_DIR = "archives"
# Chemin vers la base de données de pays (à télécharger sur MaxMind)
GEOIP_DB_PATH = 'GeoLite2-City.mmdb'

def get_country_from_ip(ip):
    """Localise le pays d'une IP via la base de données locale."""
    if not os.path.exists(GEOIP_DB_PATH):
        return "Base GeoIP absente"
    
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.city(ip)
            return response.country.name if response.country.name else "Inconnu"
    except Exception:
        return "Local/Privé"

def analyze_pcap_stats(pcap_filename):
    """Analyse approfondie du fichier PCAP."""
    file_path = os.path.join(ARCHIVE_DIR, pcap_filename)
    if not os.path.exists(file_path):
        return None

    print(f"[*] Analyse forensic en cours : {pcap_filename}...")
    try:
        packets = rdpcap(file_path)
    except Exception as e:
        return {"error": str(e)}

    total_size = 0
    ip_consumption = Counter()
    external_destinations = Counter()
    countries_stats = Counter()

    for pkt in packets:
        if pkt.haslayer(IP):
            size = len(pkt)
            total_size += size
            src = pkt[IP].src
            dst = pkt[IP].dst
            
            # 1. Statistiques de consommation locale (Source = Réseau Local)
            if src.startswith("192.168.1."):
                ip_consumption[src] += size
            
            # 2. Analyse des destinations externes (Destination != Réseau Local)
            if not dst.startswith("192.168.1.") and not dst.startswith("239."):
                country = get_country_from_ip(dst)
                external_destinations[dst] += 1
                countries_stats[country] += 1

    # Formatage du classement des appareils
    devices_ranking = []
    for ip, size in ip_consumption.items():
        percent = (size / total_size) * 100 if total_size > 0 else 0
        devices_ranking.append({
            "ip": ip,
            "data_kb": round(size / 1024, 2),
            "percentage": round(percent, 1)
        })

    # Formatage des statistiques par pays
    total_external = sum(countries_stats.values())
    countries_ranking = []
    for country, count in countries_stats.items():
        countries_ranking.append({
            "country": country,
            "hits": count,
            "percent": round((count / total_external) * 100, 1) if total_external > 0 else 0
        })

    return {
        "metadata": {
            "filename": pcap_filename,
            "total_packets": len(packets),
            "total_size_mb": round(total_size / (1024*1024), 2)
        },
        "bandwidth_usage": sorted(devices_ranking, key=lambda x: x['percentage'], reverse=True),
        "geography": sorted(countries_ranking, key=lambda x: x['hits'], reverse=True),
        "top_ips_visited": external_destinations.most_common(10)
    }

# --- ROUTES API ---

@app.route('/api/last-scan/forensic', methods=['GET'])
def get_latest_forensic():
    """Route pour obtenir l'analyse du dernier fichier capturé."""
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.pcap')]
    if not files:
        return jsonify({"error": "Aucun fichier PCAP trouvé"}), 404
    
    latest_pcap = sorted(files, reverse=True)[0]
    data = analyze_pcap_stats(latest_pcap)
    return jsonify(data)

@app.route('/api/archives', methods=['GET'])
def list_archives():
    """Liste tous les scans disponibles."""
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.json')]
    return jsonify(sorted(files, reverse=True))

if __name__ == '__main__':
    print("-------------------------------------------------------")
    print("🚀 CONSTATBOX API : Serveur d'Analyse Forensic")
    print("Lien de test : http://localhost:5000/api/last-scan/forensic")
    print("-------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)