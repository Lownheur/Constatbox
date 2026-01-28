import customtkinter as ctk
import asyncio
import threading
from datetime import datetime
import time

# Try importing bleak
try:
    from bleak import BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

class ScanBluetoothView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        
        # Header
        self.header = ctk.CTkFrame(self, height=60, fg_color="#2B58B1", corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkButton(self.header, text="< Menu", width=80, fg_color="transparent", command=lambda: controller.show_frame("ChoiceMenuView")).pack(side="left", padx=10)
        ctk.CTkLabel(self.header, text="Scan Bluetooth", font=("Arial", 20, "bold"), text_color="white").pack(side="left", padx=20)
        
        # Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.status_lbl = ctk.CTkLabel(self.content, text="Ready to scan", font=("Arial", 14))
        self.status_lbl.pack(pady=10)
        
        self.btn_scan = ctk.CTkButton(self.content, text="Lancer Scan Bluetooth", command=self.start_scan)
        self.btn_scan.pack(pady=10)
        
        self.scroll = ctk.CTkScrollableFrame(self.content, width=600, height=400)
        self.scroll.pack(pady=10)
        
    def start_scan(self):
        if not BLEAK_AVAILABLE:
            self.status_lbl.configure(text="Erreur: Librairie 'bleak' manquante. Installez-la avec 'pip install bleak'", text_color="red")
            return
            
        self.btn_scan.configure(state="disabled", text="Scanning...")
        self.status_lbl.configure(text="Scanning en cours...", text_color="orange")
        for w in self.scroll.winfo_children(): w.destroy()
        
        threading.Thread(target=self.run_async_scan, daemon=True).start()
        
    def run_async_scan(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        devices = loop.run_until_complete(self.scan_ble())
        loop.close()
        
        self.after(0, lambda: self.update_ui(devices))
        
    async def scan_ble(self):
        try:
            devices = await BleakScanner.discover()
            return devices
        except Exception as e:
            print(e)
            return []

    def update_ui(self, devices):
        self.btn_scan.configure(state="normal", text="Lancer Scan Bluetooth")
        if not devices:
            self.status_lbl.configure(text="Aucun périphérique trouvé ou erreur.", text_color="red")
            return
            
        self.status_lbl.configure(text=f"{len(devices)} Périphériques trouvés", text_color="green")
        
        for d in devices:
            # d is BLEDevice
            name = d.name or "Unknown"
            addr = d.address
            rssi = d.rssi
            
            row = ctk.CTkFrame(self.scroll, fg_color="#eee")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=name, width=200, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=addr, width=150, anchor="w", font=("Consolas", 11)).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{rssi} dBm", width=80, text_color="gray").pack(side="left", padx=10)
