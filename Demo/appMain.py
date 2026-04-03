# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 21:53:27 2022
@author: jxiong@whu.edu.cn
"""

import re
import shutil
import platform
import os
import sys
from config_adapt import Config_Adapt
from folderMan import FolderManager
from filenameMan import FilenameManager
from gausInput import GauInput
from quantum import Quantum
from ui_Start import QmyWidget
from collections import Counter
from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox
import warnings
# 过滤 PyQt5 SIP 相关的弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class QmyApp(QmyWidget):
    def __init__(self):
        # initialize config file and class parameters
        super().__init__()
        self.append_save_log(f"Python的版本为: {platform.python_version()}")
        self.config_init()
        self.params_init()

# ========== the function of config files ==================
    def config_init(self):
        # read configuration from config file and initialization
        self.config = Config_Adapt("quantum_config.ini")

        for (py_key, py_value) in self.lineEdit_widgets.items():
            res = self.config.get_config("lineEdit", py_key)
            if res["ret_val"]:
                self.set_lineEdit_content(py_key, res["data"])

        # for (py_key, py_value) in self.plainTextEdit_widgets.items():
        #     res = self.config.get_config("plainTextEdit", py_key)
        #     if res["ret_val"]:
        #         self.set_plainTextEdit_content(py_key, res["data"])

        for (py_key, py_value) in self.comboBox_widgets.items():
            # 值得注意的是如果越来越多怎么办？先读取一遍超过十个开始删除，已经修改！
            self.config.control_config_list("comboBox", py_key, length=10)
            res = self.config.get_config_list("comboBox", py_key)
            if res["ret_val"]:
                self.init_comboBox(py_key, res["data"])

        # load table data if any
        # for (py_key, py_value) in self.table_widgets.items():
        #     res = self.config.get_config_list("table", py_key)
        #     if res["ret_val"] and res["data"]:
        #         self.init_table_content(py_key, res["data"])

    def save_config(self):
        """Save the content of the line edit in saving window"""
        # 获得所有控件的内容，然后依次写入其中；combo采用insert方式写入
        for (py_key, py_value) in self.lineEdit_widgets.items():
            self.config.set_config("lineEdit", py_key, self.get_lineEdit_content(py_key))

        # for (py_key, py_value) in self.plainTextEdit_widgets.items():
        #     self.config.set_config("plainTextEdit", py_key, self.get_plainTextEdit_content(py_key))

        for (py_key, py_value) in self.comboBox_widgets.items():
            self.config.insert_config("comboBox", py_key, self.get_comboBox_current(py_key))

        # for (py_key, py_value) in self.table_widgets.items():
        #     table_data = self.get_table_content(py_key)
        #     if table_data:
        #         self.config.set_config_list("table", py_key, table_data)

    # ========== the function of params ==================
    def params_init(self):
        # ONLY_CURRENT_FOLDER 和 AUTO_OPEN 已在父类 load_except_lang() 中初始化
        if self.ui.rename_cheBox_auto_fresh_table.isChecked():
            self.AUTO_REFRESH_TABLE = True
        else:
            self.AUTO_REFRESH_TABLE = False
        # receiving energy list
        self.energy_list = []

    # ========== the function of saving window ==================
    @pyqtSlot()
    def on_save_btn_folder_open_clicked(self):
        # select a folder not save configuration
        selectedDir = self.open_folder()
        if selectedDir:
            self.insert_comboBox("save_folder", selectedDir)

    @pyqtSlot()
    def on_save_btn_log_clear_clicked(self):
        # clear saving interface log
        self.clear_plainTextEdit_content("save_log")

    @pyqtSlot()
    def on_save_btn_table_clear_clicked(self):
        # only clear table showing content, not clear the whole table
        self.clear_table_content("save_table_energy")

    def _process_energy(self, energy_type, header, file_type):
        # process energy list and return a list of energy values
        try:
            self.energy_list = []

            folder_name = self.get_save_folder_current()
            stand_E = self.get_save_stand_E()
            stand_G = self.get_save_stand_G()
            save_file_name = self.get_save_filename_current() + file_type
            save_file_abs_path = os.path.join(folder_name, save_file_name)
            self.append_save_log(f"Saving {energy_type}... ...")

            # create a Quantum object and save the energy list
            self.quant = Quantum("out,log", folder_name, stand_E, stand_G, self.ONLY_CURRENT_FOLDER)
            self.energy_list = self.quant.save_frame(header, save_file_abs_path, energy_type, file_type)

            if self.energy_list != []:
                # show the table of energy
                self.set_table_header("save_table_energy", header)
                self.fill_table_multi_rows("save_table_energy", self.energy_list, auto_adapt_col=True)
                self.append_save_log("Save OK!\n")
                # open the file with default application
                if self.AUTO_OPEN:
                    os.startfile(save_file_abs_path)
            else:
                if self.DOUBLE_CHECK:
                    self.MsgWarning("No data found, please check the file name or the file path.\n")
                else:
                    self.append_save_log("No data found, please check the file name or the file path.\n")
            self.save_config()
        except Exception as e:
            self.append_save_log(f"The error is: {e}\n")

    @pyqtSlot()
    def on_save_btn_sp_energy_clicked(self):
        header = ["Species", "Energy"]
        file_type = ".xlsx"
        self._process_energy("Single Energy", header, file_type)

    @pyqtSlot()
    def on_save_btn_freq_energy_clicked(self):
        # header = ["Species", "Cor_Zero", "Cor_Gibbs", "HF","Gibbs","E","Rel_G","Rel_E"]
        header = ["Species", "ZPE", "Cor_U", "Cor_H", "Cor_G", "HF", "E", "U", "H", "G"]
        file_type = ".xlsx"
        self._process_energy("Freq Energy", header, file_type)

    @pyqtSlot()
    def on_save_btn_freq_clicked(self):
        header = ["Species", "Frequency"]
        file_type = ".docx"
        self._process_energy("Frequency", header, file_type)

    @pyqtSlot()
    def on_save_btn_coord_clicked(self):
        header = ["Species", "Coordinates"]
        file_type = ".docx"
        self._process_energy("Coordinates", header, file_type)

    @pyqtSlot()
    def on_save_btn_detail_clicked(self):
        header = [
            "Species",
            "RC_x_GHz",
            "RC_y_GHz",
            "RC_z_GHz",
            "RC_x_cm-1",
            "RC_y_cm-1",
            "RC_z_cm-1",
            "MW",
            "num_freq"]
        file_type = ".xlsx"
        self._process_energy("Others", header, file_type)

    @pyqtSlot()
    def on_save_btn_cbs_energy_clicked(self):
        header = ["Species", "CBS_Energy"]
        file_type = ".xlsx"
        self._process_energy("CBS Energy", header, file_type)

    @pyqtSlot()
    def on_save_btn_G4_energy_clicked(self):
        header = ["Species", "G4_Energy"]
        file_type = ".xlsx"
        self._process_energy("G4 Energy", header, file_type)

    @pyqtSlot()
    def on_save_btn_W1_energy_clicked(self):
        header = ["Species", "Match1", "Match2"]
        file_type = ".xlsx"
        self._process_energy("Re match content", header, file_type)

    @pyqtSlot()
    def on_save_btn_multi_cbs_energy_clicked(self):
        header = ["Species", "MP4", "CCSD(T)", "MP2", "MP4", "HF", "Int", "OIii", "T1", "E"]
        file_type = ".xlsx"
        self._process_energy("MultiCBS Energy", header, file_type)

    @pyqtSlot()
    def on_save_btn_SI_energy_clicked(self):
        # 暂未修改
        header = ["Species", "Coordinates (x, y, z in Å)", "Energies (in Hartree)"]
        file_type = ".docx"
        self._process_energy("Support Information", header, file_type)

    # ========== the function of searching window ==================
    @pyqtSlot()
    def on_search_btn_file_open_clicked(self):
        # select a file to search
        selectedFile = self.open_file()
        if selectedFile:
            self.set_search_file_route(selectedFile[0])
            self.save_config()

    def _search_process_gauss_info(self, info_type):
        try:
            filename = self.get_search_file_route()
            self.quant = Quantum("log,out", filename)
            if info_type == "Detail":
                print_list = self.quant.detail_info(filename)
            elif info_type == "Simple":
                print_list = self.quant.simple_info(filename)
            else:
                print_list = []
            if print_list:
                for content in print_list:
                    self.append_search_log(content)
                self.save_config()
            else:
                self.append_search_log("No Eigenvectors and Eigenvalues found.")
        except Exception as e:
            self.append_search_log(str(e))

    @pyqtSlot()
    def on_search_btn_virtual_freq_clicked(self):
        self._search_process_gauss_info("Simple")

    @pyqtSlot()
    def on_search_btn_yes_clicked(self):
        self._search_process_gauss_info("Detail")

    @pyqtSlot()
    def on_search_btn_re_match_clicked(self):
        try:
            match_text = self.get_comboBox_current("search_re_match")
            filename = self.get_search_file_route()
            with open(filename, 'r', encoding='utf-8') as f:
                file_content = f.read()
            match_results = re.findall(match_text, file_content)
            if match_results:
                for result in match_results:
                    self.append_search_match_log(match_text + ": " + result)
                self.save_config()
            else:
                self.append_search_match_log("No match found.")
        except Exception as e:
            self.append_search_match_log(f"Error occurred: {e}")

    @pyqtSlot()
    def on_search_btn_result_clear_clicked(self):
        # clear searching interface
        self.clear_search_content()
        self.clear_search_match_content()

    #  ========== the function of transfer window ==================
    @pyqtSlot()
    def on_trans_btn_folder_open_clicked(self):
        # select a folder save configuration and list files name
        selectedDir = self.open_folder()
        if selectedDir:
            self.insert_comboBox("trans_folder", selectedDir)

    @pyqtSlot()
    def on_trans_btn_file_open_clicked(self):
        # select a folder save configuration and list files name
        selectedDir = self.open_file()
        if selectedDir:
            self.set_trans_file_route(selectedDir[0])

    def _read_trans_params(self):
        # read parameters from the transfer window
        self.trans_pre = self.get_trans_comBox_pre_current()
        self.trans_suf = self.get_trans_comBox_suf_current()
        self.trans_mode = self.get_trans_mode_current()
        self.trans_template = self.get_trans_template_current()
        self.read_file_type = self.get_trans_comBox_read_type_current()

        if (self.ui.trans_radbtn_chalevel.isChecked()):
            self.execType = "CHANGE-LEVEL"
            self.execType_cn = "更换水平的输入文件"
        elif (self.ui.trans_radbtn_fullirc.isChecked()):
            self.execType = "IRC"
            self.execType_cn = "IRC输入文件"
        elif (self.ui.trans_radbtn_apartirc.isChecked()):
            self.execType = "IRC-SPLIT"
            self.execType_cn = "分开的IRC输入文件"
        elif (self.ui.trans_radbtn_spints.isChecked()):   # 功能有问题，待修复
            self.execType = "SPIN-TS"
            self.execType_cn = "自旋测试文件"
        elif (self.ui.trans_radbtn_highsp.isChecked()):
            self.execType = "HIGH-SP"
            self.execType_cn = "高水平单点能输入文件"
        elif (self.ui.trans_radbtn_irc2gjf.isChecked()):
            self.execType = "IRC-GJF"
            self.execType_cn = "IRC每一帧文件"
        elif (self.ui.trans_radbtn_mod2gjf.isChecked()):
            self.execType = "MOD-GJF"
            self.execType_cn = "扫描每一帧文件"

        # 显示状态栏
        state = self.trans_mode + self.trans_template + "批量生成" + self.execType_cn
        self.set_trans_current_state(state)

        self.read_type = self.get_trans_comBox_read_type_current()

    @pyqtSlot()
    def on_trans_btn_convert_clicked(self):
        try:
            self._read_trans_params()
            gauss_obj = GauInput()

            if (self.ui.trans_radbtn_folder.isChecked()):
                trans_type = "folder"
                trans_folder = self.get_trans_folder_current()
                ret = gauss_obj.trans_folder(trans_folder, self.trans_pre,
                                            self.trans_suf, self.execType,
                                            self.read_type, self.trans_mode,
                                            self.ONLY_CURRENT_FOLDER)
            elif (self.ui.trans_radbtn_single_file.isChecked()):
                trans_type = "file"
                trans_file = self.get_trans_file_route()
                ret = gauss_obj.trans_file(trans_file, self.trans_pre,
                                        self.trans_suf, self.execType,
                                        self.read_type, self.trans_mode)
            # 检查判断是否成功
            if ret:
                self.append_trans_log("文件创建成功！")
                if trans_type == "folder" and self.AUTO_OPEN:
                    os.startfile(trans_folder)
                # save configuration after success
                self.save_config()
            else:
                self.append_trans_log("文件创建失败！")
        except Exception as e:
            self.append_trans_log(f"Error occurred: {e}")

    @pyqtSlot()
    def on_trans_btn_template_clear_clicked(self):
        self.clear_trans_template()

    @pyqtSlot()
    def on_trans_btn_log_clear_clicked(self):
        self.clear_trans_log()

    def _refresh_trans_template(self, curFolder, curTemplate):
        # refresh the template list
        abs_filename = "./Model/" + curFolder + "/" + curTemplate
        with open(abs_filename, 'r') as f:
            self.clear_trans_template()
            for line in f.readlines():
                self.append_trans_template(line.strip())

    @pyqtSlot(str)
    def on_trans_comBox_mode_currentIndexChanged(self, curText):
        # 检测到列表选项变化时，更新模板内容
        trans_mode = curText
        trans_template = self.get_trans_template_current()
        self._refresh_trans_template(trans_mode, trans_template)

    @pyqtSlot(str)
    def on_trans_comBox_template_currentIndexChanged(self, curText):
        # 检测到列表选项变化时，更新模板内容
        trans_mode = self.get_trans_mode_current()
        trans_template = curText
        self._refresh_trans_template(trans_mode, trans_template)

    @pyqtSlot()
    def on_trans_btn_save_template_clicked(self):
        # save template button
        curFolder = self.get_trans_mode_current()
        curTemplate = self.get_trans_template_current()
        abs_filename = "./Model/" + curFolder + "/" + curTemplate  # type: ignore
        content = self.ui.trans_plainTextEdit_template.toPlainText()
        with open(abs_filename, 'w') as f:
            f.write(content)

    @pyqtSlot()
    def on_trans_btn_template_import_clicked(self):
        # 直接导入内容到界面上
        selectedDir = self.open_file()
        if selectedDir:
            with open(selectedDir[0], 'r', encoding="utf-8") as f:
                self.clear_trans_template()
                for line in f.readlines():
                    self.append_trans_template(line.strip())

    def _check_import_mode_folder(self, folder_name):
        DEFAULT_TEMPLATES = [
            'F-OPT-template.txt', 'HIGH-SP-template.txt', 'INPUT-template.txt',
            'IRC-F-template.txt', 'IRC-GJF-template.txt', 'IRC-R-template.txt',
            'IRC-template.txt', 'MOD-GJF-template.txt', 'OPT-template.txt',
            'SPIN-TEST-template.txt', 'TS-template.txt'
        ]
        required_files = set(DEFAULT_TEMPLATES)
        current_files = {
            f for f in os.listdir(folder_name)
            if os.path.isfile(os.path.join(folder_name, f))
        }
        # 集合可以加减操作
        missing_files = required_files - current_files

        if missing_files:
            self.MsgWarning(f"❌ 缺少 {len(missing_files)} 个文件: {sorted(missing_files)}")
            return False
        else:
            if self.DOUBLE_CHECK:
                self.MsgInformation("✅导入成功，文件夹已复制到Model文件夹下")
            return True

    @pyqtSlot()
    def on_trans_btn_mode_import_clicked(self):
        # select a folder save configuration and list files name
        selectedDir = self.open_folder()
        # 存在bug：不能导入当前的Model文件夹，因为会冲突
        if selectedDir:
            dst_folder = os.path.join(r".\Model", os.path.basename(selectedDir))
            # 对文件内容进行检查，如果不合理就不进行操作
            if self._check_import_mode_folder(selectedDir):
                shutil.copytree(selectedDir, dst_folder, dirs_exist_ok=True)
                self.insert_comboBox("trans_mode", os.path.basename(selectedDir))
                self.save_config()

    # ========== the function of rename window ==================
    @pyqtSlot()
    def on_rename_btn_folder_open_clicked(self):
        selectedDir = self.open_folder()
        if selectedDir:
            self.insert_comboBox("rename_folder", selectedDir)

    def __check_empty_params(self, params, msg):
        # check if the parameters are empty
        if params == "":
            if self.DOUBLE_CHECK:
                self.MsgWarning(msg)
            return False
        else:
            return True

    def _rename_read_params(self):
        # input parameters
        self.name_obj = FilenameManager(self.ONLY_CURRENT_FOLDER)

        if self.ui.rename_cheBox_auto_fresh_table.isChecked():
            self.AUTO_REFRESH_TABLE = True
        else:
            self.AUTO_REFRESH_TABLE = False

        if not self.__check_empty_params(self.get_rename_loc1(), "请输入要修改的位置1！"):
            return 0
        if not self.__check_empty_params(self.get_rename_loc2(), "请输入要修改的位置2！"):
            return 0
        if not self.__check_empty_params(self.get_rename_new_content(), "请输入要修改的内容！"):
            return 0

        if not os.path.exists(self.get_rename_folder_current()):
            self.append_rename_log("不存在该文件夹，请输入正确的文件夹路径！")
            if self.DOUBLE_CHECK:
                self.MsgWarning("不存在该文件夹，请输入正确的文件夹路径！")
            return 0

        self.rename_loc1 = int(self.get_rename_loc1())
        self.rename_loc2 = int(self.get_rename_loc2())
        self.rename_folder = self.get_rename_folder_current()
        self.rename_new_content = self.get_rename_new_content()

        if self.rename_folder == "" and self.DOUBLE_CHECK:
            self.MsgWarning("请输入文件夹！")

        if self.rename_new_content == "" and self.DOUBLE_CHECK:
            self.MsgWarning("请输入要修改的内容！")

        # select parameters
        if (self.ui.rename_radbtn_pre.isChecked()):
            self.ref_type = "PRE"
            self.ref_type_cn = "之前"
        elif (self.ui.rename_radbtn_suf.isChecked()):
            self.ref_type = "SUF"
            self.ref_type_cn = "之后"
        elif (self.ui.rename_radbtn_med.isChecked()):
            self.ref_type = "MED"
            self.ref_type_cn = "中间"
        elif (self.ui.rename_radbtn_both.isChecked()):
            self.ref_type = "BOTH"
            self.ref_type_cn = "前后两端"

        if (self.ui.rename_btn_add.isChecked()):
            self.func_type = "add"
            self.func_type_cn = "添加"
        elif (self.ui.rename_btn_del.isChecked()):
            self.func_type = "del"
            self.func_type_cn = "删除"
        elif (self.ui.rename_btn_swap.isChecked()):
            self.func_type = "replace"
            self.func_type_cn = "交换"
        elif (self.ui.rename_btn_case.isChecked()):
            self.func_type = "case"
            self.func_type_cn = "大小写"
        elif (self.ui.rename_btn_insert.isChecked()):
            self.func_type = "insert"
            self.func_type_cn = "序列化"

        state = self.func_type_cn + "文件名在第" + self.get_rename_loc1() + self.ref_type_cn + "到第" + self.get_rename_loc2() + \
            self.ref_type_cn + "之间，" + self.func_type_cn + "的内容为：" + self.rename_new_content + "。"
        self.set_rename_current_state(state)
        return 1

    def rename_check(self, new_name_list):
        # check if the new name is valid
        freq = Counter(new_name_list)
        # return 1 if the new name is valid, 0 if not
        # return [0 if freq[v] > 1 else 1 for v in new_name_list]
        return ['冲突' if freq[v] > 1 else ' ' for v in new_name_list]
        # return [freq[v] > 1 for v in new_name_list]

    def rename_func(self, auto_rename=False):
        self._rename_read_params()
        self.name_obj.switch(auto_rename)
        self.save_config()
        return self.name_obj.rename_files(
            self.rename_folder,
            self.func_type,
            self.rename_loc1,
            self.rename_loc2,
            self.rename_new_content)

    @pyqtSlot()
    def on_rename_btn_rename_clicked(self):
        # 进行替换的操作
        if not self._rename_read_params():
            return
        self.folder_obj = FolderManager()
        self.folder_obj.backup(self.rename_folder)
        self.rename_func(auto_rename=True)
        self.append_rename_log("文件重命名完成！如有反悔，可以进行撤销！")

    def _refresh_rename_table(self):
        if not self._rename_read_params():
            return 0
        # 1. 原始两列信息拆成 4 列
        old_filename_list = [
            [i + 1, name]                          # 现在还是 2 列
            for i, name in enumerate(f for f in os.listdir(self.rename_folder)
                                     if os.path.isfile(os.path.join(self.rename_folder, f)))
        ]

        # 2. 拿到另外两列，这里操作了两次列表，可以优化
        rename_new_list = self.rename_func(auto_rename=False)
        check_list = self.rename_check(rename_new_list)

        # 3. 拼成 4 列，而不是 3 列
        all_filename_list = [
            [idx, old_name, new_name, check_flag]
            for (idx, old_name), new_name, check_flag
            in zip(old_filename_list, rename_new_list, check_list)
        ]

        # 4. 一次性写表（4 列）
        self.set_table_header("rename_table_folder", ["序号", "原文件名", "新文件名", "状态"])
        self.fill_table_multi_rows("rename_table_folder", all_filename_list)
        self.append_rename_log("文件重命名预览，如有冲突请查看预览列表！\n")

    @pyqtSlot()
    def on_rename_btn_refresh_clicked(self):
        self._refresh_rename_table()

    @pyqtSlot()
    def on_rename_btn_retract_clicked(self):
        try:
            result = self.MsgQuestion("确认要恢复文件名吗？")
            if (result == QMessageBox.Yes):
                self.append_rename_log("没啥大问题，文件已恢复！！！")
                self.folder_obj.restore()
            elif (result == QMessageBox.No):
                self.append_rename_log("Question消息框: No 被选择")
            elif (result == QMessageBox.Cancel):
                self.append_rename_log("Question消息框: Cancel 被选择")
            else:
                self.append_rename_log("Question消息框: 无选择")
        except Exception as e:
            self.append_rename_log(f"Error occurred: {e}")

    @pyqtSlot()
    def on_rename_table_clear_clicked(self):
        self.clear_table_content("rename_table_folder")

    @pyqtSlot()
    def on_rename_btn_log_clear_clicked(self):
        self.clear_rename_log()

    @pyqtSlot()
    def on_rename_btn_init_table_clicked(self):
        self.auto_adapt_table("rename_table_folder")

    @pyqtSlot(bool)
    def on_rename_cheBox_auto_fresh_table_toggled(self, checked):
        self.AUTO_REFRESH_TABLE = checked

    @pyqtSlot(bool)
    def on_rename_radbtn_pre_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_radbtn_suf_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_radbtn_med_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_radbtn_both_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_btn_add_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_btn_case_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_btn_del_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()

    @pyqtSlot(bool)
    def on_rename_btn_swap_toggled(self, checked):
        if checked and self.AUTO_REFRESH_TABLE:
            self._refresh_rename_table()


class QuaThread(QThread):
    # create a thread to run quantum calculation if needed
    sinOut = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        pass


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWidget = QmyApp()
    myWidget.show()
    sys.exit(app.exec())
