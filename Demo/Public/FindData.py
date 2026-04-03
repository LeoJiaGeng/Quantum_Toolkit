"""
查找log文件文件里面的零点能、吉布斯、HF的能量和虚频以及YES，返回数组!!!
"""
import math


class FindInfo():
    # 列表用于查找频率
    freq_key = ["Frequencies --",
                "Low"
                ]

    # 列表用于查找存在YES
    YES_keys = ["Maximum Force",
                "RMS     Force",
                "Maximum Displacement",
                "RMS     Displacement"
                ]

    def __init__(self, filename):
        """传入文件名，可以得到需要条件的数组"""
        self.filename = filename

    def str_to_digit(self, str_cont):
        """Converts a string with letter D+- to a digit"""
        cont_list = list(str_cont.strip().split("D+"))
        return round((float(cont_list[0]) * 10**int(cont_list[1])), 6)

    def str_list_to_2float(self, str_list):
        """Converts a string list to a digit"""
        ret_list = []
        for num in str_list:
            ret_list.append(str(round(float(num), 2)))
        return ret_list

    def eigenvectors(self, count=300):
        """检查未完成任务中的虚频，直接打印，不需要储存"""
        # 经过一步只输出一个虚频
        content_list = []
        with open(self.filename, mode="r", buffering=-1, encoding="utf-8") as fileObj:
            file_lines = fileObj.readlines()
            show = 0
            for line_num in range(len(file_lines)):
                if count <= 0:
                    break
                if "Step number" in file_lines[line_num]:
                    show = 1
                    count -= 1
                    # print("\n{}".format((file_lines[line_num]).strip()))
                    content_list
                if "Eigenvalues ---" in file_lines[line_num] and show == 1:
                    # print((file_lines[line_num]).strip())
                    content_list.append((file_lines[line_num]).strip())
                    content_list
                    show = 0
                if "Eigenvectors" in file_lines[line_num]:
                    content_list.append((file_lines[line_num + 1]).strip())
                    content_list.append(file_lines[line_num + 2].strip()[-48:])
                    # print((file_lines[line_num+1]).strip())
                    # print(file_lines[line_num+2].strip()[-48:])

        return content_list

    def eigenvectors_YES(self, count=300):
        """检查未完成任务中的虚频，直接打印，不需要储存"""
        """检查是否存在YES """
        # 经过一步只输出一个虚频
        content_list = []
        with open(self.filename, mode="r", buffering=-1, encoding="utf-8") as fileObj:
            file_lines = fileObj.readlines()
            show = 0
            for line_num in range(len(file_lines)):
                if count <= 0:
                    break
                if "Step number" in file_lines[line_num]:
                    show = 1
                    count -= 1
                    # print("\n{}".format((file_lines[line_num]).strip()))
                    content_list.append("\n{}".format((file_lines[line_num]).strip()))
                if "Eigenvalues ---" in file_lines[line_num] and show == 1:
                    # print((file_lines[line_num]).strip())
                    content_list.append((file_lines[line_num]).strip())
                    show = 0
                if "Eigenvectors" in file_lines[line_num]:
                    # print((file_lines[line_num+1]).strip())
                    # print(file_lines[line_num+2].strip()[-48:])
                    content_list.append((file_lines[line_num + 1]).strip())
                    content_list.append(file_lines[line_num + 2].strip()[-48:])
                for YES_key in self.YES_keys:
                    if "YES" in file_lines[line_num] and YES_key in file_lines[line_num]:
                        # print(file_lines[line_num].strip())
                        content_list.append(file_lines[line_num].strip())

        return content_list


if __name__ == "__main__":
    energy_dict_test = {}
    A = FindInfo(r"E:\Research\AP\task-1130\二茂铁-AP\FeR2\Rate\R\2.log")
    print(A.get_others())
    # print(A.get_rocbs_energy())
