'''
适配函数，完成所有的任务：对接界面函数。批量整理log文件的能量，频率和坐标
'''
import os
from Public.Files import ReFilenames
from Public.Excel import Excels
from Public.Word import WordDriver
from Public.GetGaussData import FindInfo


class Quantum(ReFilenames):
    def __init__(self, type, folder_name, stand_E="", stand_G="", only_curdir=True):
        super().__init__(type)
        self.folder_name = folder_name
        self.only_curdir = only_curdir
        self.full_data = []
        self.stand_E = self.is_empty(stand_E)
        self.stand_G = self.is_empty(stand_G)
        self.find_obj = FindInfo()

    def is_empty(self, str_obj):
        if str_obj == "":
            return str_obj
        else:
            return "Zero-point correction=\\s+([\\d.-]+)"

    def read_file(self, header, save_energy_type, save_file_format):
        # 多维数组（整体看是二维），第一行是标题，其余行是数据
        full_data = [header]

        for filename, fileabsroute in self.filename_and_fileabsroute(self.folder_name, self.only_curdir):
            # 二维列表，第一个元素是文件名，第二个元素是文件内容
            tranList = [filename]

            # 处理单个文件，可以一次性处理多种任务，读能量也可以读坐标、频率
            if (save_energy_type == "Single Energy"):
                content = self.find_obj.get_sp_energy(fileabsroute)
            elif (save_energy_type == "Freq Energy"):
                content = self.find_obj.get_freq_energy(fileabsroute)
            elif (save_energy_type == "Frequency"):
                content = self.find_obj.get_freqs(fileabsroute)
            elif (save_energy_type == "Coordinates"):
                content = self.find_obj.get_coord(fileabsroute, combine_symbol="   ")
            elif (save_energy_type == "Others"):
                content = self.find_obj.get_others(fileabsroute)
            elif (save_energy_type == "CBS Energy"):
                content = self.find_obj.get_cbs_energy(fileabsroute)
            elif (save_energy_type == "G4 Energy"):
                content = self.find_obj.get_g4_energy(fileabsroute)
            elif (save_energy_type == "Re match content"):
                content = self.find_obj.get_w1_energy(fileabsroute, self.stand_E, self.stand_G)
            elif (save_energy_type == "MultiCBS Energy"):
                content = self.find_obj.get_multi_cbs_energy(fileabsroute)
            elif (save_energy_type == "Support Information"):
                # 单独判断，提前结束本次循环
                xyz = self.find_obj.get_old_coord(fileabsroute)
                zpe = self.find_obj.get_zpe_energy(fileabsroute)
                hf = self.find_obj.get_sp_energy(fileabsroute)
                # 拆分路径
                dir_path = os.path.dirname(fileabsroute)
                filename = os.path.basename(fileabsroute)
                # 获取上级目录名并添加 -cbs
                parent_dir = os.path.basename(dir_path)
                new_parent_dir = parent_dir + "-cbs"
                # 获取祖父目录路径
                grandparent_dir = os.path.dirname(dir_path)
                # 处理文件名：添加 -mulcbs（保留原扩展名）
                name, ext = os.path.splitext(filename)
                new_filename = name + "-mulcbs" + ext
                # 拼接新路径
                new_path = os.path.join(grandparent_dir, new_parent_dir, new_filename)
                zpe_energy = "ZPE = " + str(zpe)
                hf_energy = "HF = " + str(hf)
                tranList.append(xyz)
                if os.path.exists(new_path):
                    multi_cbs = self.find_obj.get_multi_cbs_energy(new_path)
                    multi_cbs_energy = "CBS-QB3 = " + str(multi_cbs[-1])
                    tranList.append([zpe_energy, hf_energy, multi_cbs_energy])
                else:
                    tranList.append([zpe_energy, hf_energy])
                full_data.append(tranList)
                continue

            if isinstance(content, list):
                if (save_file_format == ".xlsx"):
                    tranList.extend(content)
                elif (save_file_format == ".docx"):
                    tranList.append(content)
            elif isinstance(content, str):
                tranList.append(content)
            else:
                tranList.append("Nan")
            full_data.append(tranList)

        return full_data

    def save_frame(self, header, new_filename, save_energy_type, save_file_format):
        # 读取传入文件夹，返回单个文件的数据，返回二维数组，如果没有直接跳过即可
        full_data = self.read_file(header, save_energy_type, save_file_format)
        # 返回带有表头的数据，去掉表头
        for i in full_data[1:]:
            if len(i) != 1:
                break
        else:
            return []

        # 开始写入数据
        if (save_file_format == ".xlsx"):
            excel_obj = Excels()
            excel_obj.write_excel_lines(full_data, filename=new_filename)
        elif (save_file_format == ".docx"):
            docx_obj = WordDriver(table_font_name="Times New Roman",
                                  table_font_size=7.5,   # 小四
                                  #  col_widths=[5, 8],    # 两列分别 5 cm、8 cm
                                  auto_adjust=True)
            if save_energy_type == "Frequency":
                heading = "分子频率"
            elif save_energy_type == "Coordinates":
                heading = "分子坐标"
            else:
                heading = "数据表"  # 默认标题
            docx_obj.write_table(full_data, filename=new_filename, heading=heading)
        return full_data[1:]

    def simple_info(self, filename):
        full_data = self.find_obj.simple_information(filename)
        for i in full_data[1:]:
            if len(i) != 1:
                break
        else:
            return []
        return full_data

    def detail_info(self, filename):
        full_data = self.find_obj.detail_information(filename)
        for i in full_data[1:]:
            if len(i) != 1:
                break
        else:
            return []
        return full_data


if __name__ == "__main__":
    nameType = "log"
    file_folder = r"E:\Research\AP\task-1130\二茂铁-AP\FeR2\Rate\R"
    # file_name = r"D:\data\C2F2O\C2F2_1.log"
    A = Quantum(nameType, file_folder)
    # B = Quantum(nameType, file_name)
