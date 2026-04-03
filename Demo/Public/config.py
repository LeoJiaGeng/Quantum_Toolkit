from configparser import ConfigParser
import os
from Public.decoration import Decorator   # 你的装饰器
# from decoration import Decorator   # 你的装饰器


class Config():
    def __init__(self, file_name='config.ini'):
        self.file_name = file_name
        self.config = ConfigParser()
        # if self.file_name not in os.listdir(os.getcwd()):
        #     self.init_config_file()
        self.config.read(self.file_name, encoding="utf-8")

    def init_config_file(self):
        """Will be override in the child class, only for testing"""
        self.add_section("save")
        self.set_config("save", "file_name", "D:/Document")
        self.set_config("save", "save_file_name", "D:/Document")
        self.add_section("search")
        self.set_config("search", "file_name", "D:/Document")

    @Decorator.raise_err()
    def save(self):
        """Save the configuration"""
        with open(self.file_name, "w+", encoding="utf-8") as file_obj:
            self.config.write(file_obj)

    @Decorator.raise_err()
    def get_config(self, section, option):
        """"Returns the value of option in the section"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_option(section, option):
            ret["ret_val"] = False
            ret["info"] = "there is no section or option"
            return ret

        ret["data"] = self.config[section][option]
        return ret

    @Decorator.raise_err()
    def set_config(self, section, option, value):
        """Set the value in the option of the section, if no the option, to create it """
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there is no section"
        elif not self.config.has_option(section, option):
            ret["info"] = "there is no option, but create one"

        self.config.set(section, option, value)
        self.save()
        return ret

    @Decorator.raise_err()
    def add_section(self, section):
        """Add a section to the configuration"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}
        if self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there has already this section"
            return ret

        self.config.add_section(section)
        self.save()
        return ret

    @Decorator.raise_err()
    def remove_section(self, section):
        """Remove a section to the configuration"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}
        if not self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there is no section"
            return ret

        self.config.remove_section(section)
        self.save()
        return ret

    @Decorator.raise_err()
    def remove_option(self, section, option):
        """Remove a option to the configuration"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_option(section, option):
            ret["ret_val"] = False
            ret["info"] = "there is no section or option"
            return ret

        self.config.remove_option(section, option)
        self.save()
        return ret

# ----------------针对list类型的配置项的操作-----------------
    @Decorator.raise_err()
    def append_config_list(self, section, option, value):
        """Append a value to existing option in the section if it doesn't exist"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there is no section"
            return ret

        current_value = self.get_config(section, option)
        if current_value["ret_val"]:
            # Get list of existing values
            existing_values = current_value["data"].split(";")
            # Check if value already exists
            if value in existing_values:
                ret["info"] = "value already exists"
                return ret
            # If not exists, append it
            new_value = current_value["data"] + ";" + value
        else:
            # If no value exists, create new one
            new_value = value

        self.config.set(section, option, new_value)
        self.save()
        return ret

    @Decorator.raise_err()
    def get_config_list(self, section, option):
        """Returns list of values from the option in the section"""
        ret = {"ret_val": True, "data": [], "info": "normal operation"}

        result = self.get_config(section, option)
        if not result["ret_val"]:
            return result

        ret["data"] = result["data"].split(";")
        return ret

    @Decorator.raise_err()
    def insert_config(self, section, option, value):
        """Insert a value to the beginning of the list or move it to front if exists"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there is no section"
            return ret

        current_value = self.get_config(section, option)
        if current_value["ret_val"]:
            # Get list of existing values
            existing_values = current_value["data"].split(";")
            # Remove value if exists
            if value in existing_values:
                existing_values.remove(value)
                ret["info"] = "move value to front"
            else:
                ret["info"] = "insert new value to front"
            # Insert value at beginning
            existing_values.insert(0, value)
            # Join back to string
            new_value = ";".join(existing_values)
        else:
            # If no value exists, create new one
            new_value = value

        self.config.set(section, option, new_value)
        self.save()
        return ret

    @Decorator.raise_err()
    def control_config_list(self, section, option, length=10):
        """Delete a value from the list in the option of the section"""
        ret = {"ret_val": True, "data": "", "info": "normal operation"}

        if not self.config.has_section(section):
            ret["ret_val"] = False
            ret["info"] = "there is no section"
            return ret

        current_value = self.get_config_list(section, option)
        new_value = current_value["data"][:length]

        self.set_config(section, option, ";".join(new_value))
        return ret


if __name__ == "__main__":
    config = Config()
    # 添加一些测试数据
    config.append_config_list("save", "file_name", "D:/Document")
    config.append_config_list("save", "file_name", "D:/Document/ts")
    config.append_config_list("save", "file_name", "D:/Document/test")

    # 插入新值到开头
    config.insert_config("save", "file_name", "D:/New")
    result = config.get_config_list("save", "file_name")
    print("插入新值后:", result["data"])  # ['D:/New', 'D:/Document', 'D:/Document/ts', 'D:/Document/test']

    # 将已存在的值移到开头
    config.insert_config("save", "file_name", "D:/Document/ts")
    result = config.get_config_list("save", "file_name")
    print("移动已有值到开头:", result["data"])  # ['D:/Document/ts', 'D:/New', 'D:/Document', 'D:/Document/test']
