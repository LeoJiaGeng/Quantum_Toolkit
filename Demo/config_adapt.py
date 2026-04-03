from Public.config import Config
import random
import time


class Config_Adapt(Config):
    def __init__(self, file_name="config.ini"):

        # -------------------- 按控件种类分组 --------------------
        self.lineEdit_ini_widgets = {
            "save_stand_E": "Step number\\s+(\\d+).*?(?=Step number|\\Z)",
            "save_stand_G": "Thermal correction to Energy=\\s+([\\d.-]+)",
            "search_file_route": "D:/Document/Python_Files/ts1.log",
            "trans_file_route": "D:/Document/Python_Files",
            "rename_loc1": "1",
            "rename_loc2": "2",
        }

        self.plainTextEdit_ini_widgets = {
            "save_log": "",
            "search_result": "",
            "search_match_result": "",
            "trans_template": "",
            "trans_log": "",
            "rename_log": "",
        }

        self.comboBox_ini_widgets = {
            "save_folder": "C:/;D:/;F:/;G:/;H:/;I:/;K:/;L:/;M:/;N:/;O:/;P:/;Q:/;R:/;S",
            "save_filename": "能量",
            "search_re_match": "Zero-point correction=\\s+([\\d.-]+);Thermal correction to Energy=\\s+([\\d.-]+)",
            "trans_folder": "D:/Document/Python_Files",
            "trans_read_type": "GauOutFile;GauInFile",
            "trans_pre": "",
            "trans_suf": "irc;gas;pcm",
            "trans_mode": "模式1-PM6;模式2-HF-6-31Gdp;模式3-B3LYP-6-31Gdp;模式4-M062X-6-31Gdp;模式5-M062X-AVDZ",
            "trans_template": "F-OPT-template.txt;HIGH-SP-template.txt;INPUT-template.txt;IRC-F-template.txt;IRC-GJF-template.txt;IRC-R-template.txt;IRC-template.txt;MOD-GJF-template.txt;OPT-template.txt;SPIN-TEST-template.txt;TS-template.txt",
            "rename_folder": "D:/Document/Python_Files",
            "rename_new_content": "12",
        }

        self.table_ini_widgets = {
            # 目前不保存数据，暂时注释掉
            "save_table_energy": ["姓名", "性别", "分数"],
            "rename_table_folder": ["序号", "文件名"],
        }

        self.section_option_dict = {
            "lineEdit": self.lineEdit_ini_widgets,
            # "plainTextEdit": self.plainTextEdit_ini_widgets,
            "comboBox": self.comboBox_ini_widgets,
            # "table": self.table_ini_widgets
        }

        super().__init__(file_name)
        if not self.config.sections():
            self.init_config_file()

    def init_config_file(self):
        for key, value in self.section_option_dict.items():
            self.add_section(key)
            for sub_key, sub_value in value.items():
                self.set_config(key, sub_key, sub_value)

    def save_config_file(self, section, option, value):
        self.set_config(section, option, value)


if __name__ == "__main__":
    config = Config_Adapt("config.ini")
    print(config.get_config("lineEdit", "search_file_route"))
