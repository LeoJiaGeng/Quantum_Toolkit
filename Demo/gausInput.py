from Public.Files import ReFilenames, SaveFile
from Public.GetGaussData import FindInfo
from Public.common import *
import os


class GauInput():
    def __init__(self):
        self.cur_folder = os.getcwd()
        pass

    def _process_gauss_input(self, filename, prefix, suffix, exec_type, read_type, mode):
        # 处理单个文件，传过来是文件绝对路径
        # 1、处理文件名
        pure_name = os.path.splitext(os.path.basename(filename))[0]
        file_folder = os.path.dirname(filename)

        # 2、设置文件的前后缀，默认gif文件
        prefix = prefix + "-" if prefix else prefix
        suffix = "-" + suffix if suffix else suffix

        # 4、设置check的名称
        chk_name = prefix + pure_name + suffix
        # 设置新文件名
        new_filename = os.path.join(file_folder, chk_name + ".gjf")

        write_file = SaveFile()

        # 3、读取文件内容
        read_obj = FindInfo()
        read_content = []

        # 注意：特殊处理MOD-GJF和IRC-GJF，并且它们优先级最高，高于文件类型判断
        if exec_type == "MOD-GJF" or exec_type == "IRC-GJF":
            read_content = read_obj.get_scan_irc_frames(filename)

            for i, each_frame in enumerate(read_content):
                xyz_list = each_frame[:-1]
                charge, spin, read_file_type = each_frame[-1]
                new_file_name = os.path.join(file_folder, chk_name + f"{i}.gjf")
                write_content = self.replace_contents(exec_type, chk_name, xyz_list, charge, spin, mode)
                write_file.save(new_file_name, write_content)
            return 1

        if read_type == "GauOutFile":
            read_content = read_obj.get_out_coord_charge_spin_state(filename)
        elif read_type == "GauInFile":
            read_content = read_obj.get_input_coord_charge_spin_state(filename)
        # 返回二维数组，第一个是坐标，最后一个是charge、spin、文件类型
        xyz_list = read_content[:-1]
        charge, spin, read_file_type = read_content[-1]

        # 判断文件类型，进行写入
        if exec_type == "IRC-SPLIT" and read_file_type == "TS":
            new_file_name_f = os.path.join(file_folder, chk_name + "-f.gjf")
            write_content = self.replace_contents("IRC-F", chk_name, xyz_list, charge, spin, mode)
            write_file.save(new_file_name_f, write_content)
            new_file_name_r = os.path.join(file_folder, chk_name + "-r.gjf")
            write_content = self.replace_contents("IRC-R", chk_name, xyz_list, charge, spin, mode)
            write_file.save(new_file_name_r, write_content)
        elif exec_type == "CHANGE-LEVEL":
            if read_file_type == "TS":
                write_content = self.replace_contents("TS", chk_name, xyz_list, charge, spin, mode)
            elif read_file_type == "OPT":
                write_content = self.replace_contents("OPT", chk_name, xyz_list, charge, spin, mode)
            else:
                # 其他类型文件，暂时不处理
                return 0
            write_file.save(new_filename, write_content)
        elif exec_type == "IRC" and read_file_type == "TS":
            write_content = self.replace_contents(exec_type, chk_name, xyz_list, charge, spin, mode)
            write_file.save(new_filename, write_content)
        elif exec_type == "HIGH-SP":
            write_content = self.replace_contents(exec_type, chk_name, xyz_list, charge, spin, mode)
            write_file.save(new_filename, write_content)
        elif exec_type == "SPIN-TS":
            if spin / 2 == 0:
                spin_list = list(range(0, 20, 2))
            else:
                spin_list = list(range(1, 21, 2))
            for spin in spin_list:
                spin_chk_name = chk_name + "-spin" + str(spin)
                new_filename = os.path.join(file_folder, spin_chk_name + ".gjf")
                write_content = self.replace_contents(exec_type, spin_chk_name, xyz_list, charge, spin, mode)
                write_file.save(new_filename, write_content)

    # 获取模板，替换模板中的数据，返回完整数据
    def replace_contents(self, template_type, chk_name, coord, charge, spin, mode):
        file_list = []

        # 选择合适的文件模版
        if template_type == "IRC":
            file_template = "IRC-template.txt"
        elif template_type == "IRC-F":
            file_template = "IRC-F-template.txt"
        elif template_type == "IRC-R":
            file_template = "IRC-R-template.txt"
        elif template_type == "TS":
            file_template = "TS-template.txt"
        elif template_type == "OPT":
            file_template = "OPT-template.txt"
        elif template_type == "HIGH-SP":
            file_template = "HIGH-SP-template.txt"
        elif template_type == "IRC-GJF":
            file_template = "IRC-GJF-template.txt"
        elif template_type == "MOD-GJF":
            file_template = "MOD-GJF-template.txt"
        elif template_type == "SPIN-TS":
            file_template = "SPIN-TEST-template.txt"

        file_template = os.path.join(self.cur_folder, f"Model/{mode}/{file_template}")

        # 打开文件替换相应部分，返回替换内容
        with open(file_template, mode="r", encoding="utf-8") as file_obj:
            for line in file_obj.readlines():
                if "replace-name" in line:
                    line = line.replace("replace-name", chk_name)
                if "replace-coordinate" in line:
                    line = "\n".join(coord)
                if "replace-charge" in line:
                    line = line.replace("replace-charge", str(charge))
                if "replace-multiplicity" in line:
                    line = line.replace("replace-multiplicity", str(spin))
                file_list.append(line)

        return file_list

# ---------对外的接口函数----------
    def trans_folder(self, foldername, prefix, suffix, exec_type, read_type, mode, curdir):
        """读取指定文件夹内所有log文件，替换成新模板的输入文件，IRC和柔性SCAN自动屏蔽"""
        if read_type == "GauOutFile":
            name_obj = ReFilenames("out,log")
        if read_type == "GauInFile":
            name_obj = ReFilenames("gjf")

        for fileabsroute in name_obj.get_all_files(foldername, only_curdir=curdir):
            self._process_gauss_input(fileabsroute, prefix, suffix, exec_type, read_type, mode)
        return 1

    def trans_file(self, filename, prefix, suffix, exec_type, read_type, mode):
        """读取指定文件，替换成新模板的输入文件"""
        self._process_gauss_input(filename, prefix, suffix, exec_type, read_type, mode)
        return 1


if __name__ == '__main__':
    A = GauInput()
    B = A.create_gjfs(r"C:\Users\DELL\Desktop\transfer\test", suffix="-irc", file_type="IRC")
    # B = A.create_gjfs(r"C:\Users\DELL\Desktop\transfer\test",file_type="IRC")
    # C = A.read_coord_inputfile(r"E:\CF3SO2F\KF_SO2Cl\new\Gas\o-TS1-gas.gjf",True)
    # print (C)
    # D = A.replace_contents("A.gjf",C,"OPT")
    # print (D)
