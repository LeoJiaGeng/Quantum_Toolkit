import pandas as pd
from Public.decoration import Decorator


class Excels:
    """Excel 读写操作（仅 xlsx，pandas 实现）"""

    def __init__(self):
        pass

    # ----------------------------- 读 -----------------------------
    @Decorator.raise_err()
    def read_excel_lines(self,
                         filename,
                         search_list,
                         direction=0,
                         sheet_index=0,
                         get_start_rowx=0,
                         get_end_rowx=None,
                         get_start_col=0,      # 新增
                         get_end_col=None):    # 新增
        """
        direction=0  -> 按列读取（search_list 是列号）
        direction=1  -> 按行读取（search_list 是行号）
        新增 get_start_col / get_end_col 用来控制"列范围"，避免越界
        """
        ret = {"ret_val": True, "data": [], "info": "normal operation"}

        df = pd.read_excel(filename, sheet_name=sheet_index, header=None)

        if direction == 0:          # 读列
            for col_idx in search_list:
                ret["data"].append(
                    df.iloc[get_start_rowx:get_end_rowx, col_idx - 1].tolist()
                )
        elif direction == 1:        # 读行
            for row_idx in search_list:
                ret["data"].append(
                    df.iloc[row_idx - 1, get_start_col:get_end_col].tolist()
                )
        else:
            ret["ret_val"] = False
            ret["info"] = "input direction is wrong"
        return ret

    # ----------------------------- 写 -----------------------------
    @Decorator.raise_err()
    def write_excel_lines(self,
                          get_list,
                          direction=0,
                          filename="提取的源文件.xlsx",
                          set_start_row=0,
                          set_start_col=0):
        """
        把二维列表写入 xlsx
        direction=0  -> 按行写
        direction=1  -> 按列写（先转置）
        """
        ret = {"ret_val": True, "data": [], "info": "normal operation"}

        if direction not in (0, 1):
            ret["ret_val"] = False
            ret["info"] = "input direction is wrong"
            return ret

        df = pd.DataFrame(get_list)
        if direction == 1:
            df = df.T

        # 构造空白底板，再把数据块放到指定偏移
        rows, cols = df.shape
        full = pd.DataFrame(index=range(set_start_row + rows),
                            columns=range(set_start_col + cols),
                            dtype=object)
        full.iloc[set_start_row:set_start_row + rows,
                  set_start_col:set_start_col + cols] = df.values

        full.to_excel(filename, index=False, header=False)
        return ret

    # ------------------------- CSV 转 XLSX -------------------------
    @Decorator.raise_err()
    def csv_to_excel(self, csv_filename, xlsx_filename):
        ret = {"ret_val": True, "data": [], "info": "normal operation"}
        pd.read_csv(csv_filename).to_excel(xlsx_filename, index=False)
        return ret

    # ------------------------- TXT 转 XLSX -------------------------
    @Decorator.raise_err()
    def txt_to_excel(self, txt_filename, column_index, xlsx_filename="file.xlsx"):
        """
        读取任意空格分隔的 txt -> xlsx
        txt_filename   : 源 txt 文件路径
        column_index   : 作为表头的列名列表
        xlsx_filename  : 输出 xlsx 文件路径（默认 file.xlsx）
        """
        ret = {"ret_val": True, "data": [], "info": "normal operation"}
        (pd.read_table(txt_filename, sep=" ", header=None, names=column_index)
         .to_excel(xlsx_filename, index=False))
        return ret


# -------------------------- 自测入口 --------------------------
if __name__ == "__main__":
    file_name = r"C:\Users\DELL\Desktop\python\1.xlsx"
    A = Excels()
    print(A.csv_to_excel("60.csv", "60.xlsx"))
    print(A.read_excel_lines(file_name, [1, 2], direction=0))
    print(A.txt_to_excel("file.txt", ["日期", "编号", "城市"], "demo.xlsx"))
    print(A.write_excel_lines([[1, 2, 5, 5], [3, 4], [4, 5, 6]], direction=0))
