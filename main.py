from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import os
import time
import re

#"http://www.aux-antilles.fr/martinique/infos-pratiques/lexique-creole.htm",

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

SKIP_SEEN_PAGE = True
SKIP_IMAGE = True
SKIP_VIDEO = False


#liste de site a visité
sites = [
    ("https://pawolotek.com", 1),
    ("http://pawolmizik.com", 1),
    ("https://azmartinique.com/fr/tout-savoir/proverbes-creoles", 0),
    ("https://www.dictionnaire-creole.com", 1),
    # ("https://www.potomitan.info/kebek/mois_creole_2024.mp4", 1),
    ("https://www.potomitan.info", 1)
]

#liste d'entete de link à ignorer

ignore_headers = {
    "#",
    "javascript:"
}


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


    website_name = re.sub(r'[<>:"/\\|?*]', '_', website_name).lstrip("_").strip()

    return website_name

def get_format_content_type(content_type) :
    if (content_type.strip().startswith("audio")) :
        return "audio"
    elif (content_type.strip().startswith("video")) :
        return "video"
    elif ("pdf" in content_type.strip()) :
        return "pdf"
    else :
        return "text"



# Visiter tous les sites
for i in range(4,5) :
    # Récupération de l'adresse du site et formatage du nom
    website = sites[i][0]
    folder_name = get_folder_name(website)
    error_load_file = ""
    
    
    
    #récupération de la page
    page_to_scrape = requests.get(website, headers=headers)
    if page_to_scrape.status_code == 200:
        act_headers = {}
        print("Page chargée avec succès.")
    else:
        print(f"Erreur lors du chargement de la page : {page_to_scrape.status_code}")
        act_headers = headers
        page_to_scrape = requests.get(website, headers=act_headers)
        folder_name += "__" + str(page_to_scrape.status_code)

    #création des fichiers
    os.makedirs(f"sites\\{folder_name}", exist_ok=True)
        
    # Sauvegarde des pages, des images
    sub_pages = [website]
    images_website = []
    sub_pages_already_visited = [website + "/"]


    # Visite de toutes les page ayant pour base website
    while (sub_pages) :
        time.sleep(0.05)
        # Récupération de la sous-page
        print("Current adresse : ", sub_pages[0])
        print("**********************************************************")
        page_to_scrape = requests.get(sub_pages[0], headers={})
        subfolder_name = get_folder_name(sub_pages[0])
        
        # Voir si le site avait été visité precedement
        SKIP_PAGE = False
        if (os.path.exists(f"sites\\{folder_name}\\{subfolder_name}") and SKIP_SEEN_PAGE) :
            SKIP_PAGE = True

        # Vérification du type de média 
        content_type = get_format_content_type(page_to_scrape.headers["content-type"])
        NOT_TEXT = False
        if (content_type != "text") :
            NOT_TEXT = True
            SKIP_PAGE = True

        #création des dossiers
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}", exist_ok=True)
        if not(SKIP_IMAGE) :
            os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\imgs", exist_ok=True)
        if not (SKIP_VIDEO) :
            os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\videos", exist_ok=True)
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\others", exist_ok=True)

        


        # ================ Récupération de la page ====================================
        # Convertir l'objet BeautifulSoup en HTML formaté
        if (content_type == "text") :
            try :
                soup = BeautifulSoup(page_to_scrape.text, "html.parser")
            except e:
                error_load_file += f"Impossible d'utiliser beautifulSoup sur {sub_pages[0]}. Erreur : {e}\n"
                save_error_load_file = f"sites\\{folder_name}\\error_load_file.txt"
                with open(save_error_load_file, "w", encoding="utf-8") as file:
                    file.write(error_load_file)
                continue
                


            html_content = soup.prettify()  # .prettify() rend le code HTML plus lisible
            save_html_page = f"sites\\{folder_name}\\{subfolder_name}\\page.html"

            # Sauvegarder le HTML dans un fichier
            with open(save_html_page, "w", encoding="utf-8") as file:
                file.write(html_content)

        # ================ Récupération des images ====================================
        if not(SKIP_IMAGE) and not(SKIP_PAGE) :
            error_dwl_img = ""                               # chaine de sauvegarde des erreurs
            act_headers = headers
            for balise_img in soup.findAll("img") :
                print("Image here")
                #Récupération de l'image via la balise
                picHttp = balise_img.get("src")

                #Vérification si l'image a déjà été croisé
                if (picHttp in images_website) :
                    continue
                else :
                    images_website.append(picHttp)

                #vérification du chemin de l'image s'il est relatifs
                picHttp = urljoin(website, picHttp)


                try :
                    picReq = requests.get(picHttp, headers=act_headers)
                except Exception as e:
                    print("Erreur Sur récupération des images :", e)
                    print("nom de la page :",sub_pages[0])
                    print("nom de la page image :",picHttp)
                    print("=========================================")
                    error_dwl_img += f"Erreur Sur récupération des images :, {e}\n"
                    continue
            

                
                # Vérifiez si la réponse est correcte et que c'est bien une image
                if picReq.status_code == 403:
                    error_dwl_img += f"{picHttp} - Erreur: Forbidden\n"
                    continue
                    
                elif 'image' not in picReq.headers.get('Content-Type', ''):
                    error_dwl_img += f"{picHttp} - Ce n'est pas une image\n"
                    continue
                #si il y'a une erreur on garde l'adresse de l'image
                elif picReq.status_code == 404 :
                    error_dwl_img += f"{picHttp} - L'adresse n'existe pas \n"
                    continue
                elif picReq.status_code != 200:
                    error_dwl_img += f"{picHttp} - Erreur: {picReq.status_code}\n"
                    continue
                
                #Nom de l'image
                picName = get_folder_name(picHttp)

                #Télécharger l'image
                save_path_img = f"sites\\{folder_name}\\{subfolder_name}\\imgs\\{picName}"
                if not(os.path.exists(save_path_img)) :
                        with open(save_path_img, "wb") as f:
                            f.write(picReq.content)

                time.sleep(0.1)

            #sauvegarde des adresses erronées
            if error_dwl_img :
                save_path_error_img = f"sites\\{folder_name}\\{subfolder_name}\\imgs\\error_dwl_img.txt"
                with open(save_path_error_img, "w") as f:
                    f.write(error_dwl_img)
            print(f"images fini pour {sub_pages[0]}")

        # ================ Récupération des vidéos ====================================
        if not(SKIP_VIDEO) and not(SKIP_PAGE) :
            error_dwl_videos = ""
            for balise_img in soup.findAll("video") :
                print("vidéo here")
                #Récupération de la vidéo via la balise
                vidHttp = balise_img.get("src")

                # Télécharger la vidéo
                try:
                    print(f"Téléchargement de la vidéo depuis : {vidHttp}")
                    video_response = requests.get(vidHttp, stream=True)
                    
                    # Vérifiez si la requête pour la vidéo a été effectuée avec succès
                    if video_response.status_code == 200:
                        # Nom du fichier de sortie
                        file_name = f"sites\\{folder_name}\\{subfolder_name}\\videos\\{get_folder_name(vidHttp)}"
                        # Enregistrer la vidéo
                        with open(file_name, 'wb') as file:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"Vidéo enregistrée sous : {file_name}")
                    else:
                        print(f"Erreur lors du téléchargement de la vidéo : {video_response.status_code}")
                
                except Exception as e:
                    print(f"Erreur lors du téléchargement de la vidéo : {e}")

                # break
            print(f"vidéos fini pour {sub_pages[0]}")

        # ================ Récupération des vidéos dans le iframs ====================================
        if (not(NOT_TEXT)) :
            vids_iframe = ""
            for balise_iframe in soup.findAll("iframe") :
                vids_iframe += balise_iframe.text + "\n"

            if (vids_iframe) :
                save_path_iframe_link = f"sites\\{folder_name}\\{subfolder_name}\\videos\\videos_link.txt"
                with open(save_path_iframe_link, "w") as f:
                    f.write(vids_iframe)


        # ================ cas non page html ====================================
        if (NOT_TEXT) :
            if (((content_type == "video") or (content_type == "audio")) and not(SKIP_VIDEO)) :
                save_path_video_page = f"sites\\{folder_name}\\{subfolder_name}\\videos\\" + os.path.basename(sub_pages[0])

                # Sauvegarder le fichier dans le répertoire local
                with open(save_path_video_page, "wb") as file:
                    file.write(page_to_scrape.content)

            if (content_type == "pdf") :
                save_path_pdf = f"sites\\{folder_name}\\{subfolder_name}\\" + os.path.basename(sub_pages[0])
                with open(save_path_pdf, 'wb') as file:
                    file.write(page_to_scrape.content)


        # ================ Récupération des links ====================================
        sub_pages_already_visited.append(sub_pages[0])
        temp_sub_page = sub_pages[0]
        del sub_pages[0]
        if (not(NOT_TEXT)) :
            for link in soup.findAll("a") :
                link_name = link.get("href")
                # print("link_name :", link_name)
                # print("website :", website)

                # lien vide
                if not(link_name) :
                    continue

                # vérifier les entêtes
                ignore = False
                for ignore_header in ignore_headers :
                    if link_name.startswith(ignore_header) :
                        ignore = True
                        break
                
                if ignore :
                    continue

                # Joindre les parties urls
                link_name = urljoin(temp_sub_page, link_name, False)

                # Url a déjà été visité
                if link_name in sub_pages_already_visited :
                    # print("REFUSED link_name in sub_pages_already_visited")
                    # print("++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue
                # Url va être visité
                elif link_name in sub_pages :
                    # print("REFUSED link_name in sub_pages")
                    # print("++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue
                # Ne pas sortir du site
                elif not(link_name.startswith(website)) :
                    # print("REFUSED not website in link_name")
                    # print("++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue
                    

                # print("++++++++++++++++++++++++++++++++++++++++++++++++")

                sub_pages.append(link_name)

        


    

    #Récupération des images
    # print(len(soup.findAll("img")))
    # print(len(soup.findAll("a")))
    # print(len(soup.findAll("video")))
    


