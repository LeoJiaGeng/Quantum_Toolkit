# Quantum - 量子化学数据处理工具

一个基于 PyQt5 的量子化学数据处理桌面应用程序，用于批量处理 Gaussian 计算结果。

## 功能特性

- **数据保存**：从 Gaussian 输出文件提取能量、频率、坐标等信息，导出为 Excel/Word
- **信息查询**：查看优化步骤特征值、虚频信息
- **文件转换**：批量生成 Gaussian 输入文件，支持多种计算模板
- **文件重命名**：批量文件名管理，支持预览和撤销

## 快速开始

### 环境要求

- Python 3.8+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python app.py
```

## 项目结构

```
Demo/
│
├── app.py                      # 程序入口
├── appMain.py                  # 主应用逻辑 (QmyApp)
├── ui_Start.py                 # UI 界面基类 (QmyWidget)
├── ui_Quantum.py               # Qt Designer 生成的表单
├── SplashModule.py             # 启动画面模块
├── ico_rc.py                   # 图标资源文件
│
├── quantum.py                  # 量子化学数据处理核心
├── gausInput.py                # Gaussian 输入文件生成
├── filenameMan.py              # 文件名管理器
├── folderMan.py                # 文件夹备份/恢复
├── config_adapt.py             # 配置适配器
│
├── Public/                     # 公共模块
│   ├── __init__.py
│   ├── Files.py                # 文件操作 (查找/重命名/保存)
│   ├── GetGaussData.py         # Gaussian 数据提取 (能量/坐标/频率)
│   ├── Excel.py                # Excel 读写 (pandas)
│   ├── Word.py                 # Word 文档生成 (python-docx)
│   ├── config.py               # INI 配置文件读写
│   ├── common.py               # 通用工具函数
│   └── decoration.py           # 装饰器 (异常处理/计时)
│
├── Model/                      # Gaussian 计算模板
│   ├── 模式1-PM6/
│   ├── 模式2-HF-6-31Gdp/
│   ├── 模式3-B3LYP-6-31Gdp/
│   ├── 模式4-M062X-6-31Gdp/
│   └── 模式5-M062X-AVDZ/
│
├── Styles/                     # QSS 主题样式
│   ├── dark.qss
│   ├── light.qss
│   └── ...
│
├── Langs/                      # 多语言翻译
│   ├── appLang_CN.qm
│   └── appLang_EN.qm
│
└── BackupFiles/                # 文件备份目录
```

## 模块架构

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py (入口)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              appMain.py (QmyApp - 主应用逻辑)                 │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │  保存页   │  查询页   │  转换页   │ 重命名页  │  设置页   │   │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │quantum.py│   │gausInput │   │filenameMan│   │folderMan │
    └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    Public/        │
                    │ ┌───────────────┐ │
                    │ │Files.py       │ │
                    │ │GetGaussData.py│ │
                    │ │Excel.py       │ │
                    │ │Word.py        │ │
                    │ │config.py      │ │
                    │ └───────────────┘ │
                    └───────────────────┘
```

## 核心模块说明

### 1. appMain.py - 主应用逻辑

`QmyApp` 类继承自 `QmyWidget`，实现四个功能模块：

| 模块 | 功能 | 核心方法 |
|------|------|---------|
| 保存页 | 提取能量/频率/坐标并导出 | `_process_energy()` |
| 查询页 | 查看 log 文件详细信息 | `_search_process_gauss_info()` |
| 转换页 | 批量生成 Gaussian 输入文件 | `_read_trans_params()` |
| 重命名页 | 批量文件重命名 | `_rename_read_params()` |

### 2. quantum.py - 数据提取核心

```python
class Quantum(ReFilenames):
    def read_file(header, save_energy_type, save_file_format)
    def save_frame(header, new_filename, save_energy_type, save_file_format)
```

支持提取的数据类型：
- Single Energy (HF 能量)
- Freq Energy (热力学修正)
- Frequency (频率)
- Coordinates (坐标)
- CBS/G4/W1 Energy (复合方法能量)

### 3. gausInput.py - 输入文件生成

```python
class GauInput:
    def trans_folder(foldername, prefix, suffix, exec_type, ...)
    def trans_file(filename, prefix, suffix, exec_type, ...)
```

支持的转换类型：
- `CHANGE-LEVEL` - 更换计算水平
- `IRC` / `IRC-SPLIT` - IRC 计算
- `HIGH-SP` - 高水平单点能
- `SPIN-TS` - 自旋测试
- `IRC-GJF` / `MOD-GJF` - 提取轨迹帧

### 4. Public/GetGaussData.py - 数据解析

`FindInfo` 类提供从 Gaussian 输出文件提取数据的方法：

```python
class FindInfo:
    def get_sp_energy(filename)      # HF 能量
    def get_freq_energy(filename)    # 热力学修正
    def get_freqs(filename)          # 频率列表
    def get_coord(filename)          # 优化坐标
    def get_cbs_energy(filename)     # CBS 能量
    def get_g4_energy(filename)      # G4 能量
```

### 5. Public/Files.py - 文件操作

```python
class ReFilenames:
    def get_all_files(dir, only_name, without_suffix, only_curdir)
    def filename_and_fileabsroute(foldername, only_curdir)
    def rename_file(old_name, new_name)

class SaveFile:
    def save(filename, dataList)
```

## 配置文件

程序运行时会在当前目录生成 `quantum_config.ini`，保存：
- 界面控件状态
- 最近使用的文件夹路径
- ComboBox 历史记录

## 模板系统

`Model/` 目录下的模板文件用于生成 Gaussian 输入：

```
Model/模式X-计算方法/
├── INPUT-template.txt      # 通用输入
├── OPT-template.txt        # 几何优化
├── TS-template.txt         # 过渡态搜索
├── IRC-template.txt        # IRC 计算
├── HIGH-SP-template.txt    # 高水平单点
└── ...
```

模板中使用占位符：
- `replace-name` → 文件名
- `replace-coordinate` → 分子坐标
- `replace-charge` → 电荷
- `replace-multiplicity` → 自旋多重度

## 多语言支持

通过 Qt 翻译系统实现中英文切换：
- 翻译文件位于 `Langs/` 目录
- 设置页可切换语言

## 打包发布

使用 PyInstaller 打包为可执行文件：

``` bash
Tools/exe.bat 是可执行打包程序，里面包含设置Python的虚拟环境，还有设置rar.exe的环境变量
Tools/uic_qua.bat 是desginer的ui文件转换成py文件的脚本，保持文件目录框架，修改ui后点击运行可以直接同步到py中
```

## 许可证

MIT License

## 作者

jxiong@whu.edu.cn
