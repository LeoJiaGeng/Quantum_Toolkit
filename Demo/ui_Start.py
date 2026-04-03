# -*- coding: utf-8 -*-
"""
Created on Sun Oct  10 21:53:27 2025
@author: Leo
"""

from PyQt5.QtCore import (Qt, pyqtSlot, QCoreApplication, QDir,
                          QFile, QTextStream, QTranslator, QSettings)
import os
import sys
from ui_Quantum import Ui_Form
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QBrush, QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog, QTableWidgetItem
import warnings
# 过滤 PyQt5 SIP 相关的弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")


class QmyWidget(QWidget):
    # 主题名映射：英文文件名 -> {CN: 中文名, EN: 英文名}
    THEME_NAMES = {
        'default': {'CN': '默认', 'EN': 'Default'},
        'dark': {'CN': '黑夜', 'EN': 'Dark'},
        'light': {'CN': '极简白', 'EN': 'Light'},
        'blue': {'CN': '科技蓝', 'EN': 'Blue'},
        'round': {'CN': '圆角彩条', 'EN': 'Round'},
        'win11': {'CN': 'Win11风格', 'EN': 'Win11'},
        'mac': {'CN': 'Mac风格', 'EN': 'Mac'},
        'forest': {'CN': '森林绿', 'EN': 'Forest'},
        'ocean': {'CN': '深海蓝', 'EN': 'Ocean'},
        'sunset': {'CN': '日落橙', 'EN': 'Sunset'},
    }

    def __init__(self, parent=None):
        # 初始化界面
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle(QCoreApplication.translate("QmyWidget", "量子化学小程序"))

        # self.lineEdit_widgets = lineEdit_widgets
        # self.plainTextEdit_widgets = plainTextEdit_widgets
        # self.comboBox_widgets = comboBox_widgets

        self.lineEdit_widgets = {
            # save window
            'save_stand_E': self.ui.save_lineEdit_standard_E,
            'save_stand_G': self.ui.save_lineEdit_standard_G,
            # search window
            'search_file_route': self.ui.search_lineEdit_file_route,
            # trans window
            'trans_file_route': self.ui.trans_lineEdit_file_route,
            'trans_current_state': self.ui.trans_lineEdit_current_state,
            # rename window
            'rename_loc1': self.ui.rename_lineEdit_loc1,
            'rename_loc2': self.ui.rename_lineEdit_loc2,
            'rename_current_state': self.ui.rename_lineEdit_current_state
        }

        self.plainTextEdit_widgets = {
            # save window
            'save_log': self.ui.save_plainTextEdit_log,
            # search window
            'search_result': self.ui.search_plainTextEdit_result,
            'search_match_result': self.ui.search_plainTextEdit_match_result,
            # trans window
            'trans_template': self.ui.trans_plainTextEdit_template,
            'trans_log': self.ui.trans_plainTextEdit_log,
            # rename window
            'rename_log': self.ui.rename_plainTextEdit_log
        }

        self.comboBox_widgets = {
            # save window
            'save_folder': self.ui.save_comBox_folder,
            'save_filename': self.ui.save_comBox_save_filename,
            # search window
            'search_re_match': self.ui.search_comBox_re_match,
            # trans window
            'trans_folder': self.ui.trans_comBox_folder,
            'trans_read_type': self.ui.trans_comBox_read_type,
            'trans_pre': self.ui.trans_comBox_pre,
            'trans_suf': self.ui.trans_comBox_suf,
            'trans_mode': self.ui.trans_comBox_mode,
            'trans_template': self.ui.trans_comBox_template,
            # rename window
            'rename_folder': self.ui.rename_comBox_folder,
            'rename_new_content': self.ui.rename_comBox_new_content
        }

        self.comboBox_set_widgets = {
            # set window
            'set_cur_folder': self.ui.set_comBox_cur_folder,
            'set_theme': self.ui.set_comBox_theme,
            'set_pull': self.ui.set_comBox_pull,
            'set_combo_number': self.ui.set_comBox_combo_number,
            'set_lang': self.ui.set_comBox_lang,
            'set_double_check': self.ui.set_comBox_double_check,
            'set_auto_open': self.ui.set_comBox_auto_open_file
        }

        self.table_widgets = {
            # save window
            'save_table_energy': self.ui.save_tableWidget_energy,
            'rename_table_folder': self.ui.rename_tableWidget_filename
        }

        self.set_tab_init()

    def set_tab_init(self):
        # 1. 设置组织名/应用名 → 决定注册表路径
        QCoreApplication.setOrganizationName("mySoft")
        QCoreApplication.setApplicationName("Quantum")

        # 2. 读取上次语言（没有则返回默认值 "CN"）
        settings = QSettings()  # 现在已自动关联到 HKEY_CURRENT_USER\Software\mySoft\Quantum
        self.lang = settings.value("Language", "CN")   # 键名随便起，第一次会返回 "CN"

        # 3. 先加载翻译，再设置下拉框（屏蔽信号避免触发）
        self.load_language(self.lang)

        if self.lang == "CN":
            self.set_set_lang("中文", block_signal=True)
        else:
            self.set_set_lang("English", block_signal=True)

        # 4. 加载剩余参数
        self.load_except_lang()

        # 5. 设置各个控件的默认值
        self.false_all_plainTextEdit_acceptDrop()

    def load_except_lang(self):
        """加载语言之外的设置项（从注册表读取并应用）"""
        settings = QSettings()

        # 屏蔽所有设置控件信号，避免连锁触发
        for key, combo in self.comboBox_set_widgets.items():
            combo.blockSignals(True)

        # 2、读取并应用"二次确认"设置（默认开启）
        double_check_val = settings.value("DoubleCheck", "开启")
        if double_check_val is None:
            double_check_val = "开启"
        settings.setValue("DoubleCheck", double_check_val)  # 确保写入注册表
        self._apply_double_check_setting(double_check_val)

        # 3、读取并应用拖拽支持设置（默认支持）
        pull_val = settings.value("Pull", "支持")
        if pull_val is None:
            pull_val = "支持"
        settings.setValue("Pull", pull_val)
        self._apply_pull_setting(pull_val)

        # 4、读取并应用是否只处理当前文件夹（默认仅当前文件夹）
        cur_folder_val = settings.value("OnlyCurrentFolder", "仅当前文件夹")
        if cur_folder_val is None:
            cur_folder_val = "仅当前文件夹"
        settings.setValue("OnlyCurrentFolder", cur_folder_val)
        self._apply_cur_folder_setting(cur_folder_val)

        # 5、读取并应用自动打开设置（默认启用）
        auto_open_val = settings.value("AutoOpen", "启用")
        if auto_open_val is None:
            auto_open_val = "启用"
        settings.setValue("AutoOpen", auto_open_val)
        self._apply_auto_open_setting(auto_open_val)

        # 6、设置主题下拉框
        self.init_theme_combo()

        # 7、读取下拉框设置（注册表存的是实际项数，需要减1转为索引）
        comboBox_max_visiable_number = int(settings.value("comboBoxNumber", 6))
        self._change_combo_number(comboBox_max_visiable_number - 1)

        # 恢复信号
        for key, combo in self.comboBox_set_widgets.items():
            combo.blockSignals(False)

    def _apply_double_check_setting(self, stored_val):
        """应用二次确认设置（从注册表读取的值）"""
        # 根据当前语言选择下拉框选项
        if self.lang == "CN":
            # 中文界面：注册表值直接对应中文选项
            self.set_comboBox_current("set_double_check", stored_val, block_signal=True)
            if stored_val == "开启":
                self.DOUBLE_CHECK = True
                self.ui.label_double_check.setText("当前选择：开启（建议开启）")
            else:
                self.DOUBLE_CHECK = False
                self.ui.label_double_check.setText("当前选择：未开启（建议开启）")
        else:
            # 英文界面：需要转换
            if stored_val == "开启":
                self.set_comboBox_current("set_double_check", "Enable", block_signal=True)
                self.DOUBLE_CHECK = True
                self.ui.label_double_check.setText("Current Choice: Enable (Recommended)")
            else:
                self.set_comboBox_current("set_double_check", "Disable", block_signal=True)
                self.DOUBLE_CHECK = False
                self.ui.label_double_check.setText("Current Choice: Disable")

    def _apply_pull_setting(self, stored_val):
        """应用拖拽设置"""
        if self.lang == "CN":
            self.set_comboBox_current("set_pull", stored_val, block_signal=True)
            if stored_val == "支持":
                self.setAcceptDrops(True)
                self.ui.label_pull.setText("当前选择：文本框支持拖拽")
            else:
                self.setAcceptDrops(False)
                self.ui.label_pull.setText("当前选择：文本框不支持拖拽")
        else:
            if stored_val == "支持":
                self.set_comboBox_current("set_pull", "Support", block_signal=True)
                self.setAcceptDrops(True)
                self.ui.label_pull.setText("Current Choice: Text Box Supports Drag and Drop")
            else:
                self.set_comboBox_current("set_pull", "Disabled", block_signal=True)
                self.setAcceptDrops(False)
                self.ui.label_pull.setText("Current Choice: Drag and Drop Disabled")

    def _apply_cur_folder_setting(self, stored_val):
        """应用文件夹处理模式设置"""
        if self.lang == "CN":
            self.set_comboBox_current("set_cur_folder", stored_val, block_signal=True)
            if stored_val == "仅当前文件夹":
                self.ONLY_CURRENT_FOLDER = True
                self.ui.label_cur_folder.setText("当前选择：仅当前文件夹")
            else:
                self.ONLY_CURRENT_FOLDER = False
                self.ui.label_cur_folder.setText("当前选择：包含子文件夹")
        else:
            if stored_val == "仅当前文件夹":
                self.set_comboBox_current("set_cur_folder", "Current Folder", block_signal=True)
                self.ONLY_CURRENT_FOLDER = True
                self.ui.label_cur_folder.setText("Current Choice: Only Current Folder")
            else:
                self.set_comboBox_current("set_cur_folder", "Including SubFolder", block_signal=True)
                self.ONLY_CURRENT_FOLDER = False
                self.ui.label_cur_folder.setText("Current Choice: Include Subfolders")

    def _apply_auto_open_setting(self, stored_val):
        """应用自动打开设置"""
        if self.lang == "CN":
            self.set_comboBox_current("set_auto_open", stored_val, block_signal=True)
            if stored_val == "启用":
                self.AUTO_OPEN = True
                self.ui.label_auto_open_file.setText("当前选择：启用自动打开")
            else:
                self.AUTO_OPEN = False
                self.ui.label_auto_open_file.setText("当前选择：关闭自动打开")
        else:
            if stored_val == "启用":
                self.set_comboBox_current("set_auto_open", "Enable", block_signal=True)
                self.AUTO_OPEN = True
                self.ui.label_auto_open_file.setText("Current Choice: Enable automatic opening")
            else:
                self.set_comboBox_current("set_auto_open", "Disable", block_signal=True)
                self.AUTO_OPEN = False
                self.ui.label_auto_open_file.setText("Current Choice: Disable automatic opening")

    #  ========== the function of lineEdit ==================
    def get_lineEdit_content(self, widget_key):
        """统一的获取内容函数"""
        if widget_key in self.lineEdit_widgets:
            return self.lineEdit_widgets[widget_key].text()
        else:
            print("there is no widget_key")

    def set_lineEdit_content(self, widget_key, content):
        """统一的设置内容函数"""
        if widget_key in self.lineEdit_widgets:
            self.lineEdit_widgets[widget_key].setText(content)

    def get_save_stand_E(self):
        return self.get_lineEdit_content("save_stand_E")

    def get_save_stand_G(self):
        return self.get_lineEdit_content("save_stand_G")

    def get_rename_loc1(self):
        return self.get_lineEdit_content("rename_loc1")

    def get_rename_loc2(self):
        return self.get_lineEdit_content("rename_loc2")

    def get_trans_file_route(self):
        return self.get_lineEdit_content("trans_file_route")

    def get_search_file_route(self):
        return self.get_lineEdit_content("search_file_route")

    def set_search_file_route(self, content):
        self.set_lineEdit_content("search_file_route", content)

    def set_trans_file_route(self, content):
        self.set_lineEdit_content("trans_file_route", content)

    def set_trans_current_state(self, content):
        self.set_lineEdit_content("trans_current_state", content)

    def set_rename_current_state(self, content):
        self.set_lineEdit_content("rename_current_state", content)

    #  ========== the function of plainTextEdit ==================
    def append_plainTextEdit_content(self, widget_key, content):
        """统一的内容显示函数"""
        if widget_key in self.plainTextEdit_widgets:
            self.plainTextEdit_widgets[widget_key].appendPlainText(content)

    def clear_plainTextEdit_content(self, widget_key):
        """统一的内容清除函数"""
        if widget_key in self.plainTextEdit_widgets:
            self.plainTextEdit_widgets[widget_key].clear()

    def set_plainTextEdit_content(self, widget_key, content):
        """统一的内容清除函数"""
        self.clear_plainTextEdit_content(widget_key)
        self.append_plainTextEdit_content(widget_key, content)

    def get_plainTextEdit_content(self, widget_key):
        """统一的内容获取函数"""
        if widget_key in self.plainTextEdit_widgets:
            return self.plainTextEdit_widgets[widget_key].toPlainText()

    def change_plainTextEdit_acceptDrop(self, widget_key, state):
        """设置是否接受拖拽"""
        if widget_key in self.plainTextEdit_widgets:
            self.plainTextEdit_widgets[widget_key].setAcceptDrops(state)

    def false_all_plainTextEdit_acceptDrop(self):
        """将所有plainTextEdit控件设置为不接受拖拽"""
        for widget_key in self.plainTextEdit_widgets:
            self.change_plainTextEdit_acceptDrop(widget_key, False)

    # save window
    def append_save_log(self, strCont):
        self.append_plainTextEdit_content('save_log', strCont)

    def clear_save_content(self):
        self.clear_plainTextEdit_content('save_log')

    def get_save_content(self):
        return self.get_plainTextEdit_content('save_log')

    # search window
    def append_search_log(self, strCont):
        self.append_plainTextEdit_content('search_result', strCont)

    def append_search_match_log(self, strCont):
        self.append_plainTextEdit_content('search_match_result', strCont)

    def clear_search_match_content(self):
        self.clear_plainTextEdit_content('search_match_result')

    def clear_search_content(self):
        self.clear_plainTextEdit_content('search_result')

    def get_search_content(self):
        return self.get_plainTextEdit_content('search_result')

    # trans window
    def append_trans_log(self, strCont):
        self.append_plainTextEdit_content('trans_log', strCont)

    def append_trans_template(self, strCont):
        self.append_plainTextEdit_content('trans_template', strCont)

    def clear_trans_template(self):
        self.clear_plainTextEdit_content('trans_template')

    def clear_trans_log(self):
        self.clear_plainTextEdit_content('trans_log')

    def get_trans_template(self):
        return self.get_plainTextEdit_content('trans_template')

    def set_trans_template(self, content):
        self.set_plainTextEdit_content('trans_template', content)

    # rename window
    def append_rename_log(self, strCont):
        self.append_plainTextEdit_content('rename_log', strCont)

    def clear_rename_log(self):
        self.clear_plainTextEdit_content('rename_log')

    #  ========== the function of Combo ==================
    def init_comboBox(self, widget_key, content_list):
        """统一初始化函数"""
        if widget_key in self.comboBox_widgets:
            combo = self.comboBox_widgets[widget_key]
        elif widget_key in self.comboBox_set_widgets:
            combo = self.comboBox_set_widgets[widget_key]
        else:
            print(f"Widget key '{widget_key}' not found.")
            return 0

        combo.blockSignals(True)             # ⛔ 屏蔽信号
        combo.clear()  # 清空也算一次当前值更改
        for item in content_list:
            combo.addItem(item)
        combo.blockSignals(False)            # ✅ 恢复信号

    def get_comboBox_list(self, widget_key):
        """统一获取函数"""
        if widget_key in self.comboBox_widgets:
            return [self.comboBox_widgets[widget_key].itemText(i)
                    for i in range(self.comboBox_widgets[widget_key].count())]
        elif widget_key in self.comboBox_set_widgets:
            return [self.comboBox_set_widgets[widget_key].itemText(
                i) for i in range(self.comboBox_set_widgets[widget_key].count())]
        else:
            print(f"Widget key '{widget_key}' not found.")

    def insert_comboBox(self, widget_key, insert_str, location=0):
        # default insert str at the first in the combo
        origin_list = self.get_comboBox_list(widget_key)
        if insert_str not in origin_list:
            new_list = origin_list
            new_list.insert(location, insert_str)
            self.init_comboBox(widget_key, new_list)

    def get_comboBox_current(self, widget_key):
        if widget_key in self.comboBox_widgets:
            return self.comboBox_widgets[widget_key].currentText()
        elif widget_key in self.comboBox_set_widgets:
            return self.comboBox_set_widgets[widget_key].currentText()
        else:
            print(f"Widget key '{widget_key}' not found.")

    def set_comboBox_current(self, widget_key, strCont, block_signal=False):
        """设置下拉框当前选项

        Args:
            widget_key: 控件键名
            strCont: 要设置的文本
            block_signal: 是否屏蔽信号（初始化时建议为True）
        """
        if widget_key in self.comboBox_widgets:
            origin_list = self.get_comboBox_list(widget_key)
            if strCont in origin_list:
                if block_signal:
                    self.comboBox_widgets[widget_key].blockSignals(True)
                self.comboBox_widgets[widget_key].setCurrentText(strCont)
                if block_signal:
                    self.comboBox_widgets[widget_key].blockSignals(False)
            else:
                print(f"strCont '{strCont}' not found in {widget_key}.")
        elif widget_key in self.comboBox_set_widgets:
            origin_list = self.get_comboBox_list(widget_key)
            if strCont in origin_list:
                if block_signal:
                    self.comboBox_set_widgets[widget_key].blockSignals(True)
                self.comboBox_set_widgets[widget_key].setCurrentText(strCont)
                if block_signal:
                    self.comboBox_set_widgets[widget_key].blockSignals(False)
            else:
                print(f"strCont '{strCont}' not found in {widget_key}.")
        else:
            print(f"Widget key '{widget_key}' not found.")

    def set_comboBox_maxVisibleItems(self, widget_key, num):
        if widget_key in self.comboBox_widgets:
            self.comboBox_widgets[widget_key].setMaxVisibleItems(num)
        elif widget_key in self.comboBox_set_widgets:
            self.comboBox_set_widgets[widget_key].setMaxVisibleItems(num)

    def set_set_lang(self, strCont, block_signal=False):
        self.set_comboBox_current("set_lang", strCont, block_signal)

    def get_save_folder_current(self):
        return self.get_comboBox_current("save_folder")

    def get_save_filename_current(self):
        return self.get_comboBox_current("save_filename")

    def get_rename_folder_current(self):
        return self.get_comboBox_current("rename_folder")

    def get_trans_folder_current(self):
        return self.get_comboBox_current("trans_folder")

    def get_trans_comBox_read_type_current(self):
        return self.get_comboBox_current("trans_read_type")

    def get_trans_comBox_pre_current(self):
        return self.get_comboBox_current("trans_pre")

    def get_trans_comBox_suf_current(self):
        return self.get_comboBox_current("trans_suf")

    def get_trans_mode_current(self):
        return self.get_comboBox_current("trans_mode")

    def get_trans_template_current(self):
        return self.get_comboBox_current("trans_template")

    def get_rename_new_content(self):
        return self.get_comboBox_current("rename_new_content")

