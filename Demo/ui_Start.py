# -*- coding: utf-8 -*-
"""
Created on Sun Oct  10 21:53:27 2025
@author: Leo
"""

import sys, os
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import (Qt, pyqtSlot, QCoreApplication, QDir, 
                          QFile, QTextStream, QTranslator, QSettings)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QBrush, QIcon

from ui_Quatum import Ui_Form


class QmyWidget(QWidget):
    def __init__(self, parent=None):
        # 初始化界面
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("量子化学小程序"))
        
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
            'rename_new_content': self.ui.rename_comBox_new_content,
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
        lang = settings.value("Language", "CN")   # 键名随便起，第一次会返回 "CN"
        if lang == "CN":
            self.set_set_lang("中文")
        else:
            self.set_set_lang("English")

        # 3. 加载翻译
        self.load_language(lang) 
        
        comboBox_max_visiable_number = settings.value("comboBoxNumber", 5) 
        for item in self.comboBox_widgets:
            self.set_comboBox_maxVisibleItems(item, comboBox_max_visiable_number)
        self.set_comboBox_current('set_combo_number', str(comboBox_max_visiable_number))
        self.ui.label_combo_number.setText(f"当前选择：组合框最多可选 {str(comboBox_max_visiable_number)} 项")
            
        # 二次确认，默认关闭
        self.DOUBLE_CHECK = False  
        
        # 设置拖拽函数
        self.setAcceptDrops(True)
        self.false_all_plainTextEdit_acceptDrop()
        # 设置好各自的拖拽函数，并选择是否启用，还有combo保留个数
        self.init_theme_combo()
        
        self.ONLY_CURRENT_FOLDER = False  # 默认仅处理当前文件夹数据

    ##  ========== the function of lineEdit ================== 
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
        
    def set_search_file_route(self, content):
        self.set_lineEdit_content("search_file_route", content)
        
    def set_trans_file_route(self, content):
        self.set_lineEdit_content("trans_file_route", content)

    def set_trans_current_state(self, content):
        self.set_lineEdit_content("trans_current_state", content)

    def set_rename_current_state(self, content):
        self.set_lineEdit_content("rename_current_state", content)
    
    ##  ========== the function of plainTextEdit ==================  
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

    def get_trans_template(self):
        return self.get_plainTextEdit_content('trans_template')
    
    def set_trans_template(self, content):
        self.set_plainTextEdit_content('trans_template', content)

    # rename window
    def append_rename_log(self, strCont):
        self.append_plainTextEdit_content('rename_log', strCont)
        
    ##  ========== the function of Combo ==================  
    def init_comboBox(self, widget_key, content_list):
        """统一初始化函数"""
        if widget_key in self.comboBox_widgets: 
            combo = self.comboBox_widgets[widget_key]          
            combo.blockSignals(True)             # ⛔ 屏蔽信号
            combo.clear() # 清空也算一次当前值更改
            for item in content_list:
                combo.addItem(item)
            combo.blockSignals(False)            # ✅ 恢复信号
        else:
            print(f"Widget key '{widget_key}' not found.")

    def get_comboBox_list(self, widget_key):
        """统一获取函数"""
        if widget_key in self.comboBox_widgets:
            return [self.comboBox_widgets[widget_key].itemText(i) for i in range(self.comboBox_widgets[widget_key].count())]
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
        else:
            print(f"Widget key '{widget_key}' not found.")

    def set_comboBox_current(self, widget_key, strCont):
        if widget_key in self.comboBox_widgets:
            origin_list = self.get_comboBox_list(widget_key)
            if strCont in origin_list:
                self.comboBox_widgets[widget_key].setCurrentText(strCont)
            else:
                print(f"strCont '{strCont}' not found in {widget_key}.")
        else:
            print(f"Widget key '{widget_key}' not found.")

    def set_comboBox_maxVisibleItems(self, widget_key, num):
        if widget_key in self.comboBox_widgets:
            self.comboBox_widgets[widget_key].setMaxVisibleItems(num)
                        
    def set_set_lang(self, strCont):
        self.set_comboBox_current("set_lang", strCont)

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
        
    ##  ========== the function of QMessageBox ==================  
    def MsgWarning(self, msg):
        dlgTitle = "Warning消息框"
        QMessageBox.warning(self, dlgTitle, msg)

    def MsgQuestion(self):
        dlgTitle="Question消息框"
        strInfo="文件已被修改，是否保存修改？"
        defaultBtn=QMessageBox.NoButton  #缺省按钮
        result=QMessageBox.question(self, dlgTitle, strInfo,
                     QMessageBox.Yes|QMessageBox.No |QMessageBox.Cancel,
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

    ##  ========== the function of File/Folder ==================  
    def open_folder(self):
        curPath = QDir.currentPath()
        dlgTitle = "选择一个目录"
        selectedDir = QFileDialog.getExistingDirectory(self, dlgTitle, curPath, QFileDialog.ShowDirsOnly)
        return selectedDir

    def open_file(self):
        curPath = QDir.currentPath()
        dlgTitle = "选择一个文件"
        filt = "所有文件(*.*);;文本文件(*.txt);;图片文件(*.jpg *.gif *.png)"
        return QFileDialog.getOpenFileName(self, dlgTitle, curPath)

    ##  ========== the function of drag and drop ==================  
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
            if files[0].lower().endswith(('.log','.out')):
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
            return            
        if files:
            if files[0].lower().endswith(('.gjf', '.log')):
                self.set_trans_file_route(files[0])
            elif files[0].lower().endswith(('.txt', '.md')):
                with open(files[0], 'r', encoding='utf-8') as f:
                    self.set_trans_plainTextEdit_template(f.read())
            elif self.DOUBLE_CHECK:
                self.MsgWarning("仅支持Gaussian输入文件或模板文件拖拽")

    def on_rename_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[重命名页] 文件→", files, " 文件夹→", folders)

        # 重命名页只关心**文件夹**
        if folders:
            if folders[0] in self.get_comboBox_list("rename_folder"):
                self.set_comboBox_current("rename_folder", folders[0])
            else:
                self.insert_comboBox("rename_folder", folders[0], 0)
            return              
        if files:   # 单文件→取所在目录
            if self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入文件")

    def on_preference_drop(self, paths):
        files, folders = self._split_paths(paths)
        print("[设置页] 文件→", files, " 文件夹→", folders)

        if files or folders:
            if self.DOUBLE_CHECK:
                self.MsgWarning("设置页不支持拖入文件/文件夹")

    ##  ========== the function of table ==================  
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
            # 设置headerItem的字体
            headerItem.setFont(font)
            # 设置headerItem的文字颜色为红色
            headerItem.setForeground(QBrush(Qt.red))  
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
      
    def fill_table_row(self, widget_key, row_data, row=None):
        # 如果widget_key不在table_widgets字典中，返回False
        if widget_key not in self.table_widgets:
            return False

        table = self.table_widgets[widget_key]
        # 如果表格的列数与row_data的长度不一致，返回False
        if table.columnCount() < len(row_data):
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
            item = QTableWidgetItem(str(value))
            # 设置item的文字居中对齐
            item.setTextAlignment(Qt.AlignCenter)
            # 将item插入到指定的行和列中
            table.setItem(row, col, item)
        # 返回True表示填充成功
        return True

    def fill_table_multi_rows(self, widget_key, rows_data):
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
            self.fill_table_row(widget_key, row_data)   
            
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
        table.resizeRowsToContents() # resize rows
        table.resizeColumnsToContents() # resize columns
        table.horizontalHeader().setVisible(True)  # show h_header 
        table.verticalHeader().setVisible(False) # show v_header  

    ##  ========== the function of setting tab ================== 
    def init_theme_combo(self):
        """枚举 Styles 目录下所有 qss 文件，填充下拉框"""
        qss_dir = QDir("Styles")
        if not qss_dir.exists():
            qss_dir.mkpath(".")          # 目录不存在就创建
        filters = ["*.qss"]
        qss_files = qss_dir.entryList(filters, QDir.Files)
        # 去掉扩展名当显示名
        theme_list = [os.path.splitext(f)[0] for f in qss_files]
        self.init_comboBox("set_theme", theme_list) #在这里屏蔽信号，避免初始化重复刷新

        # 上次用过的主题（可选）
        settings = QSettings()
        last_theme = settings.value("LastTheme", "无格式")
        if last_theme and last_theme in theme_list:
            self.set_comboBox_current("set_theme", last_theme) # 更改下拉框就会自动刷新
            # self.apply_theme(last_theme)   # 启动即应用
        
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
   
    # ---------- lang ----------
    def load_language(self, lang):
        if hasattr(self, 'translator') and self.translator:
            QApplication.removeTranslator(self.translator)
        self.translator = QTranslator()
        qm_file = f"./Lang/appLang_{lang}.qm"
        if self.translator.load(qm_file):
            QApplication.installTranslator(self.translator)
        self.ui.retranslateUi(self)
        # 4. 把新语言写回「注册表」
        QSettings().setValue("Language", lang)   # 键不存在会自动创建

    @pyqtSlot(str)
    def on_set_comBox_lang_currentIndexChanged(self, text):
        """语言下拉框切换，字体自动变换不需要进行操作，不然会报错"""
        if text == "中文":
            lang = "CN" 
        else: 
            lang = "EN"
        self.load_language(lang)     

    @pyqtSlot(str)
    def on_set_comBox_double_check_currentIndexChanged(self, text):
        if text == "开启":
            self.DOUBLE_CHECK = True
            self.ui.label_double_check.setText("当前选择：开启（建议开启）")
        elif text == "未开启":
            self.DOUBLE_CHECK = False
            self.ui.label_double_check.setText("当前选择：未开启（建议开启）")

    @pyqtSlot(str)
    def on_set_comBox_pull_currentIndexChanged(self, text):
        if text == "支持":
            self.setAcceptDrops(True)
            self.ui.label_pull.setText("当前选择：文本框支持拖拽")
        elif text == "不支持":
            self.setAcceptDrops(False)
            self.ui.label_pull.setText("当前选择：文本框不支持拖拽")

    def _fill_rename_table(self, folder):
        indx_filename_list = [[i + 1, name] for i, name in enumerate(f for f in os.listdir(folder)
                                                if os.path.isfile(os.path.join(folder, f)))]
        # print(indx_filename_list)
        self.fill_table_multi_rows("rename_table_folder", indx_filename_list)
        self.auto_adapt_table("rename_table_folder")        

    @pyqtSlot(str)
    def on_rename_comBox_folder_currentIndexChanged(self, folder):
        if folder != "" and folder != None:
            if self.ui.reanem_cheBox_auto_fresh_table.isChecked():
                self._fill_rename_table(folder)   
    
    @pyqtSlot(str)
    def on_set_comBox_theme_currentIndexChanged(self, theme):
        if theme:                       # 防止空串
            self.apply_theme(theme)
            self.ui.label_theme.setText(f"当前主题：{theme}")

    @pyqtSlot(str)
    def on_set_comBox_cur_folder_currentIndexChanged(self, text):
        if text == "仅当前文件夹":                       
            self.ONLY_CURRENT_FOLDER = True
            self.ui.label_cur_folder.setText("当前选择：仅当前文件夹")
        elif text == "包含子文件夹":
            self.ONLY_CURRENT_FOLDER = False
            self.ui.label_cur_folder.setText("当前选择：包含子文件夹")
        else:
            pass

    @pyqtSlot(int)
    def on_set_comBox_combo_number_currentIndexChanged(self, number):
        # 初始化不会触发，需要自己手动触发一次
        for item in self.comboBox_widgets:
            self.set_comboBox_maxVisibleItems(item, number+1)
        self.ui.label_combo_number.setText(f"当前选择：组合框最多可选 {number+1} 项")
        QSettings().setValue("comboBoxNumber", number+1)  # 记忆

    # ---------- 测试代码，继承类会被覆盖 ----------
    @pyqtSlot()
    def on_rename_btn_refresh_clicked(self):
        folder = self.get_comboBox_current("rename_folder")
        if folder != "" and folder != None:
            self._fill_rename_table(folder)   
        print("parent class")
                                             
    @pyqtSlot()
    def on_rename_table_clear_clicked(self):
        table = self.table_widgets["rename_table_folder"].setRowCount(0)
        print("parent class")    

    @pyqtSlot()
    def on_rename_btn_rename_clicked(self):
        self.set_table_column("rename_table_folder",2,["100","200","300"])
        self.auto_adapt_table("rename_table_folder")    
        print(self.get_table_column("rename_table_folder",1))    
        print("parent class")
           
    @pyqtSlot()
    def on_save_btn_sp_energy_clicked(self):
        headerText=["姓 名","性 别","分数"] 
        self.set_table_header("save_table_energy", headerText)
        self.ui.label_lang.setText("当前语言：中文")
        print("parent class")
        pass
    
    @pyqtSlot()
    def on_save_btn_freq_energy_clicked(self):
        self._test_all_table_funcs_step_by_step()
        print("parent class")
        pass
    
    @pyqtSlot()
    def on_search_btn_virtual_freq_clicked(self):
        print(self.ui.tabWidget.currentIndex())
        print("parent class")
        pass

    @pyqtSlot()
    def on_trans_btn_convert_clicked(self):
        print(self.ui.tabWidget.currentIndex())
        print("parent class")
        pass   
             
if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWidget = QmyWidget()
    myWidget.show()
    sys.exit(app.exec())
        