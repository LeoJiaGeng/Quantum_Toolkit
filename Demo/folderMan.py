import shutil
import pathlib
from Public.config import Config   # 你的 config.py


class FolderManager:
    def __init__(self, bf_dir='BackupFiles', ini='backup.ini'):
        self.bf_dir = pathlib.Path(bf_dir)
        self.ini = ini
        self.cfg = Config(self.ini)          # 直接用你写好的类
        self.bf_dir.mkdir(exist_ok=True)

    # ---------- 备份 ----------
    def backup(self, src):
        src = pathlib.Path(src).resolve()
        if not src.exists():
            raise FileNotFoundError(src)

        # 1. 清空 backup 目录
        for it in self.bf_dir.iterdir():
            if it.is_dir():
                shutil.rmtree(it)
            else:
                it.unlink()

        # 2. 复制
        dst = self.bf_dir / src.name
        shutil.copytree(src, dst, dirs_exist_ok=False)

        # 3. 写 ini（用你的函数）
        self.cfg.remove_section('BACKUP')      # 清掉旧节
        self.cfg.add_section('BACKUP')
        self.cfg.set_config('BACKUP', 'src', str(src))
        return dst

    # ---------- 还原 ----------
    def restore(self):
        # 读源路径
        ret = self.cfg.get_config('BACKUP', 'src')
        if not ret['ret_val']:
            raise FileNotFoundError('backup.ini 里找不到备份记录')
        src_path = pathlib.Path(ret['data'])
        dst_path = self.bf_dir / src_path.name

        if not dst_path.exists():
            raise FileNotFoundError('备份目录不存在')

        # 先删原目录，再拷回
        if src_path.exists():
            shutil.rmtree(src_path)
        shutil.copytree(dst_path, src_path)
        return src_path


if __name__ == '__main__':
    fm = FolderManager()
    # 备份
    fm.backup(r'D:\tmp')
    # 还原
    fm.restore()
