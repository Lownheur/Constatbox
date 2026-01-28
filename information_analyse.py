import customtkinter as ctk

class InfoAnalyseView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=120, fg_color="#2B58B1", corner_radius=0)
        self.header.place(x=0, y=0, relwidth=1)
        
        self.label_title = ctk.CTkLabel(self.header, text="WELCOME TO CONSTAT BOX", 
                                        font=("Arial", 28, "bold"), text_color="white")
        self.label_title.place(relx=0.5, rely=0.5, anchor="center")

        # --- Formulaire ---
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.place(relx=0.5, rely=0.25, anchor="n", relwidth=0.9)

        # 1. Propriétaire
        self.ent_owner = self.create_input_field("Propriétaire du domicile")
        self.ent_owner.pack(pady=10, fill="x")

        # 2. Téléphone
        self.ent_phone = self.create_input_field("Téléphone")
        self.ent_phone.pack(pady=10, fill="x")

        # 3. Localisation
        self.ent_loc = self.create_input_field("Localisation")
        self.ent_loc.pack(pady=10, fill="x")

        # --- Carte (Placeholder) ---
        # On simule la carte affichée en bas
        self.map_frame = ctk.CTkFrame(self, fg_color="#E0E0E0", corner_radius=15, height=300)
        self.map_frame.place(relx=0.5, rely=0.55, relwidth=0.7, anchor="n")
        
        ctk.CTkLabel(self.map_frame, text="[Carte Interactive]\n(Fonctionnalité MapView à intégrer)", 
                     text_color="gray", font=("Arial", 14)).place(relx=0.5, rely=0.5, anchor="center")

        # --- Bouton Enregistrer (Invisible ou explicite ?) ---
        # L'utilisateur a dit "on fait enregistrer les information et ca nous passe a la page d'apres"
        self.btn_save = ctk.CTkButton(self, text="ENREGISTRER", fg_color="#2B58B1", 
                                      font=("Arial", 16, "bold"), height=50,
                                      command=self.save_and_continue)
        self.btn_save.place(relx=0.5, rely=0.9, anchor="n")

    def create_input_field(self, placeholder):
        # Créer un champ style "Card"
        frame = ctk.CTkFrame(self.form_frame, fg_color="white", border_width=1, border_color="#cccccc", corner_radius=8)
        
        # Icone (Texte en attendant)
        icon = "👤" if "Propriétaire" in placeholder else "📞" if "Téléphone" in placeholder else "📍"
        lbl = ctk.CTkLabel(frame, text=icon, font=("Arial", 20), width=40)
        lbl.pack(side="left", padx=10)
        
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, border_width=0, fg_color="transparent", 
                             font=("Arial", 14), text_color="black", height=45)
        entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # Retourne le frame, mais on doit pouvoir accéder à l'entry. 
        # Astuce: on attache l'entry au frame
        frame.entry = entry 
        return frame

    def save_and_continue(self):
        # Sauvegarde
        self.controller.session_data["owner"] = self.ent_owner.entry.get()
        self.controller.session_data["phone"] = self.ent_phone.entry.get()
        self.controller.session_data["location"] = self.ent_loc.entry.get()
        
        print(f"Info session: {self.controller.session_data}")
        self.controller.show_frame("ChoiceMenuView")
