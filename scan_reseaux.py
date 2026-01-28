import customtkinter as ctk
import pywifi
from pywifi import const
import time
import threading
import socket
import requests
import os
import json
from datetime import datetime
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1
import geocoder

class ScanReseauView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        
        # --- Variables ---
        self.wifi = pywifi.PyWiFi()
        try:
            self.iface = self.wifi.interfaces()[0]
        except:
            self.iface = None # Pas de carte wifi
            
        self.current_network = None
        self.history_file = "constat_history.json"
        
        # --- Header ---
        self.header = ctk.CTkFrame(self, height=60, fg_color="#2B58B1", corner_radius=0)
        self.header.pack(fill="x")
        
        ctk.CTkButton(self.header, text="< Menu", width=80, fg_color="transparent", command=lambda: controller.show_frame("ChoiceMenuView")).pack(side="left", padx=10)
        ctk.CTkLabel(self.header, text="Analyeur Réseau WiFi", font=("Arial", 20, "bold"), text_color="white").pack(side="left", padx=20)

        # --- TabView Mobile ---
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_conn = self.tabview.add("Connexion WiFi")
        self.tab_anal = self.tabview.add("Analyse Forensic")
        
        # --- Onglet 1: Connexion ---
        ctk.CTkLabel(self.tab_conn, text="Réseaux Détectés", font=("Arial", 16, "bold")).pack(pady=5)
        self.btn_scan = ctk.CTkButton(self.tab_conn, text="Actualiser les réseaux", command=self.start_wifi_scan)
        self.btn_scan.pack(pady=5)
        
        self.wifi_scroll = ctk.CTkScrollableFrame(self.tab_conn, height=200)
        self.wifi_scroll.pack(fill="x", pady=10)
        
        # Form Connexion
        self.entry_ssid = ctk.CTkEntry(self.tab_conn, placeholder_text="SSID")
        self.entry_ssid.pack(pady=5, fill="x")
        self.entry_pw = ctk.CTkEntry(self.tab_conn, placeholder_text="Mot de passe", show="*")
        self.entry_pw.pack(pady=5, fill="x")
        self.btn_connect = ctk.CTkButton(self.tab_conn, text="Se Connecter", command=self.connect_wifi)
        self.btn_connect.pack(pady=10)

        # --- Onglet 2: Analyse ---
        self.status_label = ctk.CTkLabel(self.tab_anal, text="NON CONNECTÉ", text_color="red", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)
        
        self.btn_analyse = ctk.CTkButton(self.tab_anal, text="LANCER L'ANALYSE", state="disabled", 
                                         height=50, fg_color="green", command=self.run_forensic_analysis)
        self.btn_analyse.pack(pady=10, fill="x")
        
        self.log_output = ctk.CTkTextbox(self.tab_anal)
        self.log_output.pack(fill="both", expand=True, pady=10)

    def on_show(self):
        # Scan auto à l'arrivée sur la page
        if self.iface:
            self.start_wifi_scan()

    def log(self, text):
        self.after(0, lambda: self.log_output.insert("end", text + "\n"))
        self.after(0, lambda: self.log_output.see("end"))

    # --- Logique WiFi (Adaptée) ---
    def start_wifi_scan(self):
        if not self.iface: return
        self.btn_scan.configure(state="disabled", text="Scanning...")
        
        def _scan():
            try:
                self.iface.scan()
                time.sleep(3)
                results = self.iface.scan_results()
                unique = {res.ssid: res for res in results if res.ssid}
                self.after(0, lambda: self.update_wifi_list(unique))
            except Exception as e:
                self.log(f"Erreur scan: {e}")
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="Scanner"))
            
        threading.Thread(target=_scan, daemon=True).start()

    def update_wifi_list(self, networks):
        for w in self.wifi_scroll.winfo_children(): w.destroy()
        
        for ssid, data in networks.items():
            btn = ctk.CTkButton(self.wifi_scroll, text=f"{ssid} ({100+data.signal}%)", 
                                anchor="w", fg_color="transparent", text_color="black", hover_color="#ddd",
                                command=lambda s=ssid: self.select_wifi(s))
            btn.pack(fill="x")
            
    def select_wifi(self, ssid):
        self.entry_ssid.delete(0, "end")
        self.entry_ssid.insert(0, ssid)

    def connect_wifi(self):
        ssid = self.entry_ssid.get()
        pw = self.entry_pw.get()
        if not ssid: return
        self.log(f"Connexion à {ssid}...")
        
        def _conn():
            self.iface.disconnect()
            time.sleep(1)
            p = pywifi.Profile()
            p.ssid = ssid
            p.auth = const.AUTH_ALG_OPEN
            p.akm.append(const.AKM_TYPE_WPA2PSK)
            p.cipher = const.CIPHER_TYPE_CCMP
            p.key = pw
            self.iface.remove_all_network_profiles()
            tmp = self.iface.add_network_profile(p)
            self.iface.connect(tmp)
            
            for _ in range(10):
                if self.iface.status() == const.IFACE_CONNECTED:
                    self.current_network = ssid
                    self.after(0, self.on_connected)
                    return
                time.sleep(1)
            self.log("Echec connexion.")
            
        threading.Thread(target=_conn, daemon=True).start()

    def on_connected(self):
        self.status_label.configure(text=f"CONNECTÉ : {self.current_network}", text_color="green")
        self.btn_analyse.configure(state="normal")
        self.log("Connecté avec succès.")

    # --- Logique Analyse (Copiée/Améliorée) ---
    def get_mac_vendor(self, mac):
        try:
            res = requests.get(f"https://api.macvendors.com/{mac}", timeout=2)
            return res.text if res.status_code == 200 else "Inconnu"
        except: return "Erreur"

    def get_device_details(self, ip):
        hostname = "Inconnu"
        try: hostname = socket.gethostbyaddr(ip)[0]
        except: pass
        
        os_guess = "Inconnu"
        try:
            pkt = IP(dst=ip)/ICMP()
            reply = sr1(pkt, timeout=1, verbose=0)
            if reply:
                ttl = reply.ttl
                if ttl <= 64: os_guess = "Linux/Mobile"
                elif ttl <= 128: os_guess = "Windows"
                elif ttl <= 255: os_guess = "Cisco/Net"
        except: pass
        return hostname, os_guess

    def run_forensic_analysis(self):
        self.btn_analyse.configure(state="disabled", text="Analyse...")
        self.log("Démarrage forensic analysis...")
        
        def _analyze():
            try:
                # Localisation
                g = geocoder.ip('me')
                
                # IP Locale
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                my_ip = s.getsockname()[0]
                s.close()
                target = ".".join(my_ip.split('.')[:-1]) + ".0/24"
                
                # Scan ARP
                ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target), timeout=4, verbose=False)
                
                devices = []
                for _, rcve in ans:
                    vendor = self.get_mac_vendor(rcve.hwsrc)
                    host, os_res = self.get_device_details(rcve.psrc)
                    
                    # Classification simple
                    dtype = "Autre"
                    vup = vendor.upper()
                    if "APPLE" in vup: dtype = "Apple"
                    elif "MSI" in vup or "DELL" in vup: dtype = "PC"
                    elif "XIAOMI" in vup or "SAMSUNG" in vup: dtype = "Mobile"
                    
                    devices.append({
                        "ip": rcve.psrc, "mac": rcve.hwsrc, "vendor": vendor,
                        "hostname": host, "os": os_res, "type": dtype
                    })
                
                # Sauvegarde
                data = {
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "heure": datetime.now().strftime("%H:%M:%S"),
                    "wifi": self.current_network,
                    "localisation": {"adresse": g.address, "ville": g.city, "pays": g.country},
                    "devices": devices,
                    # Ajout des données de session (Formulaire précédent)
                    "session_info": self.controller.session_data
                }
                
                self.save_to_json(data)
                self.log(f"Analyse terminée. {len(devices)} appareils trouvés.")
                
            except Exception as e:
                self.log(f"Erreur durant l'analyse: {e}")
            
            self.after(0, lambda: self.btn_analyse.configure(state="normal", text="LANCER L'ANALYSE"))
            
        threading.Thread(target=_analyze, daemon=True).start()

    def save_to_json(self, data):
        hist = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    hist = json.load(f)
            except: pass
        hist.append(data)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(hist, f, indent=4, ensure_ascii=False)
