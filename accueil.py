import customtkinter as ctk
from PIL import Image
import os

class AccueilView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=120, fg_color="#2B58B1", corner_radius=0)
        self.header.place(x=0, y=0, relwidth=1)
        
        # Titre
        self.label_title = ctk.CTkLabel(self.header, text="WELCOME TO\nCONSTAT BOX", 
                                        font=("Arial", 24, "bold"), text_color="white")
        self.label_title.place(relx=0.5, rely=0.5, anchor="center")

        # --- Décoration (Canvas) ---
        self.canvas = ctk.CTkCanvas(self, width=414, height=896, bg="white", highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.header.lift() # Header au dessus

        # Cercle bas gauche
        self.canvas.create_oval(-50, 750, 200, 1000, fill="#2B58B1", outline="")
        
        # Bulles (Centrées ou ajustées)
        self.canvas.create_oval(180, 820, 200, 840, fill="#2B58B1", outline="") 
        self.canvas.create_oval(210, 820, 230, 840, outline="#33AA33", width=2)
        self.canvas.create_oval(240, 820, 260, 840, outline="#33AA33", width=2)

        # --- Logo ---
        logo_path = "OFAClogo.jpg"
        if os.path.exists(logo_path):
            # Taille réduite pour mobile
            img = ctk.CTkImage(Image.open(logo_path), size=(250, 180)) 
            self.logo_label = ctk.CTkLabel(self, image=img, text="")
            self.logo_label.place(relx=0.5, rely=0.45, anchor="center")

        # --- Bouton Start ---
        self.btn_start = ctk.CTkButton(self, text="COMMENCER", fg_color="#2B58B1", 
                                       font=("Arial", 16, "bold"), width=200, height=50,
                                       command=lambda: controller.show_frame("InfoAnalyseView"))
        self.btn_start.place(relx=0.5, rely=0.75, anchor="center")

        # --- Footer ---
        footer_text = "CONSTAT BOX | Powered by 3IL"
        self.label_footer = ctk.CTkLabel(self, text=footer_text, font=("Arial", 10), text_color="black")
        self.label_footer.place(relx=0.5, rely=0.95, anchor="center")