#  ========== the function of QMessageBox ==================
    def MsgWarning(self, msg):
        dlgTitle = "Warning消息框"
        QMessageBox.warning(self, dlgTitle, msg)

    def MsgInformation(self, msg):
        dlgTitle = "Information消息框"
        QMessageBox.information(self, dlgTitle, msg)

    def MsgQuestion(self, strInfo="文件已被修改，是否保存修改？"):
        dlgTitle = "Question消息框"
        defaultBtn = QMessageBox.NoButton  # 缺省按钮
        result = QMessageBox.question(self, dlgTitle, strInfo,
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                      defaultBtn)

        return result
        # if (result==QMessageBox.Yes):
        #     self.ui.plainTextEdit.appendPlainText("Question消息框: Yes 被选择")
        # elif(result==QMessageBox.No):
        #     self.ui.plainTextEdit.appendPlainText("Question消息框: No 被选择")
        # elif(result==QMessageBox.Cancel):
        #     self.ui.plainTextEdit.appendPlainText("Question消息框: Cancel 被选择")
        # else:
        #     self.ui.plainTextEdit.appendPlainText("Question消息框: 无选择")

#  ========== the function of File/Folder ==================
    def open_folder(self):
        curPath = QDir.currentPath()
        dlgTitle = "选择一个目录"
        selectedDir = QFileDialog.getExistingDirectory(self, dlgTitle, curPath, QFileDialog.ShowDirsOnly)
        return selectedDir

    def open_file(self):
        curPath = QDir.currentPath()
        dlgTitle = "选择一个文件"
        return QFileDialog.getOpenFileName(self, dlgTitle, curPath)

