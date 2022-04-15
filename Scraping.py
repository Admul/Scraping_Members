from cProfile import label
from email import header
from logging import root
from msilib.schema import Class
from operator import length_hint
from threading import Thread, local
from time import sleep
from tkinter import ttk
from tkinter import *
from turtle import pos
from bs4 import BeautifulSoup
from multiprocessing import Pool
from matplotlib.pyplot import text
from numpy import pad, place
from proxy_auth import proxies

import csv
import json
import requests
import bs4
import os
import sys
import threading
import time
import cleaner

class Parser():
    """
    Scraping members from www.bundestag.de
    """
    
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "content-language": "en"
        }
        
        self.gui()
        
    def start(self):
        
        self.work_state = True
        self.btn_clear['state'] = "disabled"
        self.btn_start.config(text='Cancel', command=self.cancel)
        
        gm_l = threading.Thread(target=self.get_members_list)
        gm_pl = threading.Thread(target=self.get_members_pages_links)
        gm_p = threading.Thread(target=self.get_members_pages)
        gm_i = threading.Thread(target=self.get_members_info)

        gm_l.start()
        gm_pl.start()

        gm_p.start()
        gm_i.start()
        
    def cancel(self):
        self.work_state = False
        self.clear()
        
        self.btn_clear['state'] = "normal"
        self.btn_start.config(text='Start', command=self.start)
        
    def gui(self):
        
        # GUI window
        self.root = Tk()
        self.root.title('Members scraper')
        self.root.geometry("800x600")
        
        # Progressbars and his labels
        self.gm_l_label = Label(self.root, text='Enter start button')
        self.gm_l_progress = ttk.Progressbar(self.root, orient=HORIZONTAL,
                                        length=300, mode='determinate')
        
        self.gm_pl_label = Label(self.root, text='Enter start button')
        self.gm_pl_progress = ttk.Progressbar(self.root, orient=HORIZONTAL,
                                         length=300, mode='determinate')
        
        self.gm_p_label = Label(self.root, text='Enter start button')
        self.gm_p_progress = ttk.Progressbar(self.root, orient=HORIZONTAL,
                                        length=300, mode='determinate')
        
        self.gm_i_label = Label(self.root, text='Enter start button')
        self.gm_i_progress = ttk.Progressbar(self.root, orient=HORIZONTAL,
                                        length=300, mode='determinate')
        
        self.gm_l_label.pack(pady=10)
        self.gm_l_progress.pack()
        
        self.gm_pl_label.pack(pady=10)
        self.gm_pl_progress.pack()
        
        self.gm_p_label.pack(pady=10)
        self.gm_p_progress.pack()
        
        self.gm_i_label.pack(pady=10)
        self.gm_i_progress.pack()
        
        # Buttons
        self.btn_start = Button(self.root, text='Start', command=self.start)
        self.btn_clear = Button(self.root, text='Clear', command=self.clear)
        
        self.btn_start.pack(pady=10)
        self.btn_clear.pack(pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", lambda c: self.root.destroy())
        self.root.mainloop()

    def clear(self):
        cleaner.start()
        
        self.gm_l_progress['value'] = 0
        self.gm_pl_progress['value'] = 0
        self.gm_p_progress['value'] = 0
        self.gm_i_progress['value'] = 0
    
    # Получаем полный путь от данного файла и локальный от данного файла к файлу по локальному пути
    def local_path(self, local_path): 
        return os.path.join(os.path.dirname(__file__), local_path)
    
    # Получаем все списки членов партий
    def get_members_list(self):
        
        point = 100/(740/20)
        
        for i in range(0, 740, 20):
            
            # Cancel progress
            if self.work_state == False:
                return 0
            
            url = f"https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset={i}"

            req = requests.get(url, headers=self.headers)
            src = req.text

            with open(self.local_path(f"data/members_{i}.html"), "w", encoding="utf-8") as file:
                file.write(src)
                self.gm_l_label.config(text=f"members_{i}.html создан")
                
            self.gm_l_progress['value'] += point
        
        self.gm_l_progress['value'] = 100
    
    # Получаем ссылки страниц членов партии и записываем в csv файл
    def get_members_pages_links(self):
        count = 0
        self.point = 100/740

        for i in range(0, 740, 20):
            while not os.path.exists(f"data/members_{i}.html"):
                time.sleep(0.1)

            with open(self.local_path(f"data/members_{i}.html"), encoding="utf-8") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            members_urls = soup.find_all(class_="bt-slide-content")

            for member_url in members_urls:
                
                # Cancel progress
                if self.work_state == False:
                    return 0
                
                url = member_url.find("a").get("href")

                with open(self.local_path(f"members.csv"), "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([url])

                count += 1
                self.gm_pl_progress['value'] += self.point
                self.gm_pl_label.config(
                    text=f"Записано {count} членов партии...")

        self.gm_pl_progress['value'] = 100
        self.gm_pl_label.config(text="Запись членов партии завершенна.")

    # Получаем страницы членов партии
    def get_members_pages(self):
        
        while not os.path.exists(f"members.csv"):
            time.sleep(0.1)
        
        with open(self.local_path("members.csv")) as file:
            reader = csv.reader(file)
                
            count = 0
            for row in reader:
                # Cancel progress
                if self.work_state == False:
                    return 0
                
                url = row[0]
                    
                req = requests.get(url, headers=self.headers, proxies=proxies)
                src = req.text
                    
                with open(self.local_path(f"members/{count}_member.html"), "w", encoding="utf-8") as file:
                    file.write(src)
                        
                self.gm_p_progress['value'] += self.point
                self.gm_p_label.config(text=f"Страница {count} сохранена")
                count += 1
                
                time.sleep(2)
                
        self.gm_p_progress['value'] = 100
        self.gm_p_label.config(text="Все страницы сохранены")

    #Получаем информацию о членах партии
    def get_members_info(self):
        members_info = []

        for count in range(0, 737): # 737
            
            # Cancel progress
            if self.work_state == False:
                return 0
            
            while not os.path.exists(f"members/{count}_member.html"):
                time.sleep(0.1)
                
            with open(self.local_path(f"members/{count}_member.html"), encoding="utf-8") as file:
                src = file.read()
                soup = BeautifulSoup(src, "lxml")
                    
                member_info = {}
                    
                try:
                    name = soup.find(class_="col-xs-8 col-md-9 bt-biografie-name").find("h3").text.split(", ")[0].strip()
                    member_info.update({"name": name})
                        
                    links = soup.find(class_="bt-linkliste").find_all("a")
                    for link in links:
                        title = link.get("title")
                        link = link.get("href")
                        member_info.update({title: link})
                            
                    members_info.append(member_info)

                    self.gm_i_progress['value'] += self.point
                    self.gm_i_label.config(
                        text=f"Член партии номер: {count} сохранен, осталось {737-count}...")
                except:
                    self.gm_i_progress['value'] += self.point
                    self.gm_i_label.config(
                        text=f"Член партии номер: {count} сохранен, осталось {737-count}...")
                    self.gm_i_label.config(
                        text=f"==ERROR== Член партии номер: {count} НЕ сохранен...")
                    
        time.sleep(1/2)

        with open(self.local_path("members_info.json"), "w", encoding="utf-8") as file:
            json.dump(members_info, file, indent=4, ensure_ascii=False)
            
        self.gm_i_progress['value'] = 100
        self.gm_i_label.config(text="Все члены партии сохранены")
    
        
if __name__=='__main__':
    parser = Parser()
    parser.start()
