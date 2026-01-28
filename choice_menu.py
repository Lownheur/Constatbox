import customtkinter as ctk

class ChoiceMenuView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=100, fg_color="#2B58B1", corner_radius=0)
        self.header.place(x=0, y=0, relwidth=1)
        
        self.label_title = ctk.CTkLabel(self.header, text="SCAN RESEAU & PERIPHERIQUES", 
                                        font=("Arial", 24, "bold"), text_color="white")
        self.label_title.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bell Icon (Simulation)
        self.bell = ctk.CTkButton(self.header, text="🔔 2", width=40, fg_color="red", hover_color="darkred", corner_radius=20)
        self.bell.place(relx=0.9, rely=0.5, anchor="center")

        # --- Menu Grid ---
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.place(relx=0.5, rely=0.2, anchor="n", relwidth=0.9, relheight=0.7)

        # Labels de section
        ctk.CTkLabel(self.menu_frame, text="SCANS", font=("Arial", 14, "bold"), text_color="#FF5555", anchor="w").pack(fill="x", pady=(10,5))
        
        # Boutons Scans (Stack vertical pour mobile)
        self.btn_scan_net = self.create_big_button(self.menu_frame, "SCAN RESEAU\n(WIFI & LAN)", 
                                                   command=lambda: controller.show_frame("ScanReseauView"))
        self.btn_scan_net.pack(fill="x", pady=10)
        
        self.btn_scan_bt = self.create_big_button(self.menu_frame, "SCAN PERIPHERIQUES\n(BLUETOOTH)",
                                                   command=self.launch_bluetooth_scan)
        self.btn_scan_bt.pack(fill="x", pady=10)

        # Section Historique
        ctk.CTkLabel(self.menu_frame, text="HISTORIQUE", font=("Arial", 14, "bold"), text_color="#FF5555", anchor="w").pack(fill="x", pady=(20,5))
        
        self.btn_history = self.create_big_button(self.menu_frame, "CONSULTER\nL'HISTORIQUE",
                                                  command=lambda: controller.show_frame("HistoryView"))
        self.btn_history.pack(fill="x", pady=10)

    def create_big_button(self, parent, text, command):
        btn = ctk.CTkButton(parent, text=text, font=("Arial", 16, "bold"), 
                            fg_color="white", text_color="black", 
                            height=150, corner_radius=10,
                            border_width=1, border_color="#cccccc",
                            hover_color="#f0f0f0",
                            command=command)
        return btn

    def launch_bluetooth_scan(self):
        self.controller.show_frame("ScanBluetoothView")
