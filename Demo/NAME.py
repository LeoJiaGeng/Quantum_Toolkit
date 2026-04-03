class QmyWidget(QWidget):
    def __init__(self, parent=None):
        self.lineEdit_widgets = {
            # save window
            'save_stand_E': self.ui.save_lineEdit_standard_E,
            'save_stand_G': self.ui.save_lineEdit_standard_G,
            # search window
            'search_file_route': self.ui.search_lineEdit_file_route,
            # trans window
            'trans_file_route': self.ui.trans_lineEdit_file_route,
            # rename window
            'rename_loc1': self.ui.rename_lineEdit_loc1,
            'rename_loc2': self.ui.rename_lineEdit_loc2,
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
            'save_filename': self.ui.save_comBox_filename,
            # search window
            'search_re_match': self.ui.search_comBox_re_match,
            'search_folder': self.ui.trans_comBox_folder,
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
            'set_double_check': self.ui.set_comBox_double_check
        }
