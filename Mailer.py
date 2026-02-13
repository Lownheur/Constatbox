#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 00:44:41 2026

@author: benbruno
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

import os

def send_investigation_log(file_path):
    # --- CONFIGURATION ---
    sender_email = "bengono2911@gmail.com"
    sender_name = "No-Reply ConstatBox"
    receiver_email = "bengonobekolo2911@gmail.com"
    app_password = "nobd kjlr adog grtt" 
    msg = MIMEMultipart()
    # formataddr crée une chaîne propre : "No-Reply ConstatBox <ton_email@gmail.com>"
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = receiver_email
    msg['Subject'] = f"🛡️ [RAPPORT AUTOMATIQUE] - {os.path.basename(file_path)}"
    msg['Reply-To'] = "noreply@constatbox.local"
    body = "L'analyse est terminée. Trouve ci-joint le journal de surveillance humaine généré par la Pi."
    msg.attach(MIMEText(body, 'plain'))

    # Pièce jointe (le log)
    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(file_path)}")
            msg.attach(part)

        # Connexion au serveur SMTP de Google
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Rapport envoyé par email à {receiver_email}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")