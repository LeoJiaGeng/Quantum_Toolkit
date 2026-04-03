# recifyName.py —— 单个文件重命名版（自动避免重复）
import os
from Public.Files import ReFilenames


class FilenameManager:
    """
    文件名管理器
    - 核心功能：单个文件重命名，自动避免冲突
    - 批量功能：通过 batch_process() 提取循环逻辑
    """

    def __init__(self, only_curdir=True):
        """
        初始化
        :param only_curdir: 批量处理时是否只处理当前目录（不递归子目录）
        """
        self.rf = ReFilenames()
        self.confirm_transfer = False
        self.only_curdir = only_curdir

    def switch(self, on):
        """设置是否实际执行重命名（True=执行，False=预览）"""
        self.confirm_transfer = bool(on)

    # ---------------- 操作分发表（保持不变）----------------
    _OPS = {
        'del': lambda self, path, l1, l2, txt: self._del(path, l1, l2),
        'add': lambda self, path, l1, l2, txt: self._add(path, l1, txt),
        'replace': lambda self, path, l1, l2, txt: self._replace(path, l1, l2, txt),
        'case': lambda self, path, l1, l2, txt: self._case(path, l1, l2),
        'insert': lambda self, path, l1, l2, txt: self._insert(path, l1, txt),
    }

    # ---------------- 核心入口：单个文件处理 ----------------
    def main(self, file_path, operation, loc1=0, loc2=None, new_content=''):
        """
        处理单个文件的重命名
        :return: 新的完整文件名（不含路径）
        """
        if operation not in self._OPS:
            raise ValueError(f'不支持的 operation: "{operation}"，支持: {list(self._OPS.keys())}')

        return self._OPS[operation](self, file_path, loc1, loc2, new_content)

    # ---------------- 批量处理：循环逻辑提取 ----------------
    def batch_process(self, folder_path, operation, loc1=0, loc2=None, new_content=''):
        """
        批量处理文件夹内所有文件（复用单个文件逻辑）
        :return: 新文件名列表，失败项为 None
        """
        results = []
        for file_path in self.rf.get_all_files_in_folder(folder_path, self.only_curdir):
            try:
                result = self.main(file_path, operation, loc1, loc2, new_content)
                results.append(result)
            except Exception as e:
                print(f"❌ 处理失败 {file_path}: {e}")
                results.append(None)
        return results

    # ---------------- 功能实现（全部改为单个文件） ----------------
    def _del(self, file_path, l1, l2):
        """删除文件名中 [l1:l2] 区间的字符"""
        folder, _, raw, sfx = self.rf.get_file_detail(file_path)
        new_raw = raw[:l1] + (raw[l2:] if l2 is not None else '')
        self._maybe_rename(file_path, folder, new_raw, sfx)
        return new_raw + sfx

    def _add(self, file_path, l1, txt):
        """在位置 l1 处添加文本"""
        folder, _, raw, sfx = self.rf.get_file_detail(file_path)
        new_raw = raw[:l1] + txt + raw[l1:]
        self._maybe_rename(file_path, folder, new_raw, sfx)
        return new_raw + sfx

    def _replace(self, file_path, l1, l2, txt):
        """替换文件名中 [l1:l2] 区间的文本"""
        if l1 == 0 and l2 == 0:  # 特判：不替换
            _, _, raw, sfx = self.rf.get_file_detail(file_path)
            return raw + sfx

        folder, _, raw, sfx = self.rf.get_file_detail(file_path)
        new_raw = raw[:l1] + txt + raw[l2:]
        self._maybe_rename(file_path, folder, new_raw, sfx)
        return new_raw + sfx

    def _case(self, file_path, l1, l2):
        """切换文件名中 [l1:l2] 区间的大小写"""
        folder, _, raw, sfx = self.rf.get_file_detail(file_path)
        seg = raw[l1:l2]
        new_raw = raw[:l1] + seg.swapcase() + raw[l2:]
        self._maybe_rename(file_path, folder, new_raw, sfx)
        return new_raw + sfx

    def _insert(self, file_path, l1, txt):
        """在位置 l1 处插入文本（支持 {idx} 占位符）"""
        folder, _, raw, sfx = self.rf.get_file_detail(file_path)
        # 单个文件模式下 idx 固定为 1
        new_raw = raw[:l1] + txt.format(idx=1) + raw[l1:] + sfx
        self._maybe_rename(file_path, folder, new_raw, sfx)
        return new_raw + sfx

    # ---------------- 重命名核心：自动避免重复 ----------------
    def _maybe_rename(self, old_path, folder, new_raw, sfx):
        if self.confirm_transfer:
            new_abs_name = self.rf.combine_file(folder, new_raw, sfx)
            self.rf.rename_file(old_path, new_abs_name)

    def rename_check(self, new_name_list):
        """
        检查新文件名列表是否有重复（保留原接口，主要用于批量场景）
        :return: 列表，1 表示有效，0 表示无效（重复）
        """
        freq = {}
        for name in new_name_list:
            freq[name] = freq.get(name, 0) + 1

        return [0 if freq[name] > 1 else 1 for name in new_name_list]

    # --------- 对外接口（兼容旧版）----------
    def rename_files(self, file_path, operation, loc1=0, loc2=None, new_content=''):
        """
        对外的接口函数（现在处理单个文件）
        如需批量处理，请使用 batch_process() 方法
        """
        return self.batch_process(file_path, operation, loc1, loc2, new_content)

    def rename_after(self, file_path, operation, loc1=0, loc2=None, new_content=''):
        if operation == 'del':
            loc2 = loc1
            loc1 = 0
        elif operation == 'add':
            loc1 = loc1
            loc2 = None
        elif operation == 'case':
            loc2 = loc1
            loc1 = 0
        elif operation == 'replace':
            loc2 = loc1
            loc1 = 0
        elif operation == 'insert':
            loc2 = loc1
            loc1 = 0
        return self.main(file_path, operation, loc1, loc2, new_content)

    def rename_before(self, file_path, operation, loc1=0, loc2=None, new_content=''):
        if operation == 'del':
            loc1 = loc1
            loc1 = 0
        elif operation == 'add':
            loc1 = loc1
            loc2 = None
        elif operation == 'case':
            loc2 = loc1
            loc1 = 0
        elif operation == 'replace':
            loc2 = loc1
            loc1 = 0
        elif operation == 'insert':
            loc2 = loc1
            loc1 = 0
        return self.main(file_path, operation, loc1, loc2, new_content)