#  ========== the function of drag and drop ==================
    def dragEnterEvent(self, event) -> None:
        if (event.mimeData().hasUrls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = [u.toLocalFile() for u in event.mimeData().urls()]
        if not urls:
            return

        idx = self.ui.tabWidget.currentIndex()   # 当前页 0~4
        # 路由
        if idx == 0:
            self.on_save_drop(urls)
        elif idx == 1:
            self.on_search_drop(urls)
        elif idx == 2:
            self.on_transfer_drop(urls)
        elif idx == 3:
            self.on_rename_drop(urls)
        elif idx == 4:
            self.on_preference_drop(urls)

    def _split_paths(self, paths):
        """返回 (files, folders) 两个列表"""
        files, folders = [], []
        for p in paths:
            if os.path.isfile(p):
                files.append(p)
            elif os.path.isdir(p):
                folders.append(p)
        return files, folders

# ========== the function of drag and drop tab details ==========
    def on_save_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[保存页] 文件→", files, " 文件夹→", folders)

        if folders:
            if folders[0] in self.get_comboBox_list("save_folder"):
                self.set_comboBox_current("save_folder", folders[0])
            else:
                self.insert_comboBox("save_folder", folders[0], 0)
            return
        if files:
            if files[0].lower().endswith(('.xls', '.xlsx')):
                self.insert_comboBox("save_filename", os.path.basename(files[0]), 0)
            elif self.DOUBLE_CHECK:
                self.MsgWarning("仅支持表格文件拖拽")

    def on_search_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[查询页] 文件→", files, " 文件夹→", folders)

        if files:
            if files[0].lower().endswith(('.log', '.out')):
                self.set_search_file_route(files[0])
            elif self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入除log/out文件外的其他文件")
        if folders:
            if self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入文件夹")

    def on_transfer_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[转换页] 文件→", files, " 文件夹→", folders)

        if folders:
            if folders[0] in self.get_comboBox_list("trans_folder"):
                self.set_comboBox_current("trans_folder", folders[0])
            else:
                self.insert_comboBox("trans_folder", folders[0], 0)
            return 0
        if files:
            if files[0].lower().endswith(('.gjf', '.log', ".out")):
                self.set_trans_file_route(files[0])
            elif files[0].lower().endswith(('.txt', '.md')):
                with open(files[0], 'r', encoding='utf-8') as f:
                    self.set_trans_plainTextEdit_template(f.read())
            elif self.DOUBLE_CHECK:
                self.MsgWarning("仅支持Gaussian输入文件或模板文件拖拽")

    def on_rename_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[重命名页] 文件→", files, " 文件夹→", folders)

        if folders:
            if folders[0] in self.get_comboBox_list("rename_folder"):
                self.set_comboBox_current("rename_folder", folders[0])
            else:
                self.insert_comboBox("rename_folder", folders[0], 0)
            return
        # 手动刷新表格（根据自动刷新开关）
        self._refresh_rename_table_if_auto()
        return
        if files:
            if self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入文件")

    def _refresh_rename_table_if_auto(self):
        """根据自动刷新开关刷新重命名表格"""
        if self.ui.rename_cheBox_auto_fresh_table.isChecked():
            folder = self.get_comboBox_current("rename_folder")
            if folder and os.path.exists(folder):
                header = ["序号", "原文件名", "新文件名", "状态"]
                self.set_table_header("rename_table_folder", header)
                self._fill_rename_table(folder)
            elif not folder or not os.path.exists(folder):
                self.append_rename_log("文件夹路径无效，无法刷新表格")

    def on_preference_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[设置页] 文件→", files, " 文件夹→", folders)

        if files or folders:
            if self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入文件/文件夹")

#  ========== the function of table ==================
    def set_table_header(self, widget_key, headerText):
        """设置表头"""
        if widget_key in self.table_widgets:
            self.table_widgets[widget_key].setColumnCount(len(headerText))
            self.table_widgets[widget_key].setHorizontalHeaderLabels(headerText)

        # 遍历headerText中的每个元素，设置表头的样式
        for i in range(len(headerText)):
            # 创建一个QTableWidgetItem对象，并设置其文本为headerText[i]
            headerItem = QTableWidgetItem(headerText[i])
            # 获取headerItem的字体
            font = headerItem.font()
            # 设置字体大小为11
            font.setPointSize(11)
            # 关键：加粗
            font.setBold(True)
            # 设置headerItem的字体
            headerItem.setFont(font)
            # 设置headerItem的文字颜色为蓝色
            headerItem.setForeground(QBrush(Qt.blue))
            # 将设置好的headerItem应用到表格的水平表头
            self.table_widgets[widget_key].setHorizontalHeaderItem(i, headerItem)

    def clear_table_content(self, widget_key):
        """仅删除内容，保留表头"""
        if widget_key in self.table_widgets:
            self.table_widgets[widget_key].clearContents()

    def get_table_header(self, widget_key):
        """返回当前表头文字列表"""
        if widget_key not in self.table_widgets:
            return []
        table = self.table_widgets[widget_key]
        return [table.horizontalHeaderItem(i).text()
                for i in range(table.columnCount())]

    def append_table_content(self, widget_key, row_data):
        self.fill_table_row(widget_key, row_data)

    def fill_table_row(self, widget_key, row_data, row=None, auto_adapt_col=False):
        # 如果widget_key不在table_widgets字典中，返回False
        if widget_key not in self.table_widgets:
            return False

        table = self.table_widgets[widget_key]
        # 如果表格的列数与row_data的长度不一致，返回False，并且不自动适应列数
        if table.columnCount() < len(row_data) and not auto_adapt_col:
            return False          # 长度不一致，拒绝填充

        # 确定要填充的目标行
        if row is None:
            # 如果没有指定行，则在表格的最后一行添加数据
            row = table.rowCount()
            table.insertRow(row)
        else:
            # 如果指定的行尚未存在，则自动扩展表格
            while table.rowCount() <= row:
                table.insertRow(table.rowCount())

        # 填充数据到表格中
        for col, value in enumerate(row_data):
            # 将value转换为字符串，并创建一个QTableWidgetItem对象
            # 如果value是列表，则将其元素用换行符连接成字符串
            if isinstance(value, list):
                string_list = [str(item) for item in value]
                item = QTableWidgetItem("\n".join(string_list))
            else:
                item = QTableWidgetItem(str(value))
            # 设置item的文字居中对齐
            item.setTextAlignment(Qt.AlignCenter)
            # 将item插入到指定的行和列中
            table.setItem(row, col, item)
        # 返回True表示填充成功
        return True

    def fill_table_multi_rows(self, widget_key, rows_data, auto_adapt_col=False):
        """
        rows_data 是二维列表，每个元素是一行数据。
        统一先清空旧内容（保留表头），再一次性写入。
        """
        # 如果widget_key不在table_widgets字典中，直接返回
        if widget_key not in self.table_widgets:
            return
        table = self.table_widgets[widget_key]
        # 清空表格的所有行，但保留表头
        table.setRowCount(0)
        # 遍历rows_data中的每一行数据，并调用fill_table_row函数来填充
        for row_data in rows_data:
            self.fill_table_row(widget_key, row_data, auto_adapt_col=auto_adapt_col)
        self.auto_adapt_table(widget_key)

    def add_table_column(self, widget_key, header_text, column_data=None, index=None):
        """
        新增一列。
        header_text : 新列表头
        column_data : 可选，整列数据（长度需与现有行数一致）
        index       : 插入位置，None 表示追加到最右侧
        """
        if widget_key not in self.table_widgets:
            return False
        table = self.table_widgets[widget_key]
        old_col_cnt = table.columnCount()
        new_col = old_col_cnt if index is None else index
        table.insertColumn(new_col)                 # 物理插入列
        table.setHorizontalHeaderItem(new_col, QTableWidgetItem(header_text))

        # 如果有数据，则一次性写入
        if column_data is not None:
            if len(column_data) != table.rowCount():
                return False  # 行数不匹配
            for row, val in enumerate(column_data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, new_col, item)
        return True

    def set_table_column(self, widget_key, col_index, column_data):
        """
        替换整列数据（保留表头）。
        col_index   : 目标列号
        column_data : 新数据列表，长度必须与现有行数一致
        """
        if widget_key not in self.table_widgets:
            return False
        table = self.table_widgets[widget_key]
        if len(column_data) > table.rowCount():
            return False
        for row, val in enumerate(column_data):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, col_index, item)
        return True

    def get_table_column(self, widget_key, col_index):
        """取出整列文本，返回 list[str]"""
        if widget_key not in self.table_widgets:
            return []
        table = self.table_widgets[widget_key]
        return [table.item(r, col_index).text()
                if table.item(r, col_index) else ''
                for r in range(table.rowCount())]

    def auto_adapt_table(self, widget_key):
        # 如果widget_key不在table_widgets字典中，返回False
        if widget_key not in self.table_widgets:
            return False

        table = self.table_widgets[widget_key]
        table.resizeRowsToContents()  # resize rows
        table.resizeColumnsToContents()  # resize columns
        table.horizontalHeader().setVisible(True)  # show h_header
        table.verticalHeader().setVisible(False)  # show v_header

