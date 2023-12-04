import sys
from pathlib import Path
import re
import os
import shutil
import time

files_list = {'images':('.jpeg', '.png', '.jpg', '.svg'),
    'video':('.avi', '.mp4', '.mov', '.mkv'),
    'documents':('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
    'audio':('.mp3', '.ogg', '.wav', '.amr'),
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
    *x_root, name = root.split(os.sep)
    clear_name = re.sub('\W+', '_', name)
    x_root.append(translate(clear_name))
    
    return os.sep.join(x_root)

def translate(name):
    en_name = name.translate(TRANS)
    
    return en_name

def unpack_archive(path):
    if path.name == 'archives':
        for archive in path.iterdir():
            file_name = archive.name.split(".")[0]
            os.mkdir(os.path.join(user_input, path.name, file_name))
            try:
                shutil.unpack_archive(str(archive), os.path.join(user_input, path.name, file_name))
            except shutil.ReadError:
                os.rmdir(os.path.join(user_input, path.name, file_name))
            os.remove(str(archive))

def parse_folder(path):
    
    if path.is_file():
        try:
            if os.path.splitext(path)[1].lower() in files_list['images']:
                shutil.copy(str(path), os.path.join(user_input, 'images'))
                os.remove(path)
        
            elif os.path.splitext(path)[1].lower() in files_list['video']:
                shutil.copy(str(path), os.path.join(user_input, 'video'))
                os.remove(path)
        
            elif os.path.splitext(path)[1].lower() in files_list['documents']:
                shutil.copy(str(path), os.path.join(user_input, 'documents'))
                os.remove(path)
        
            elif os.path.splitext(path)[1].lower() in files_list['audio']:
                shutil.copy(str(path), os.path.join(user_input, 'audio'))
                os.remove(path)
        
            elif os.path.splitext(path)[1].lower() in files_list['archives']:
                shutil.copy(str(path), os.path.join(user_input, 'archives'))
                os.remove(path)
        
            elif os.path.splitext(path)[1].lower() in files_list['others']:
                shutil.copy(str(path), os.path.join(user_input, 'others'))
                os.remove(path)

            else:
                shutil.copy(str(path), os.path.join(user_input, 'others'))
                os.remove(path)

                
        except shutil.SameFileError:
            pass
                   
    elif path.is_dir():
        dir_name = re.compile(path.name)
        matches = list(filter(dir_name.fullmatch, created_folders))
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

            known_ext_list = []
            for value in files_list.values():
                for ext in value:
                    known_ext_list.append(ext)
        
            unknown_ext = ()
            for file in path.glob('**/*'):
                if os.path.splitext(file)[1].lower() not in known_ext_list and len(os.path.splitext(file)[1]) != 0:
                    unknown_ext = unknown_ext + (os.path.splitext(file)[1],)
       
            files_list["others"] = tuple(set(unknown_ext))
            print(f"The list of all extensions known to the script\n {files_list}")

            for key in files_list.keys():
                try:
                    os.mkdir(os.path.join(user_input, key))
                except FileExistsError:
                    pass
                created_folders.append(key)

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
                        if ext.lower() == extension:
                            files_list_result.get(category_name).append(Path(new_name).name)
            
            print(f"The list of all files in each category\n {files_list_result}")
            

if __name__ == '__main__':
    main()