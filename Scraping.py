import csv
from email import header
import json
from threading import local
from bs4 import BeautifulSoup
import requests
import bs4
import os

# Получаем полный путь от данного файла и локальный от данного файла к файлу по локальному пути
def local_path(local_path):
    return os.path.join(os.path.dirname(__file__), local_path)

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
}


# # Получаем все списки членов партий
# for i in range(0, 740, 20):
#     url = f"https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset={i}"

#     req = requests.get(url, headers=headers)
#     src = req.text
    
#     with open(local_path(f"data/members_{i}.html"), "w", encoding="utf-8") as file:
#         file.write(src)

# # Получаем ссылки страниц членов партии и записываем в csv файл
# count = 0
# for i in range(0, 740, 20):
#     with open(local_path(f"data/members_{i}.html"), encoding="utf-8") as file:
#         src = file.read()
        
#     soup = BeautifulSoup(src, "lxml")
#     members_urls = soup.find_all(class_="bt-slide-content")
    
#     for member_url in members_urls:
#         url = member_url.find("a").get("href")
        
#         with open(local_path(f"members.csv"), "a", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow([url])
            
#         count += 1
#         print(f"Записано {count} членов партии...")
        
# print("Запись членов партии завершенна...")

# # Получаем страницы членов партии
# with open(local_path("members.csv")) as file:
#     reader = csv.reader(file)
    
#     count = 0
#     for row in reader:
#         url = row[0]
#         name = url.split("/")[-1].split("-")[0]
        
#         req = requests.get(url, headers=headers)
#         src = req.text
        
#         with open(local_path(f"members/{count}_member.html"), "w", encoding="utf-8") as file:
#             file.write(src)
            
#         print(f"Страница {count} сохранена")
#         count += 1

# Получаем информацию о членах партии
members_info = []

for count in range(97, 737): # 737
    with open(local_path(f"members/{count}_member.html"), encoding="utf-8") as file:
        src = file.read()
        soup = BeautifulSoup(src, "lxml")
        
        member_info = {}
        
        name = soup.find(class_="col-xs-8 col-md-9 bt-biografie-name").find("h3").text.split(", ")[0].strip()
        member_info.update({"name": name})
        
        links = soup.find(class_="bt-linkliste").find_all("a")
        for link in links:
            title = link.get("title")
            link = link.get("href")
            member_info.update({title: link})
            
        members_info.append(member_info)     
        
        print(f"Член партии номер: {count} сохранен, осталось {737-count}...")

with open(local_path("members_info.json"), "w", encoding="utf-8") as file:
    json.dump(members_info, file, indent=4, ensure_ascii=False)