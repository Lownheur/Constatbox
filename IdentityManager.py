#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 23:01:51 2026

@author: benbruno
"""

import json
import os
from scapy.all import DNS, DNSQR, IP, NBNSQueryRequest

class IdentityManager:
    def __init__(self, db_file="archives/identities.json"):
        self.db_file = db_file
        self.identities = self.load_db()

    def load_db(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}

    def save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.identities, f, indent=4)

    def resolve_human_name(self, ip, mac, packet=None):
        """
        Tente de trouver un nom humain pour une IP/MAC donnée.
        """
        mac = mac.upper()
        
        # 1. Vérifier si on connaît déjà cette MAC
        if mac in self.identities:
            return self.identities[mac]

        # 2. Analyse passive du paquet pour trouver un nom d'hôte
        if packet:
            # MDNS (Apple/Linux/Android) - "Je suis l'iPhone de Marcelle"
            if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
                try:
                    qname = packet.getlayer(DNSQR).qname.decode().lower()
                    if ".local" in qname:
                        hostname = qname.split(".local")[0]
                        self.update_identity(mac, hostname)
                        return hostname
                except: pass

            # NBNS (Windows)
            if packet.haslayer(NBNSQueryRequest):
                try:
                    hostname = packet.getlayer(NBNSQueryRequest).QUESTION_NAME.decode().strip()
                    self.update_identity(mac, hostname)
                    return hostname
                except: pass

        return f"Appareil-{ip.split('.')[-1]}"

    def update_identity(self, mac, name):
        if mac not in self.identities or self.identities[mac] != name:
            self.identities[mac] = name
            self.save_db()
            print(f"    [🔍 IDENTITY] Nouvelle cible identifiée : {mac} est désormais '{name}'")