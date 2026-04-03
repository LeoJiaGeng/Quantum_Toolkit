import os
import shutil
import time
from Public.Files import ReFilenames


def rename(input_dir, file_list, rename_list):
    # 输入文件夹，文件夹内需要修改的文件(带后缀)，重命名的列表(不带后缀)
    for filename, rename in zip(file_list, rename_list):
        # get the file suffix
        portion = os.path.splitext(filename)
        # combine the old file suffix with the new name
        new_name = rename + portion[1]
        print("{} --> {}".format(filename, new_name))
        # print(os.path.join(input_dir,filename))
        # replace file name
        os.replace(os.path.join(input_dir, filename), os.path.join(input_dir, new_name))

    print("Coverting Success!")


def remove():
    # Read a temporary directory
    input_dir = r"C:\Users\DELL\Desktop\C4xianan1"
    input_suffix = "log"
    file_obj = ReFilenames(input_suffix)
    delete_list = file_obj.get_all_files(input_dir)
    for delete_file in delete_list:
        os.remove(delete_file)
        print("{} file was delete!".format(delete_file))

    print("total {} files, Success!".format(len(delete_list)))


def back_folder(folder):
    cur_time = "back_files" + time.strftime('%Y-%m-%d-%H', time.localtime())
    temp_folder = os.path.join(os.getcwd(), cur_time)
    if os.path.isdir(temp_folder):
        # 删除临时文件夹
        shutil.rmtree(temp_folder)
    # 备份文件内的文件,本身自带创建文件夹的功能，所以有就先删了
    shutil.copytree(folder, temp_folder)
    print(f"文件夹成功备份到{temp_folder}")
    return temp_folder


def recover_folder(back_folder, old_folder):
    shutil.rmtree(old_folder)
    shutil.copytree(back_folder, old_folder)
    print(f"文件夹从{back_folder}成功恢复到{old_folder}！")


if __name__ == "__main__":
    # rename()
    # remove()
    folder = r"C:\Users\DELL\Desktop\transfer\test"
    a = os.listdir(folder)
    b = ["test_" + str(i) for i in range(len(a))]
    bak_folder = back_folder(folder)  # 备份
    rename(folder, a, b)  # 修改
    recover_folder(bak_folder, folder)  # 恢复
