import customtkinter as ctk
import json
import os

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.history_file = "constat_history.json"
        
        # --- Header ---
        self.header = ctk.CTkFrame(self, height=60, fg_color="#2B58B1", corner_radius=0)
        self.header.pack(fill="x")
        
        ctk.CTkButton(self.header, text="< Menu", width=80, fg_color="transparent", command=lambda: controller.show_frame("ChoiceMenuView")).pack(side="left", padx=10)
        ctk.CTkLabel(self.header, text="Historique des Analyses", font=("Arial", 20, "bold"), text_color="white").pack(side="left", padx=20)
        
        ctk.CTkButton(self.header, text="Actualiser", width=100, fg_color="#1a3b7c", command=self.load_history).pack(side="right", padx=10)

        # Content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def on_show(self):
        self.load_history()

    def load_history(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        if not os.path.exists(self.history_file):
            ctk.CTkLabel(self.scroll, text="Aucun historique.").pack()
            return
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: return
        
        for entry in reversed(data):
            self.create_card(entry)

    def create_card(self, entry):
        card = ctk.CTkFrame(self.scroll, fg_color="#f0f0f0", corner_radius=10, border_width=1, border_color="#ddd")
        card.pack(fill="x", pady=10, padx=5)
        
        # Header Card
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(head, text=f"📅 {entry['date']} {entry['heure']}", font=("Arial", 12, "bold"), text_color="#555").pack(side="left")
        ctk.CTkLabel(head, text=f"📡 {entry.get('wifi','?')}", font=("Arial", 12, "bold"), text_color="#2B58B1").pack(side="right")
        
        # Info Session (Nouveau)
        sess = entry.get('session_info', {})
        if sess:
            info_str = f"👤 {sess.get('owner','?')} | 📞 {sess.get('phone','?')}"
            ctk.CTkLabel(card, text=info_str, font=("Arial", 11), text_color="#666").pack(anchor="w", padx=10)

        # Devises summary
        devs = entry.get('devices', [])
        ctk.CTkLabel(card, text=f"{len(devs)} Appareils connectés", text_color="green", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5,0))
        
        # Table
        if devs:
            tbl = ctk.CTkFrame(card, fg_color="white")
            tbl.pack(fill="x", padx=10, pady=10)
            
            # Headers
            hframe = ctk.CTkFrame(tbl, fg_color="#eee", height=25)
            hframe.pack(fill="x")
            cols = ["Appareil", "Type", "IP", "MAC"]
            for c in cols:
                ctk.CTkLabel(hframe, text=c, font=("Arial", 10, "bold"), width=100, anchor="w").pack(side="left", padx=5, expand=True, fill="x")
                
            # Rows
            for d in devs:
                rframe = ctk.CTkFrame(tbl, fg_color="transparent")
                rframe.pack(fill="x", pady=2)
                
                name = d.get('hostname') or d.get('vendor') or "?"
                typ = d.get('type', '?')
                
                ctk.CTkLabel(rframe, text=name[:20], width=100, anchor="w", font=("Arial", 10)).pack(side="left", padx=5, expand=True, fill="x")
                ctk.CTkLabel(rframe, text=typ[:15], width=100, anchor="w", text_color="gray", font=("Arial", 10)).pack(side="left", padx=5, expand=True, fill="x")
                ctk.CTkLabel(rframe, text=d['ip'], width=100, anchor="w", font=("Consolas", 10)).pack(side="left", padx=5, expand=True, fill="x")
                ctk.CTkLabel(rframe, text=d['mac'], width=100, anchor="w", font=("Consolas", 10), text_color="gray").pack(side="left", padx=5, expand=True, fill="x")
