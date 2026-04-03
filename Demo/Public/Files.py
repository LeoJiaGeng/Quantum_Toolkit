'''查找文件夹内所有文件，当前目录，删除，重命名，指定的文件是否在其中
'''
import os


class ReFilenames():
    '''读取指定文件内，包括子文件夹所有的后缀名'''

    def __init__(self, format_end="log"):
        self.__format_end = tuple([s.strip() for s in format_end.split(',')])
        self.file_list = []

    def __str__(self) -> str:
        return self.suffix

    def __len__(self) -> int:
        return len(self.file_list)

    @property
    def suffix(self):
        return self.__format_end

    @suffix.setter
    def suffix(self, name):
        self.__format_end = name

    def _process_file(self, root_dir, file, only_name, without_suffix):
        if not only_name:
            file_name = os.path.join(root_dir, file)
            self.file_list.append(file_name)
        elif only_name and (not without_suffix):
            self.file_list.append(file)
        else:
            only_file_name = file.split(".")[0]
            self.file_list.append(only_file_name)

    def get_all_files(self, dir, only_name=False, without_suffix=False, only_curdir=False):
        '''获取文件夹内及其子文件夹中所有带有后缀为self.suffix的文件'''
        self.file_list = []
        if only_curdir:
            # 只处理当前目录
            for file in os.listdir(dir):
                if os.path.isfile(os.path.join(dir, file)) and file.endswith(self.suffix):
                    self._process_file(dir, file, only_name, without_suffix)
        else:
            # 处理当前目录及其子目录
            for root_dir, _, files in os.walk(dir):
                for file in files:
                    if file.endswith(self.suffix):
                        self._process_file(root_dir, file, only_name, without_suffix)

        if not self.file_list:
            print("没有匹配到该后缀名的文件")
        return self.file_list

    def sort_file_names(self):
        self.file_list.sort()

    def filename_and_fileabsroute(self, foldername, only_curdir=False):
        '''获取文件夹内所有文件的名字和绝对路径'''
        filename_list = self.get_all_files(foldername, only_name=True, without_suffix=True, only_curdir=only_curdir)
        fileroute_list = self.get_all_files(foldername, only_curdir=only_curdir)
        return zip(filename_list, fileroute_list)

    def get_all_files_in_folder(self, foldername, only_curdir=False):
        '''获取文件夹内所有文件
        Args:
            foldername: 目标文件夹路径
            only_curdir: 是否仅获取当前目录的文件（不递归子目录），默认为False
        '''
        file_list = []

        if only_curdir:
            # 只获取当前目录的文件（不递归）
            for entry in os.scandir(foldername):
                if entry.is_file():
                    file_list.append(entry.path)
        else:
            # 递归获取所有子目录的文件（原有逻辑）
            for root_dir, sub_dir, files in os.walk(foldername):
                for file in files:
                    file_list.append(os.path.join(root_dir, file))

        return file_list

    def delete_file(self, filename):
        '''删除文件'''
        if os.path.exists(filename):
            os.remove(filename)
            print("文件删除成功")
        else:
            print("文件不存在")

    def rename_file(self, old_name, new_name):
        '''重命名文件'''
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            print("文件重命名成功")
        else:
            print("文件不存在")

    def is_file_in_folder(self, filename, foldername):
        '''判断文件是否在文件夹内'''
        file_list = self.get_all_files_in_folder(foldername)
        if filename in file_list:
            return True
        else:
            return False

    def get_file_detail(self, filename):
        '''获取文件详细信息'''
        file_folder = os.path.split(filename)[0]
        file_name = os.path.split(filename)[1]
        raw_name = os.path.splitext(file_name)[0]
        file_suffix = os.path.splitext(file_name)[1]
        # file_size = os.path.getsize(filename)
        # file_time = os.path.getctime(filename)
        return file_folder, file_name, raw_name, file_suffix

    def combine_file(self, file_folder, raw_name, file_suffix):
        '''合并文件'''
        new_name = os.path.join(file_folder, raw_name + file_suffix)
        return new_name


class SaveFile(object):
    def __init__(self):
        pass

    def save_n(self, filename, dataList):
        with open(filename, mode="+a", encoding="utf-8") as file_obj:
            for data in dataList:
                file_obj.write(str(data) + "\n")
            file_obj.close()

    def save(self, filename, dataList):
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, mode="+a", encoding="utf-8") as file_obj:
            for data in dataList:
                file_obj.write(str(data))
            file_obj.close()


class OpenFile(object):
    def __init__(self):
        pass

    def read_file(self, file_name, location=None, length=-1):
        with open(file_name, "r", encoding="utf-8") as file_obj:
            file_obj.seek(location)
            content = file_obj.read(length)
            return content

    """在windows下打开文件，显示文件界面"""

    def open_file(self, file_location):
        os.startfile(file_location)
        print("finshed!")


class CreateFile(object):
    def __init__(self):
        pass

    def creat_file(self, file_name):
        pass


if __name__ == "__main__":
    A = ReFilenames("txt")
    # print(A._read_all_files__format_end)
    # print(A.get_all_files(r"D:\Document\Python_Files\Project"))
    fi = A.get_all_files(r"E:\Python_Files\codehub\Quantum_10.12\Demo\Model\模式1-PM6", True)
    print(fi)
    for i in fi:
        print(i)
        # A.delete_file(i)
    print(len(fi))
