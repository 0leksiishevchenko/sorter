import sys
from pathlib import Path
import re
import os
import shutil
import time

files_list = {'images':('.jpeg', '.png', '.jpg', '.svg'),
    'videos':('.avi', '.mp4', '.mov', '.mkv'),
    'documents':('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
    'music':('.mp3', '.ogg', '.wav', '.amr'),
    'archives':('.zip', '.gz', '.tar')}

created_folders = []

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
        
TRANS = {}
for ua_symb, en_symb in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(ua_symb.upper())] = en_symb.upper()
    TRANS[ord(ua_symb)] = en_symb   

def normalize(root):
    *x_root, name = root.split("\\")
    clear_name = re.sub('\W+', '_', name)
    x_root.append(translate(clear_name))
    
    return '\\'.join(x_root)

def translate(name):
    en_name = name.translate(TRANS)
    
    return en_name

def unpack_archive(path):
    if path.name == 'archives':
        for archive in path.iterdir():
            file_name = archive.name.split(".")[0]
            os.mkdir(f"{user_input}\\{path.name}\\{file_name}")
            shutil.unpack_archive(str(archive), f"{user_input}\\{path.name}\\{file_name}")
            os.remove(str(archive))

def parse_folder(path):
    
    if path.is_file():
        try:
            if os.path.splitext(path)[1] in files_list['images']:
                shutil.copy(str(path), f"{user_input}\\images")
                os.remove(path)
        
            if os.path.splitext(path)[1] in files_list['videos']:
                shutil.copy(str(path), f"{user_input}\\videos")
                os.remove(path)
        
            if os.path.splitext(path)[1] in files_list['documents']:
                shutil.copy(str(path), f"{user_input}\\documents")
                os.remove(path)
        
            if os.path.splitext(path)[1] in files_list['music']:
                shutil.copy(str(path), f"{user_input}\\music")
                os.remove(path)
        
            if os.path.splitext(path)[1] in files_list['archives']:
                shutil.copy(str(path), f"{user_input}\\archives")
                os.remove(path)
        
            if os.path.splitext(path)[1] in files_list['unknown']:
                shutil.copy(str(path), f"{user_input}")
                os.remove(path)
                
        except shutil.SameFileError:
            pass
                   
    elif path.is_dir():
        dir_name = re.compile(path.name)
        matches = list(filter(dir_name.match, created_folders))
        if len(matches) != 0:
            pass          
        else:
            for sub_path in path.iterdir():
                parse_folder(sub_path)
            os.rmdir(str(path))

def main():
    global user_input
    if len(sys.argv) < 2:
        user_input = ""
    else:
        user_input = sys.argv[1]

    path = Path(user_input)
    if path.exists():
        if path.is_dir():
            for key, value in files_list.items():
                os.mkdir(user_input+'/'+key)
                created_folders.append(key)

            known_ext_list = []
            for value in files_list.values():
                for ext in value:
                    known_ext_list.append(ext)
        
            unknown_ext = ()
            for file in path.glob('**/*'):
                if os.path.splitext(file)[1] not in known_ext_list and len(os.path.splitext(file)[1]) != 0:
                    unknown_ext = unknown_ext + (os.path.splitext(file)[1],)
       
            files_list["unknown"] = unknown_ext
            print(files_list)

            files_list_result = files_list.copy()
            for key in files_list_result.keys():
                files_list_result[key] = []
            
            for item in path.iterdir():
                parse_folder(item)
        
            for item in path.iterdir():
                unpack_archive(item)
           
            for file in path.glob('**/*'):
                root, ext = os.path.splitext(file)
                new_name = normalize(root) + ext
                os.rename(file, new_name)
                for category_name, extensions in files_list.items():
                    for extension in extensions:
                        if ext == extension:
                            files_list_result.get(category_name).append(Path(new_name).name)
            
            print(files_list_result)

if __name__ == '__main__':
    main()