from pathlib import Path
from glob import glob
import os

def check_unique_directory(dir_name="./output") ->str:
    #이전에 만들어 진적이 없는 새로운 폴더이름을 준다.
    cnt = 0
    new_dir_name = dir_name
    while os.path.exists(new_dir_name): # during not exists dir_name
        cnt += 1
        new_dir_name = dir_name + str(cnt)
    return new_dir_name

def create_directory(dir_name) -> str:
    # return directory name
    try:
        dir_name = os.path.abspath(dir_name)
        if not os.path.exists(dir_name):
            print("Create File : " + dir_name)
            os.makedirs(dir_name)
    except OSError:
        print('Check_directory Error: Creating directory. ' + dir_name)
        raise OSError
    return dir_name

    