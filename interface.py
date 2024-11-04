from urllib.parse import urljoin, urlparse
from tkinter import filedialog
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import tkinter as tk
import requests
import time
import re
import os
import threading


class ScrapGui(tk.Tk) :

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.act_website = ""
        self.base_save_path = ""
        self.default_name_html = "page.html"
        self.next_path = []
        self.already_seen_path = []
        self.website_images = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        self.ignore_headers = {
            "#",
            "javascript:"
        }

        # ====================================== Interface ====================================== 
        self.width = 800
        self.height = 450
        self.bg_color1 = "#FCFAEE"
        # configuration de la fenêtre
        self.title("Scrapping interface")
        self.geometry(f"{self.width}x{self.height}")

        # Frame principale
        self.main_frame = tk.Frame(self, background="lightgrey", bd=2, relief=tk.GROOVE, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # ============= Frame gauche ============= 
        self.left_frame = tk.Frame(self.main_frame, height=self.height, width=self.width//3 ,background=self.bg_color1, highlightthickness=0)
        self.left_frame.pack(anchor="w", side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)

        # Adresse web
        tk.Label(self.left_frame, text="Adresse du site web : ", background=self.bg_color1,
                 font=("helvetica", 13)).pack(side=tk.TOP, anchor="w", padx=2)
        self.input_website = tk.Entry(self.left_frame, relief="solid", font=("helvetica", 12))
        self.input_website.pack(side=tk.TOP, anchor="w", fill="x", pady=2, padx=4, ipady=2)

        #sep
        tk.Frame(self.left_frame, background=self.bg_color1, height=15).pack(side=tk.TOP, fill="x")

        # chemin de sauvegarde
        tk.Label(self.left_frame, text="Chemin de sauvegarde : ", background=self.bg_color1,
                 font=("helvetica", 13)).pack(side=tk.TOP, anchor="w", padx=2)
        frame_save_path = tk.Frame(self.left_frame)
        frame_save_path.pack(side=tk.TOP, fill="x")

        #
        self.folder_icon = ImageTk.PhotoImage(Image.open("icon\\folder.png").resize((18, 18)))
        self.search_folder_btn = tk.Button(frame_save_path, image=self.folder_icon, width=20, height=20, command=self.get_path_folder)
        self.search_folder_btn.pack(side="left")

        self.search_folder_input = tk.Entry(frame_save_path, relief="solid", font=("helvetica", 12))
        self.search_folder_input.pack(side="left", fill="x", padx=4, ipady=3, expand=True)

        #sep
        tk.Frame(self.left_frame, background=self.bg_color1, height=15).pack(side=tk.TOP, fill="x")


        # === Option

        # Variables associées aux Checkbuttons
        self.opt_skip_seen_page_var = tk.IntVar()
        self.opt_skip_image_var = tk.IntVar()
        self.opt_skip_video_var = tk.IntVar()


        tk.Label(self.left_frame, text="Options : ", background=self.bg_color1,
                 font=("helvetica", 13)).pack(side=tk.TOP, anchor="w", padx=2)
        
        self.opt_skip_seen_page = tk.Checkbutton(self.left_frame, text="Skip seen page", 
                                                 bg=self.bg_color1, variable=self.opt_skip_seen_page_var)
        self.opt_skip_seen_page.pack(side=tk.TOP, anchor="w")

        self.opt_skip_image = tk.Checkbutton(self.left_frame, text="Skip image", 
                                             bg=self.bg_color1, variable=self.opt_skip_image_var)
        self.opt_skip_image.pack(side=tk.TOP, anchor="w")

        self.opt_skip_video = tk.Checkbutton(self.left_frame, text="Skip video", 
                                             bg=self.bg_color1, variable=self.opt_skip_video_var)
        self.opt_skip_video.pack(side=tk.TOP, anchor="w")

        # Commencer
        self.start = tk.Button(self.left_frame, text="Commencer", width=30, command=self.start_scrap)
        self.start.pack(side=tk.TOP, expand=True)


        # ============= Frame sep ============= 
        sep = tk.Frame(self.main_frame, height=self.height, highlightthickness=0, background="black", width=2)
        sep.pack(side=tk.LEFT, fill=tk.Y)

        # ============= Frame droite ============= 
        self.right_frame = tk.Frame(self.main_frame, height=self.height ,background=self.bg_color1, highlightthickness=0, width=self.width * 2//3)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH,expand=True)
        self.right_frame.pack_propagate(False)

    def start_scrap(self) :
        # Lancer la tâche longue dans un thread séparé
        threading.Thread(target=self.scrap, daemon=True).start()

    def scrap(self) :
        """
        Fonction pour scrapper le site
        """

        # Récupération de l'adresse du site
        self.act_website = self.input_website.get()
        if not(self.act_website) :
            return
        
        # Récupération du chemin de sauvegarde
        self.base_save_path = self.search_folder_input.get()
        if not(self.base_save_path) :
            return
        
        #option
        SKIP_SEEN_PAGE = self.opt_skip_seen_page_var.get()  
        SKIP_IMAGE = self.opt_skip_image_var.get()
        SKIP_VIDEO = self.opt_skip_video_var.get()
        

        # Initialisation
        self.init_main_dir()
        self.start["state"] = "disabled"

        # Visite de toutes les pages ayant pour base website
        while (self.next_path) :
            time.sleep(0.05)

            # Récupération du site web et génération du nom du dir
            page_to_scrape = requests.get(self.next_path[0], headers=self.headers)
            subfolder_name = self.get_folder_name(self.next_path[0],)
            act_save_path = os.path.join(self.base_save_path, subfolder_name)

            # Vérification si cette page avait déjà été visité
            SKIP_PAGE = False
            if (os.path.exists(os.path.join(act_save_path, self.default_name_html)) and SKIP_SEEN_PAGE) :
                SKIP_PAGE = True

            # Vérification du type de média 
            content_type = self.get_format_content_type(page_to_scrape.headers["content-type"])
            NOT_TEXT = False
            if (content_type != "text") :
                NOT_TEXT = True
                SKIP_PAGE = True
            else :
                try :
                    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
                except Exception as e:
                    error_load_file = f"Impossible d'utiliser beautifulSoup sur {self.next_path[0]}. Erreur : {e}\n"
                    error_load_file += "===========================================================================\n"
                    save_error_load_file = os.path.join(self.base_save_path, "error_load_file.txt")
                    with open(save_error_load_file, "a", encoding="utf-8") as file:
                        file.write(error_load_file)
                    continue

            # création des dossiers
            os.makedirs(act_save_path, exist_ok=True)
            if not(SKIP_IMAGE) :
                os.makedirs(os.path.join(act_save_path, "imgs"), exist_ok=True)
            if not (SKIP_VIDEO) :
                os.makedirs(os.path.join(act_save_path, "videos"), exist_ok=True)

            # ============= Récupération de la page ============= 
            if (not(SKIP_PAGE) and (content_type == "text")) :
                self.get_page(soup, act_save_path)

            # ============= Récupération des images ============= 
            if not(SKIP_IMAGE) and not(SKIP_PAGE) :
                self.get_image(soup, act_save_path)

            # ================ cas non page html ================
            if (NOT_TEXT) :
                if (((content_type == "video") or (content_type == "audio")) and not(SKIP_VIDEO)) :
                    save_path_video_page = os.path.join(act_save_path, "videos", os.path.basename(self.next_path[0]))
                    
                    # Sauvegarder le fichier dans le répertoire local
                    with open(save_path_video_page, "wb") as file:
                        file.write(page_to_scrape.content)

                if (content_type == "pdf") :
                    save_path_pdf = os.path.join(act_save_path, os.path.basename(self.next_path[0]))
                    
                    with open(save_path_pdf, 'wb') as file:
                        file.write(page_to_scrape.content)

            # ============== Recuperation des liens ==============
            self.already_seen_path.append(self.next_path[0])
            if (not(NOT_TEXT)) :
                self.get_link(soup)
            del self.next_path[0]




    def get_path_folder(self) :
        # Ouvre une boîte de dialogue pour sélectionner un dossier
        directory_path = filedialog.askdirectory(title="Sélectionner un dossier")
        if directory_path:
            self.search_folder_input.delete(0, tk.END)
            self.search_folder_input.insert(0, directory_path)

    def init_main_dir(self) :
        """
        Fonction pour créer le dossier qui contiendra toutes les pages du sites
        """
        # Vérification que le chemon ne se soit pas vide
        if not(self.act_website) :
            return
        
        self.base_save_path = os.path.join(self.base_save_path ,ScrapGui.get_folder_name(self.act_website))
        
        # Création des fichiers
        os.makedirs(self.base_save_path, exist_ok=True)
        with open(os.path.join(self.base_save_path, "error_load_file.txt"), "w") :
            pass

        # 
        self.next_path = [self.act_website]
        self.already_seen_path = [self.act_website + "/"]
        self.website_images = []

    def get_page(self, soup, path) :
        """
        Récupère la page du site web
        """       
        html_content = soup.prettify()  # .prettify() rend le code HTML plus lisible
        save_html_page = os.path.join(path, self.default_name_html)
        # Sauvegarder le HTML dans un fichier
        with open(save_html_page, "w", encoding="utf-8") as file:
            file.write(html_content)

    def get_image(self, soup, path) :
        error_dwl_img = ""                               # chaine de sauvegarde des erreurs
        for balise_img in soup.findAll("img") :
            # Récupération de l'image via la balise
            picHttp = balise_img.get("src")

            # Vérification si l'image a déjà été croisé
            if (picHttp in self.website_images) :
                continue
            else :
                self.website_images.append(picHttp)

            # vérification du chemin de l'image s'il est relatifs
            picHttp = urljoin(self.next_path[0], picHttp)

            # Request l'image
            try :
                picReq = requests.get(picHttp, headers=self.headers)
            except Exception as e:
                error_dwl_img += f"Erreur Sur récupération des images :, {e}\n"
                error_dwl_img += f"nom de la page : {self.next_path[0]}\n"
                error_dwl_img += f"nom de la page image : {picHttp}\n"
                error_dwl_img += "=========================================\n"
                continue

            # Vérifiez si la réponse est correcte et que c'est bien une image
            if picReq.status_code == 403:
                error_dwl_img += f"{picHttp} - Erreur: Forbidden\n"
                error_dwl_img += "=========================================\n"
                continue          
            elif 'image' not in picReq.headers.get('Content-Type', ''):
                error_dwl_img += f"{picHttp} - Ce n'est pas une image\n"
                error_dwl_img += "=========================================\n"
                continue
            #si il y'a une erreur on garde l'adresse de l'image
            elif picReq.status_code == 404 :
                error_dwl_img += f"{picHttp} - L'adresse n'existe pas \n"
                error_dwl_img += "=========================================\n"
                continue
            elif picReq.status_code != 200:
                error_dwl_img += f"{picHttp} - Erreur: {picReq.status_code}\n"
                error_dwl_img += "=========================================\n"
                continue

            #Nom de l'image
            picName = self.get_folder_name(picHttp)

            #Télécharger l'image
            save_path_img = os.path.join(path, "imgs", picName)       
            if not(os.path.exists(save_path_img)) :
                with open(save_path_img, "wb") as f:
                    f.write(picReq.content)

            time.sleep(0.1)

        #sauvegarde des adresses erronées
        if error_dwl_img :
            save_path_error_img = os.path.join(path, "imgs", "error_dwl_img.txt")
            with open(save_path_error_img, "w") as f:
                f.write(error_dwl_img)


    def get_link(self, soup) :
        for link in soup.findAll("a") :
            link_name = link.get("href")

            # lien vide
            if not(link_name) :
                continue

            # vérifier les entêtes
            ignore = False
            for ignore_header in self.ignore_headers :
                if link_name.startswith(ignore_header) :
                    ignore = True
                    break
                
            if ignore :
                continue

            # Joindre les parties urls
            link_name = urljoin(self.next_path[0], link_name, False)

            # Url a déjà été visité
            if link_name in self.already_seen_path:
                continue

            # Url va être visité
            elif link_name in self.next_path :
                continue

            # Ne pas sortir du site
            elif not(link_name.startswith(self.act_website)) :
                continue

            self.next_path.append(link_name)

    @staticmethod
    def get_format_content_type(content_type) :
        if (content_type.strip().startswith("audio")) :
            return "audio"
        elif (content_type.strip().startswith("video")) :
            return "video"
        elif ("pdf" in content_type.strip()) :
            return "pdf"
        else :
            return "text"

    @staticmethod
    def get_folder_name(website_name) :
        """
        Fonction pour formater le nom des dossiers
        """
        to_replace_dict = {
            "https://" : "",
            "http://" : "",
            "/" : "_"
        }

        temp = urlparse(website_name).path
        if (temp) :
            website_name = temp


        for key, value in to_replace_dict.items() :
            website_name = website_name.replace(key, value) 

        # Suppresion de char invalide
        website_name = re.sub(r'[<>:"/\\|?*]', '_', website_name).lstrip("_").strip()

        # Vérification du nombre de char
        if len(website_name) >= 255 :
            website_name = website_name[:250] + "..."

        return website_name
    



        
        



fen = ScrapGui()
fen.mainloop()


# def open_directory_dialog():
#     # Ouvre une boîte de dialogue pour sélectionner un dossier
#     directory_path = filedialog.askdirectory(title="Sélectionner un dossier")
#     if directory_path:
#         print("Dossier sélectionné :", directory_path)

# # Créer la fenêtre principale
# root = tk.Tk()
# root.title("Sélectionner un dossier")

# # Bouton pour ouvrir la boîte de dialogue
# button = tk.Button(root, text="Sélectionner un dossier", command=open_directory_dialog)
# button.pack(pady=20)

# # Démarrer l'application Tkinter
# root.mainloop()