if __name__ == '__main__':
    fm = FilenameManager()
    fm.switch(False)          # 仅预览
    cases = [
        # del 不能后面比前面大
        (r'D:\tmp', 'del', 0, 0),
        (r'D:\tmp', 'del', 0, 4),
        (r'D:\tmp', 'del', 4, 8),
        (r'D:\tmp', 'del', 8, 4),
        # add 只写一个位置即可
        (r'D:\tmp', 'add', 0, None, 'NEW-'),
        (r'D:\tmp', 'add', 3, None, '-INS'),
        (r'D:\tmp', 'add', 100, None, '_END'),
        # replace 可以跨越边界
        (r'D:\tmp', 'replace', 0, 0, 'M'),
        (r'D:\tmp', 'replace', 0, 1, 'm'),
        (r'D:\tmp', 'replace', 4, 7, 'XYZ'),
        (r'D:\tmp', 'replace', 7, 100, 'END'),
        # case
        (r'D:\tmp', 'case', 0, 0),
        (r'D:\tmp', 'case', 0, 3),
        (r'D:\tmp', 'case', 4, 7),
        # insert 可以用 {} 格式化
        (r'D:\tmp', 'insert', 0, None, '{idx}_'),
        (r'D:\tmp', 'insert', 100, None, '_No{idx}'),
        (r'D:\tmp', 'insert', 6, None, '_{idx}')
    ]
    for path, op, l1, l2, *rest in cases:
        txt = rest[0] if rest else ''
        res = fm.main(path, op, l1, l2, txt)
        print(f'{op}  {l1=} {l2=} {txt=} -> {res}')
