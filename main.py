import customtkinter as ctk
from PIL import Image
import os
import sys

# Import des vues
from accueil import AccueilView
from information_analyse import InfoAnalyseView
from choice_menu import ChoiceMenuView
from scan_reseaux import ScanReseauView
from history import HistoryView
from scan_bluetooth import ScanBluetoothView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ConstatBoxApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CONSTATBOX - Mobile")
        self.geometry("414x896") # Aspect ratio mobile (ex: iPhone XR/11)
        self.resizable(False, False)

        # Données de session partagées entre les vues
        self.session_data = {
            "owner": "",
            "phone": "",
            "location": "",
            "coords": None
        }

        # Container principal
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True)

        # Dictionnaire des vues
        self.frames = {}
        
        # Initialisation des vues disponibles
        # Note: On instancie les classes de vue ici.
        # Chaque vue devra hériter de ctk.CTkFrame et prendre 'controller' en arg.
        
        self.view_classes = (
            AccueilView,
            InfoAnalyseView,
            ChoiceMenuView,
            ScanReseauView,
            HistoryView,
            ScanBluetoothView
        )

        # On charge la première vue
        self.show_frame("AccueilView")

    def show_frame(self, page_name):
        """Affiche la vue demandée et la crée si nécessaire (Lazy Loading)"""
        
        # Masquer la vue actuelle si elle existe
        for frame in self.frames.values():
            frame.pack_forget()

        if page_name not in self.frames:
            # Recherche de la classe correspondante
            cls = next((c for c in self.view_classes if c.__name__ == page_name), None)
            if cls:
                # Création de l'instance
                # On passe 'self' comme contrôleur pour accéder à shared_data et show_frame
                frame = cls(parent=self.container, controller=self)
                self.frames[page_name] = frame
            else:
                print(f"Vue {page_name} introuvable.")
                return

        # Afficher la nouvelle vue
        frame = self.frames[page_name]
        frame.pack(fill="both", expand=True)
        
        # Rafraîchir si la vue a une méthode 'on_show'
        if hasattr(frame, "on_show"):
            frame.on_show()

if __name__ == "__main__":
    app = ConstatBoxApp()
    app.mainloop()