#  ========== the function of saving tab ==================
    @pyqtSlot()
    def on_save_btn_auto_adapt_clicked(self):
        self.auto_adapt_table("save_table_energy")

#  ========== the function of setting tab ==================
    def init_theme_combo(self):
        """枚举 Styles 目录下所有 qss 文件，填充下拉框"""
        qss_dir = QDir("Styles")
        if not qss_dir.exists():
            qss_dir.mkpath(".")          # 目录不存在就创建
        filters = ["*.qss"]
        qss_files = qss_dir.entryList(filters, QDir.Files)
        # 去掉扩展名当文件名
        self.theme_files = [os.path.splitext(f)[0] for f in qss_files]

        # 根据当前语言生成显示名
        display_names = []
        for theme in self.theme_files:
            if theme in self.THEME_NAMES:
                display_names.append(self.THEME_NAMES[theme].get(self.lang, theme))
            else:
                display_names.append(theme)

        self.init_comboBox("set_theme", display_names)

        # 重新应用组合框最大可见项数设置
        settings = QSettings()
        combo_number = int(settings.value("ComboNumber", 6))
        self.set_comboBox_maxVisibleItems("set_theme", combo_number)

        # 上次用过的主题（可选）
        last_theme = settings.value("LastTheme", "default")
        if last_theme and last_theme in self.theme_files:
            # 根据文件名找到对应的显示名
            if last_theme in self.THEME_NAMES:
                display_name = self.THEME_NAMES[last_theme].get(self.lang, last_theme)
            else:
                display_name = last_theme
            self.set_comboBox_current("set_theme", display_name)

    def get_theme_file_from_display(self, display_name):
        """从显示名获取文件名"""
        for theme_file, names in self.THEME_NAMES.items():
            if names.get(self.lang) == display_name or theme_file == display_name:
                return theme_file
        return display_name  # 如果没找到映射，直接返回原值

    def apply_theme(self, theme_name):
        """加载并设置 qss"""
        qss_path = f"Styles/{theme_name}.qss"
        file = QFile(qss_path)
        if not file.exists():
            # logging.warning("主题文件不存在：%s", qss_path)
            return
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            QApplication.instance().setStyleSheet(stream.readAll())
            file.close()
            QSettings().setValue("LastTheme", theme_name)  # 记忆
            # logging.info("已应用主题：%s", theme_name)
            # 将所有参数都读取一遍，避免重置

    # ---------- lang ----------
    def load_language(self, lang):
        if hasattr(self, 'translator') and self.translator:
            QApplication.removeTranslator(self.translator)
        self.translator = QTranslator()
        qm_file = f"./Langs/appLang_{lang}.qm"
        if self.translator.load(qm_file):
            QApplication.installTranslator(self.translator)
        # 为什么更换语言会重新加载，奇怪的很
        self.comboBox_set_widgets["set_combo_number"].blockSignals(True)
        self.ui.retranslateUi(self)
        self.comboBox_set_widgets["set_combo_number"].blockSignals(False)
        # 重新设置窗口标题（retranslateUi会将其重置为空）翻译上下文不匹配
        self.setWindowTitle(QCoreApplication.translate("QmyWidget", "量子化学小程序"))

        # 4. 把新语言写回「注册表」
        QSettings().setValue("Language", lang)   # 键不存在会自动创建

    @pyqtSlot(str)
    def on_set_comBox_lang_currentIndexChanged(self, text):
        """语言下拉框切换"""
        # 判断切换后的语言
        new_lang = None
        if text == "中文":
            new_lang = "CN"
        elif text == "English":
            new_lang = "EN"

        if new_lang is None or new_lang == self.lang:
            return  # 无效切换或语言未变

        # 更新语言
        self.lang = new_lang
        self.load_language(self.lang)

        # 重新加载设置（会根据新语言更新界面选项）
        self.load_except_lang()

    @pyqtSlot(str)
    def on_set_comBox_double_check_currentIndexChanged(self, text):
        self._change_double_check_mode(text)

    def _change_double_check_mode(self, text):
        if self.lang == "CN":
            if text == "开启":
                self.DOUBLE_CHECK = True
                self.ui.label_double_check.setText("当前选择：开启（建议开启）")
                QSettings().setValue("DoubleCheck", "开启")
            elif text == "未开启":
                self.DOUBLE_CHECK = False
                self.ui.label_double_check.setText("当前选择：未开启（建议开启）")
                QSettings().setValue("DoubleCheck", "未开启")
        elif self.lang == "EN":
            if text == "Enable":
                self.DOUBLE_CHECK = True
                self.ui.label_double_check.setText("Current Choice: Enable (Recommended)")
                QSettings().setValue("DoubleCheck", "开启")
            elif text == "Disable":
                self.DOUBLE_CHECK = False
                self.ui.label_double_check.setText("Current Choice: Disable")
                QSettings().setValue("DoubleCheck", "未开启")
        else:
            pass

    @pyqtSlot(str)
    def on_set_comBox_pull_currentIndexChanged(self, text):
        self._change_pull_mode(text)

    def _change_pull_mode(self, text):
        if self.lang == "CN":
            if text == "支持":
                self.setAcceptDrops(True)
                self.ui.label_pull.setText("当前选择：文本框支持拖拽")
                QSettings().setValue("Pull", "支持")
            elif text == "不支持":
                self.setAcceptDrops(False)
                self.ui.label_pull.setText("当前选择：文本框不支持拖拽")
                QSettings().setValue("Pull", "不支持")
        elif self.lang == "EN":
            if text == "Support":
                self.setAcceptDrops(True)
                self.ui.label_pull.setText("Current Choice: Text Box Supports Drag and Drop")
                QSettings().setValue("Pull", "支持")
            elif text == "Disabled":
                self.setAcceptDrops(False)
                self.ui.label_pull.setText("Current Choice: Drag and Drop Disabled")
                QSettings().setValue("Pull", "不支持")
        else:
            pass

    def _fill_rename_table(self, folder):
        indx_filename_list = [[i + 1, name] for i, name in enumerate(f for f in os.listdir(folder)
                                                                     if os.path.isfile(os.path.join(folder, f)))]
        # print(indx_filename_list)
        self.fill_table_multi_rows("rename_table_folder", indx_filename_list)
        self.auto_adapt_table("rename_table_folder")

    @pyqtSlot(str)
    def on_rename_comBox_folder_currentIndexChanged(self, folder):
        header = ["序号", "原文件名", "新文件名", "状态"]
        if self.ui.rename_cheBox_auto_fresh_table.isChecked():
            if folder == "" or folder is None:
                if self.DOUBLE_CHECK:
                    self.MsgWarning("请选择文件夹！")
                self.append_rename_log("请输入文件夹路径！")
            elif not os.path.exists(folder):
                if self.DOUBLE_CHECK:
                    self.MsgWarning("不存在该文件夹，请输入正确的文件夹路径！")
                self.append_rename_log("不存在该文件夹，请输入正确的文件夹路径！")
            else:
                self.set_table_header("rename_table_folder", header)
                self._fill_rename_table(folder)

    @pyqtSlot(str)
    def on_set_comBox_theme_currentIndexChanged(self, theme):
        if theme:                       # 防止空串
            # 将显示名转换为文件名
            theme_file = self.get_theme_file_from_display(theme)
            self.apply_theme(theme_file)
            if self.lang == "CN":
                self.ui.label_theme.setText(f"当前主题：{theme}")
            elif self.lang == "EN":
                self.ui.label_theme.setText(f"Current Theme: {theme}")

    @pyqtSlot(str)
    def on_set_comBox_cur_folder_currentIndexChanged(self, text):
        self._change_cur_folder_mode(text)

    def _change_cur_folder_mode(self, text):
        if self.lang == "CN":
            if text == "仅当前文件夹":
                self.ONLY_CURRENT_FOLDER = True
                self.ui.label_cur_folder.setText("当前选择：仅当前文件夹")
                QSettings().setValue("OnlyCurrentFolder", "仅当前文件夹")
            elif text == "包含子文件夹":
                self.ONLY_CURRENT_FOLDER = False
                self.ui.label_cur_folder.setText("当前选择：包含子文件夹")
                QSettings().setValue("OnlyCurrentFolder", "包含子文件夹")
        elif self.lang == "EN":
            if text == "Current Folder":
                self.ONLY_CURRENT_FOLDER = True
                self.ui.label_cur_folder.setText("Current Choice: Only Current Folder")
                QSettings().setValue("OnlyCurrentFolder", "仅当前文件夹")
            elif text == "Including SubFolder":
                self.ONLY_CURRENT_FOLDER = False
                self.ui.label_cur_folder.setText("Current Choice: Include Subfolders")
                QSettings().setValue("OnlyCurrentFolder", "包含子文件夹")
        else:
            pass

    @pyqtSlot(str)
    def on_set_comBox_auto_open_file_currentIndexChanged(self, text):
        self._change_auto_open_file_mode(text)

    def _change_auto_open_file_mode(self, text):
        if self.lang == "CN":
            if text == "启用":
                self.AUTO_OPEN = True
                self.ui.label_auto_open_file.setText("当前选择：启用自动打开")
                QSettings().setValue("AutoOpen", "启用")
            elif text == "不启用":
                self.AUTO_OPEN = False
                self.ui.label_auto_open_file.setText("当前选择：关闭自动打开")
                QSettings().setValue("AutoOpen", "不启用")
        elif self.lang == "EN":
            if text == "Enable":
                self.AUTO_OPEN = True
                self.ui.label_auto_open_file.setText("Current Choice: Enable automatic opening")
                QSettings().setValue("AutoOpen", "启用")
            elif text == "Disable":
                self.AUTO_OPEN = False
                self.ui.label_auto_open_file.setText("Current Choice: Disable automatic opening")
                QSettings().setValue("AutoOpen", "不启用")
        else:
            pass

    @pyqtSlot(int)
    def on_set_comBox_combo_number_currentIndexChanged(self, number):
        self._change_combo_number(number)

    def _change_combo_number(self, number):
        # 初始化不会触发，需要自己手动触发一次
        for item in self.comboBox_widgets:
            self.set_comboBox_maxVisibleItems(item, number + 1)
        for item in self.comboBox_set_widgets:
            self.set_comboBox_maxVisibleItems(item, number + 1)

        # 设置组合框的当前索引（number 是索引值）
        self.set_comboBox_current("set_combo_number", str(number + 1), block_signal=True)

        if self.lang == "CN":
            self.ui.label_combo_number.setText(f"当前选择：组合框最多可选 {number+1} 项")
        elif self.lang == "EN":
            self.ui.label_combo_number.setText(f"Current Choice: Combo Box Can Select Up to {number+1} Items")
        QSettings().setValue("comboBoxNumber", number + 1)

    # ---------- 测试代码，继承类会被覆盖 ----------
    @pyqtSlot()
    def on_rename_btn_refresh_clicked(self):
        folder = self.get_comboBox_current("rename_folder")
        if folder:
            self._fill_rename_table(folder)

    @pyqtSlot()
    def on_rename_table_clear_clicked(self):
        self.table_widgets["rename_table_folder"].setRowCount(0)

    @pyqtSlot()
    def on_rename_btn_rename_clicked(self):
        self.set_table_column("rename_table_folder", 2, ["100", "200", "300"])
        self.auto_adapt_table("rename_table_folder")
        print(self.get_table_column("rename_table_folder", 1))  # 保留调试输出

    @pyqtSlot()
    def on_save_btn_sp_energy_clicked(self):
        headerText = ["姓 名", "性 别", "分数"]
        self.set_table_header("save_table_energy", headerText)
        self.ui.label_lang.setText("当前语言：中文")

    @pyqtSlot()
    def on_save_btn_freq_energy_clicked(self):
        self._test_all_table_func_step_by_step()

    @pyqtSlot()
    def on_search_btn_virtual_freq_clicked(self):
        print(self.ui.tabWidget.currentIndex())  # 保留调试输出

    @pyqtSlot()
    def on_trans_btn_convert_clicked(self):
        print(self.ui.tabWidget.currentIndex())  # 保留调试输出


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWidget = QmyWidget()
    myWidget.show()
    sys.exit(app.exec())
