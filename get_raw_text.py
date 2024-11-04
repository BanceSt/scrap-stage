from bs4 import BeautifulSoup
import os
import fitz


# print(len(os.listdir("sites\www.potomitan.info")))

BASE_PATH = "sites\www.potomitan.info"
raw_text = ""

def is_html_page(name) :
    " Renvoir vrai si la page est une page html"
    # Extraire l'extension de fichier et la convertir en minuscule
    ext = name.lower().split('.')[-1]

    # Vérifier si l'extension est l'une de celles attendues
    return ext in ["html", "htm", "php"]

def is_pdf_page(name) :
    " Renvoir vrai si la page est une page html"
    # Extraire l'extension de fichier et la convertir en minuscule
    ext = name.lower().split('.')[-1]

    # Vérifier si l'extension est l'une de celles attendues
    return ext in ["pdf"]

def get_pdf_name(path_folder) :
    " retourne le nom du pdf dans le dossier "
    files = os.listdir()

    for file in files :
        if (".pdf" in file.lower()) :
            return file
        
    return False

folders = os.listdir(BASE_PATH)

for folder in folders :
    # Création du chemin
    path_join = os.path.join(BASE_PATH, folder)
    
    # Est ce une page HTML
    if (is_html_page(folder)) :
        # chemin page html
        path_page = os.path.join(path_join, "page.html")
        print("path_page :", path_page)
        print("======================================")

        # Ouvrir et lire le contenu du fichier HTML
        with open(path_page, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Initialiser BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Récupérer tout le texte à l'intérieur de la balise body
        if (soup.body) :
            body = soup.body.get_text(separator=' ', strip=True)
        else :
            body = soup.get_text(" ", True)

        raw_text += body + "\n"
    
    elif (is_pdf_page(folder)) :
        # Récupération nom pdf
        pdf_name = get_pdf_name(path_join)
        if not(pdf_name) :
            continue

        #chemin du pdf
        path_pdf = os.path.join(path_join, pdf_name)

        # ouvrir le fichier pdf
        try : 
            pdf_doc = fitz.open(path_join)

            # Parcourir toutes les pages du PDF
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc.load_page(page_num)  # Charger la page
                raw_text += page.get_text("text")  # Extraire le texte brut
        except Exception as e:
            print(f"Erreur {e}")
        finally :
            # Fermer le fichier PDF
            pdf_doc.close()

# Sauvegarde du fichier raw_text
path_save = "data"
os.makedirs(path_save, exist_ok=True)
with open(os.path.join(path_save, "raw_text.txt"), "w", encoding='utf-8') as file:
    file.write(raw_text)


        

        


    


