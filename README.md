# Projet ConstatBox

Ce dépôt contient le code source et la documentation du projet **ConstatBox**, un kit d'investigation numérique de premier niveau.

## 📄 Documentation (Charte de Projet)

La charte de projet est rédigée en LaTeX.

### Prérequis
- Une distribution LaTeX (TeX Live, MiKTeX, MacTeX...)
- `pdflatex` installé et accessible dans le PATH.

### Compilation
Pour générer le fichier PDF de la charte, exécutez la commande suivante dans votre terminal :

```bash
pdflatex charte_projet.tex
```

Cela générera le fichier `charte_projet.pdf`.

> **Note :** Il est recommandé d'exécuter la commande deux fois pour s'assurer que la table des matières est correctement générée.

## 💻 Application Mobile (Interface)

L'interface utilisateur est développée en Python avec Kivy (ou framework similaire selon `requirements.txt`).

### Prérequis
- Python 3.x installé.
- Les dépendances du projet installées :
  ```bash
  pip install -r requirements.txt
  ```

### Lancement de l'application
Pour lancer l'application principale, exécutez :

```bash
python main.py
```
