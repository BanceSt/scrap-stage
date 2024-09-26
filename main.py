from bs4 import BeautifulSoup
import requests
import os
import time
import re

#"http://www.aux-antilles.fr/martinique/infos-pratiques/lexique-creole.htm",

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


#liste de site a visité
sites = [
    ("https://pawolotek.com", ""),
    ("http://pawolmizik.com", ""),
    ("https://azmartinique.com/fr/tout-savoir/proverbes-creoles", ""),
    ("https://www.dictionnaire-creole.com", ''),
    ("https://www.potomitan.info", '')
]



def get_folder_name(website_name) :
    """
    Fonction pour formater le nom des dossiers
    """
    to_replace_dict = {
        "https://" : "",
        "http://" : "",
        "/" : "__"
    }

    for key, value in to_replace_dict.items() :
        website_name = website_name.replace(key, value) 

    return re.sub(r'[<>:"/\\|?*]', '_', website_name)


# Visiter tous les sites
for i in range(2,3) :
    # Récupération de l'adresse du site et formatage du nom
    website = sites[i][0]
    folder_name = get_folder_name(website)
    
    
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
    sub_pages_already_visited = []


    # Visite de toutes les page ayant pour base website
    while (sub_pages) :
        time.sleep(0.05)
        # Récupération de la sous-page
        page_to_scrape = requests.get(sub_pages[0], headers={})
        subfolder_name = get_folder_name(sub_pages[0])
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        #création des dossiers
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}", exist_ok=True)
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\imgs", exist_ok=True)
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\videos", exist_ok=True)
        os.makedirs(f"sites\\{folder_name}\\{subfolder_name}\\others", exist_ok=True)

        # ================ Récupération de la page ====================================
        # Convertir l'objet BeautifulSoup en HTML formaté
        html_content = soup.prettify()  # .prettify() rend le code HTML plus lisible

        save_html_page = f"sites\\{folder_name}\\{subfolder_name}\\page.html"

        # Sauvegarder le HTML dans un fichier
        with open(save_html_page, "w", encoding="utf-8") as file:
            file.write(html_content)

        # ================ Récupération des images ====================================
        error_dwl_img = ""
        act_headers = headers
        for balise_img in soup.findAll("img") :
            #Récupération de l'image via la balise
            picHttp = balise_img.get("src")
            if (picHttp in images_website) :
                continue
            else :
                images_website.append(picHttp)

            try :
                picReq = requests.get(picHttp, headers=act_headers)
            except Exception as e:
                print("Erreur Sur récupération des images :", e)
                print("nom de la page :",sub_pages[0])
                print("=========================================")
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

        #sauvegarde des adresse erronée
        if error_dwl_img :
            save_path_error_img = f"sites\\{folder_name}\\{subfolder_name}\\imgs\\error_dwl_img.txt"
            with open(save_path_error_img, "w") as f:
                f.write(error_dwl_img)

        # ================ Récupération des vidéos ====================================
        error_dwl_videos = ""
        for balise_img in soup.findAll("video") :
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

        # ================ Récupération des vidéos dans le iframs ====================================
        vids_iframe = ""
        for balise_iframe in soup.findAll("iframe") :
            vids_iframe += balise_iframe.text + "\n"

        if (vids_iframe) :
            save_path_iframe_link = f"sites\\{folder_name}\\{subfolder_name}\\videos\\videos_link.txt"
            with open(save_path_iframe_link, "w") as f:
                f.write(vids_iframe)

         # ================ Récupération des links ====================================
        sub_pages_already_visited.append(sub_pages[0])
        del sub_pages[0]
        for link in soup.findAll("a") :
            time.sleep(0.15)
            link_name = link.get("href")
            print("link_name :", link_name)
            print("website :", website)
            if not(link_name) :
                print("++++++++++++++++++++++++++++++++++++++++++++++++")
                continue
            # Ne pas récupérer un chemin déja visité
            if link_name in sub_pages_already_visited :
                print("REFUSED link_name in sub_pages_already_visited")
                print("++++++++++++++++++++++++++++++++++++++++++++++++")
                continue
            elif link_name in sub_pages :
                print("REFUSED link_name in sub_pages")
                print("++++++++++++++++++++++++++++++++++++++++++++++++")
                continue
            # Ne pas sortir du site
            elif not(website in link_name) :
                print("REFUSED website in link_name")
                print("++++++++++++++++++++++++++++++++++++++++++++++++")
                continue

            print("++++++++++++++++++++++++++++++++++++++++++++++++")

            sub_pages.append(link_name)

        


    

    #Récupération des images
    # print(len(soup.findAll("img")))
    # print(len(soup.findAll("a")))
    # print(len(soup.findAll("video")))
    


