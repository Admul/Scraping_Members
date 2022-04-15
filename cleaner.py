import os
import threading

cur_dir = os.getcwd()

def main_dir_del():
    try:
        os.remove("members.csv")
        os.remove("members_info.json")
        print("members.csv and members_info.json deleted")
    except: pass
    
def data_dir_del():
    files = os.listdir('./data')
    print(files)
    for file in files:
        os.remove(f"./data/{file}")
        print(f'data/{file} deleted')
        

def members_dir_del():
    files = os.listdir('./members')
    print(files)
    for file in files:
        os.remove(f"./members/{file}")
        print(f'members/{file} deleted')
        
def start():
    main_dd = threading.Thread(target=main_dir_del)
    data_dd = threading.Thread(target=data_dir_del)
    members_dd = threading.Thread(target=members_dir_del)

    main_dd.start()
    data_dd.start()
    members_dd.start()
