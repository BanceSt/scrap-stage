import re

print("Start")
pattern_date = r"\d{2}:\d{2} GMT / \d{2}\.\d{2}\.\d{4}"
pattern_fax_tel = r"(Tel[:.]?|Fax[:.]?)\s?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}"

# ouvrir le fichier 
with open("data\\raw_text.txt", "r", encoding='ISO-8859-1') as file :
    content = file.read()


new_content = re.sub(pattern_date, "", content)
new_content = re.sub(pattern_fax_tel, "", new_content)

with open("data\\raw_text_form1.txt", "w", encoding="ISO-8859-1") as file :
    file.write(new_content)

print("End")