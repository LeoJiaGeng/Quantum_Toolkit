import re
from pathlib import Path

# 元素周期表 1-118，索引 0 占位，1=H, 2=He, … 8=O
ELEMENTS = [
    "", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
]


class FindInfo():
    # 列表用于查找cbs能量
    cbs_key = ["UMP4(SDQ)", "CCSD(T)", "EUMP2", "UMP4(SDQ)",
               "SCF Done:  E(RHF)", "CBS-Int", "OIii", "T1 Diagnostic"]
    rocbs_key = ["ROMP4(SDQ)", "CCSD(T)", "E(PMP2)", "ROMP4(SDQ)",
                 "SCF Done:  E(ROHF)", "CBS-Int", "OIii", "T1 Diagnostic"]
    coordinates_key = ["Redundant internal coordinates",
                       "Recover connectivity data from disk"]

    def __init__(self):
        pass

    def _extract_hf_value(self, file_path):
        """
        从 Gaussian 日志文件末尾开始，每两段拼接后查找 |HF=...| 的值。
        拼接前会 strip 每一行，拼接时去掉换行符。
        返回第一个匹配到的符号数字字符串，未找到返回 None。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f.readlines()[::-1]]   # 倒序并去空格

        for i in range(len(lines) - 1):
            combined = (lines[i + 1] + lines[i]).replace('\n', '')
            out_match = re.search(r'\|HF=([+-]?\d+\.\d+)\|', combined)
            log_match = re.search(r'\\HF=([+-]?\d+\.\d+)\\', combined)
            if out_match:
                return out_match.group(1)
            if log_match:
                return log_match.group(1)
        return []

    def _extract_zpe_value(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f.readlines()[::-1]]   # 倒序并去空格

        for i in range(len(lines) - 1):
            combined = (lines[i + 1] + lines[i]).replace('\n', '')
            out_match = re.search(r'\|ZeroPoint=(\d+\.\d+)\|', combined)
            log_match = re.search(r'\\ZeroPoint=(\d+\.\d+)\\', combined)
            if out_match:
                return float(out_match.group(1))
            if log_match:
                return float(log_match.group(1))
        return []

    def _extract_thermal_corrections(self, file_path):
        """
        从 Gaussian 日志文件中提取 8 个能量/修正值，按上面约定顺序返回。
        若任一值缺失，返回 None。
        """
        patterns = {
            "zpc": r"Zero-point correction=\s+([\d.-]+)",
            "tec": r"Thermal correction to Energy=\s+([\d.-]+)",
            "thc": r"Thermal correction to Enthalpy=\s+([\d.-]+)",
            "tgc": r"Thermal correction to Gibbs Free Energy=\s+([\d.-]+)",
            "zp": r"Sum of electronic and zero-point Energies=\s+([\d.-]+)",
            "therm": r"Sum of electronic and thermal Energies=\s+([\d.-]+)",
            "enth": r"Sum of electronic and thermal Enthalpies=\s+([\d.-]+)",
            "free": r"Sum of electronic and thermal Free Energies=\s+([\d.-]+)",
        }
        order = ["zpc", "tec", "thc", "tgc", "zp", "therm", "enth", "free"]

        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        res = []
        for key in order:
            m = re.search(patterns[key], text)
            if not m:
                return []
            res.append(float(m.group(1)))
        # old version:
        # hf = res[4]-res[0]
        # res = order[:2]+[hf]+[order[4]]+[order[-1]]
        hf = self._extract_hf_value(file_path)
        res.insert(4, float(hf))
        return res

    def _extract_rot_mass_dof(self, file_path):
        """
        从 Gaussian 日志文件末尾开始，提取第一次出现的
        Rotational constants (GHZ): 三个值 + 包括分子量 + 频率数目
        返回顺序：(A, B, C, mass, dof)
        任一缺失返回 None
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[::-1]          # 倒序扫描

        pat_rot = re.compile(r'Rotational constants \(GHZ\):\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)')
        pat_mass = re.compile(r'Molecular mass:\s+([\d.-]+)\s+amu\.')
        pat_dof = re.compile(r'Deg\. of freedom\s+(\d+)')

        x = y = z = mass = dof = None

        for ln in lines:
            if x is None:
                m = pat_rot.search(ln)
                if m:
                    x, y, z = map(float, m.groups())
            if mass is None:
                m = pat_mass.search(ln)
                if m:
                    mass = float(m.group(1))
            if dof is None:
                m = pat_dof.search(ln)
                if m:
                    dof = int(m.group(1))
            if all(v is not None for v in (x, y, z, mass, dof)):
                x_new = round((x / 30.0), 6)
                y_new = round((y / 30.0), 6)
                z_new = round((z / 30.0), 6)
                return [x, y, z, x_new, y_new, z_new, mass, dof]
        return []

    def _extract_last_input_orientation(self, file_path, combine_symbol):
        """
        从后往前找第一个 Input orientation: 坐标块，
        返回 ["El X Y Z", ...] 字符串列表；找不到返回 None。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[::-1]   # 倒序

        # 定位坐标表头
        start_idx = None
        for i, line in enumerate(lines):
            if "Input orientation:" in line:
                start_idx = i
                break
        if start_idx is None:
            return None

        search_lines = lines[start_idx::-1]  # 再次正序
        return self.__extract_coord_block(search_lines, combine_symbol)

    def __extract_coord_block(self, search_lines, combine_symbol="   "):
        # 正则匹配坐标行：Center Number | Atomic Number | Atomic Type | X | Y | Z
        # 只用传入给定好的字符串文件列表，索引自己提前做好
        coord_pat = re.compile(r'^\s*\d+\s+(\d+)\s+\d+\s+([-]?\d+\.\d+)\s+([-]?\d+\.\d+)\s+([-]?\d+\.\d+)')
        res = []
        read_flag = False

        # 从表头向下扫，遇到 ---- 行两次，第二次之后开始抓坐标；遇到下一个 ---- 结束
        dash_count = 0
        for line in search_lines:
            if "Input orientation:" in line:  # 再次确认
                read_flag = True
                continue
            if '----' in line and read_flag:
                dash_count += 1
                continue
            if dash_count == 2:          # 已到达数据区
                m = coord_pat.match(line)
                if m:
                    anum = int(m.group(1))
                    el = ELEMENTS[anum] if anum < len(ELEMENTS) else f"X{anum}"
                    x, y, z = m.groups()[1:]
                    if combine_symbol == "   ":
                        new_line = f"{el:<2}{x:>12}{y:>12}{z:>12}"
                        res.append(new_line)
                    else:
                        read_coord = f"{el} {x} {y} {z}"
                        res.append(read_coord.replace(" ", combine_symbol))
            if dash_count == 3:   # 遇到下一个分隔行即结束
                break
        return res if res else []

    def _extract_irc_scan_frames(self, file_path, combine_symbol="   "):
        charge, spin, state = self._extract_charge_spin_state(file_path)
        all_list = []
        if state == "OPT":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "Optimization completed" in line:
                        coord = self.__extract_coord_block(lines[i:], combine_symbol)
                        coord.append([charge, spin, state])
                        all_list.append(coord)
            return all_list
        elif state == "IRC":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            file_list = self.__extract_irc_point_path(file_path)
            for i in range(len(file_list)):
                if i == len(file_list) - 1:
                    search_lines = lines[file_list[i][0]:]
                else:
                    search_lines = lines[file_list[i][0]:file_list[i + 1][0]]
                coord = self.__extract_coord_block(search_lines, combine_symbol)
                coord.append([charge, spin, state])
                file_list[i][0] = coord

            # 1. 拆成两组
            g2 = [row for row in file_list if row[2] == 2]   # path_num == 2
            g1 = [row for row in file_list if row[2] == 1]   # path_num == 1

            # 2. 行号分别倒序 / 正序
            g2_line = [row[0] for row in g2][::-1]      # 倒序
            g1_line = [row[0] for row in g1]            # 正序

            all_list.extend(g2_line)
            all_list.extend(g1_line)
            return all_list
        return []

    def __extract_irc_point_path(self, file_path):
        """
        打开文本文件，提取所有匹配行。
        返回：[[行号, point_num, path_num], ...]
        """
        pattern = re.compile(r'Point Number:\s+(\d+)\s+Path Number:\s+(\d+)')
        results = []

        # 自动兼容 GBK / UTF-8
        try:
            text = Path(file_path).read_text(encoding='utf-8')
        except UnicodeDecodeError:
            text = Path(file_path).read_text(encoding='gbk', errors='ignore')

        for lineno, line in enumerate(text.splitlines(), 1):
            m = pattern.search(line)
            if m:
                results.append([lineno, int(m.group(1)), int(m.group(2))])
        return results

    def _extract_charge_spin_state(self, file_path):
        pattern = re.compile(r'Charge\s*=\s*(-?\d+)\s+Multiplicity\s*=\s*(\d+)')
        RE_IRC = re.compile(r'\birc\b', re.I)
        RE_TS = re.compile(r'\bopt\s*=\s*\([^)]*ts[^)]*noeigen[^)]*\)', re.I)
        RE_SCAN = re.compile(r'\bopt\s*=\s*\(?mod\b', re.I)
        RE_OPT = re.compile(r'\bopt\b', re.I)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 从文件头开始逐行读取
            state = "Unknown"
            for line in f:
                match = pattern.search(line)
                if "#" in line:
                    line = line.strip()          # 原始行，保留大小写
                if RE_IRC.search(line):
                    state = "IRC"
                    continue
                if RE_TS.search(line):
                    state = "TS"
                    continue
                if RE_SCAN.search(line):
                    state = "SCAN"
                    continue
                if RE_OPT.search(line):
                    state = "OPT"
                    continue

                if match:
                    charge = int(match.group(1))
                    multiplicity = int(match.group(2))
                    return [charge, multiplicity, state]
        return []

    def check_list_all_digit(self, check_list):
        if len(check_list) == 1:
            return False
        for num in check_list:
            if not ((str(num).isdigit()) or (num[0] == '-' and num[1:].isdigit())):
                return False
            return True

    def _extract_input_coord_charge_spin(self, file_path, only_corrds=True):
        ret_list = []
        write_flag = False
        # 只允许进入一次读取坐标
        flag_times = 0
        with open(file_path) as file_obj:
            for line in file_obj.readlines():
                # 仅读取坐标，坐标空行后的信息丢弃
                if only_corrds:
                    if write_flag and line == '\n':
                        write_flag = False
                if write_flag:
                    ret_list.append(line[:-1])  # 去掉末尾的换行符
                    # 通过电荷和自旋多重度的数字特性来判断位置是否开始
                if self.check_list_all_digit(list(line.strip().split(" "))):
                    if flag_times == 0:
                        write_flag = True
                        charge, multiplicity = list(line.strip().split(" "))
                    flag_times += 1
        ret_list.append([charge, multiplicity, "Unknown"])
        return ret_list

    def _extract_all_frequencies(self, file_path):
        """
        按出现顺序提取日志中所有 Frequencies -- 后的数字（一行 1~N 个都收）。
        返回 List[float]，无则返回空列表。
        """
        freq_pat = re.compile(r'Frequencies --\s+((?:\s+[-]?\d+(?:\.\d+)?)+)')
        freqs = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                m = freq_pat.search(line)
                if m:
                    # 把匹配到的整个数字串再按空白拆分
                    numbers = m.group(1).split()
                    freqs.extend(float(n) for n in numbers)
        return ",".join(map(str, freqs))

    def _extract_steps_information(self, file_path):
        patt_step = re.compile(r'Step number\s+(\d+).*?(?=Step number|\Z)', re.S)
        patt_eig = re.compile(r'Eigenvalues ---\s+((?:[-+]?\d+\.\d+(?:e[+-]?\d+)?\s+){4})', re.I)
        # patt_d    = re.compile(
        #     r'Eigenvectors required to have negative eigenvalues:.*?\n\s+1\s+((?:[-+]?\d+\.\d+\s+){4})', re.S)
        patt_d = re.compile(
            r'Eigenvectors required to have negative eigenvalues:\s*\n\s*((?:\S+\s+){4})', re.S)
        patt_for = re.compile(
            r'Maximum Force\s+([-+]?\d+\.\d+(?:e[+-]?\d+)?)\s+[\d.e+-]+\s+(NO|YES).*?'
            r'RMS\s+Force\s+([-+]?\d+\.\d+(?:e[+-]?\d+)?)\s+[\d.e+-]+\s+(NO|YES).*?'
            r'Maximum Displacement\s+([-+]?\d+\.\d+(?:e[+-]?\d+)?)\s+[\d.e+-]+\s+(NO|YES).*?'
            r'RMS\s+Displacement\s+([-+]?\d+\.\d+(?:e[+-]?\d+)?)\s+[\d.e+-]+\s+(NO|YES)', re.S)

        # 初始化两个输出列表
        out_detailed = ["No" + 4 * " Eig_val" + 4 * " Eig_vec" + 8 * " Num|Stu"]
        out_concise = ["No" + 2 * " Eig_val" + 3 * " Eig_vec" + 4 * " Stu"]

        with open(file_path, 'r', encoding='utf-8') as f:
            txt = f.read()

        for m in patt_step.finditer(txt):
            step_num = int(m.group(1))
            block = m.group(0)

            e = patt_eig.search(block)
            d = patt_d.search(block)
            f = patt_for.search(block)

            # 全部没有才跳过
            if not any([e, d, f]):
                continue

            # 提取数据，缺失的部分用 None 占位
            e4 = e.group(1).split()[:4] if e else [None] * 4
            d4 = d.group(1).split()[:4] if d else [None] * 4
            f_groups = list(f.groups()) if f else [None] * 8

            # 详细版（完整输出）
            pieces_detailed = [str(step_num)] + e4 + d4 + f_groups
            out_detailed.append(' '.join(str(p) if p is not None else "None" for p in pieces_detailed))

            # 精简版（序号+2个eig1+3个eig2+4个状态）
            pieces_concise = [str(step_num)] + e4[:2] + d4[:3] + [f_groups[i] for i in [1, 3, 5, 7]]
            out_concise.append(' '.join(str(p) if p is not None else "None" for p in pieces_concise))

        return out_detailed, out_concise

    def str_to_digit(self, str_cont):
        """Converts a string with letter D+- to a digit"""
        cont_list = list(str_cont.strip().split("D+"))
        return round((float(cont_list[0]) * 10**int(cont_list[1])), 6)

    def _extract_multi_cbs_energy(self, file_path):
        """查找多重CBS能量"""
        cbs_energy_list = [0] * (len(self.cbs_key) + 1)
        flag = 0
        with open(file_path, mode="r", buffering=-1, encoding="utf-8") as fileObj:
            file_lines = fileObj.readlines()
            for line in file_lines:
                if self.cbs_key[0] in line and flag == 0:  # MP4
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[0] = (self.str_to_digit(energy))
                    flag = 1
                if self.cbs_key[1] in line and flag == 1 and len(line) < 30:  # CCSD
                    energy = list(line.strip().split("= "))[-1]
                    cbs_energy_list[1] = (self.str_to_digit(energy))
                if "Normal termination" in line and flag != 3 and flag != 4:
                    flag = 2
                if self.cbs_key[2] in line and flag == 2:  # MP2
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[2] = (self.str_to_digit(energy))
                    flag = 3
                if self.cbs_key[3] in line and flag == 3:  # MP4
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[3] = (self.str_to_digit(energy))
                if "Normal termination" in line and flag != 2:
                    flag = 4
                if self.cbs_key[4] in line and flag == 4:  # hf
                    energy = list(line.strip().split(" "))[6]
                    cbs_energy_list[4] = (float(energy))
                    flag = 5
                if self.cbs_key[6] in line and flag == 5:  # INT
                    energy = list(line.strip().split(" "))
                    e2_cbs = float(energy[6])
                    cbs_int = float(energy[14])
                    cbs_energy_list[5] = (e2_cbs + cbs_int)
                    flag = 6
                if self.cbs_key[5] in line and flag == 6:  # OIII
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[6] = (float(energy))
                    break
                if self.cbs_key[7] in line:  # T1 value
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[7] = (float(energy))

        delta_ccsd = cbs_energy_list[1] - cbs_energy_list[0]
        delta_cbs = cbs_energy_list[3] - cbs_energy_list[2]
        mp2 = cbs_energy_list[4] + cbs_energy_list[5] - cbs_energy_list[6] * 0.00579
        final_energy = round((delta_ccsd + delta_cbs + mp2), 6)
        cbs_energy_list[8] = (final_energy)
        # print("文件{}cbs能量查找完毕\n".format(file_path))
        return cbs_energy_list

    def _extract_multi_rocbs_energy(self, file_path):
        """查找DL-ROCBS-Q的能量"""
        cbs_energy_list = [0] * (len(self.rocbs_key) + 1)  # 加上总计值
        flag = 0
        with open(file_path, mode="r", buffering=-1, encoding="utf-8") as fileObj:
            file_lines = fileObj.readlines()
            for line in file_lines:
                if self.rocbs_key[0] in line and flag == 0:  # MP4
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[0] = (self.str_to_digit(energy))
                    flag = 1
                if self.rocbs_key[1] in line and flag == 1 and len(line) < 30:  # CCSD
                    energy = list(line.strip().split("= "))[-1]
                    cbs_energy_list[1] = (self.str_to_digit(energy))
                if "Normal termination" in line and flag != 3 and flag != 4:
                    flag = 2
                if self.rocbs_key[2] in line and flag == 2:  # MP2
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[2] = (self.str_to_digit(energy))
                    flag = 3
                if self.rocbs_key[3] in line and flag == 3:  # MP4
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[3] = (self.str_to_digit(energy))
                if "Normal termination" in line and flag != 2:
                    flag = 4
                if self.rocbs_key[4] in line and flag == 4:  # hf
                    energy = list(line.strip().split(" "))[6]
                    cbs_energy_list[4] = (float(energy))
                    flag = 5
                if self.cbs_key[5] in line and flag == 5:  # INT
                    energy = list(line.strip().split(" "))
                    e2_cbs = float(energy[6])
                    cbs_int = float(energy[14])
                    cbs_energy_list[5] = (e2_cbs + cbs_int)
                    flag = 6
                if self.cbs_key[6] in line and flag == 6:  # OIII
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[6] = (float(energy))
                    break
                if self.cbs_key[7] in line:  # T1 value
                    energy = list(line.strip().split(" "))[-1]
                    cbs_energy_list[7] = (float(energy))

        delta_ccsd = cbs_energy_list[1] - cbs_energy_list[0]
        delta_cbs = cbs_energy_list[3] - cbs_energy_list[2]
        mp2 = cbs_energy_list[4] + cbs_energy_list[5] - cbs_energy_list[6] * 0.00579
        final_energy = round((delta_ccsd + delta_cbs + mp2), 6)
        cbs_energy_list[8] = (final_energy)

        # print("文件{}cbs能量查找完毕\n".format(file_path))
        return cbs_energy_list

    def __process_single_energy(self, file_path, pattern):
        """
        从文件读取，提取所有匹配的能量值
        Args:
            file_path: 要读取的文件路径
        Returns:
            list: 提取的所有能量值字符串（单位：Hartree），按文件中出现的顺序
        """
        matches = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

            # 从后往前查找所有匹配项
            for line in reversed(lines):
                match = pattern.search(line)
                if match:
                    matches.append(match.group(1))

        if len(matches) == 0:
            matches = ["Nan"]
        else:
            # 反转列表恢复原始顺序（文件中先出现的在前）
            matches.reverse()
        return matches

    def _extract_cbs_energy(self, file_path):
        # 编译正则表达式：匹配 E(CBS-QB3)= 后跟的能量值
        # 支持格式：-1419.515046, -1.234e-10, 2.34E+05
        # 返回字符串形式的能量值
        pattern = re.compile(r'E\(CBS-QB3\)=\s+(-?\d+\.\d+(?:[Ee][+-]?\d+)?)')
        return self.__process_single_energy(file_path, pattern)[-1]

    def _extract_g4_energy(self, file_path):
        pattern = re.compile(r'E\(G4\)=\s+(-?\d+\.\d+(?:[Ee][+-]?\d+)?)')
        return self.__process_single_energy(file_path, pattern)[-1]

    def _extract_w1_energy(self, file_path, match_str1, match_str2):
        # W1 match
        # pattern = re.compile(r'E\(W1\)=\s+(-?\d+\.\d+(?:[Ee][+-]?\d+)?)')
        pattern1 = re.compile(match_str1, re.S)
        pattern2 = re.compile(match_str2, re.S)
        match_list1 = self.__process_single_energy(file_path, pattern1)
        match_list2 = self.__process_single_energy(file_path, pattern2)

        energy_float_list1 = []
        energy_float_list2 = []
        for energy_str1 in match_list1:
            try:
                energy_float_list1.append(float(energy_str1))
            except ValueError:
                # 处理转换错误（可选：跳过或记录日志）
                print(f"警告：无法将 '{energy_str1}' 转换为浮点数，已跳过")
                continue

        for energy_str2 in match_list2:
            try:
                energy_float_list2.append(float(energy_str2))
            except ValueError:
                # 处理转换错误（可选：跳过或记录日志）
                print(f"警告：无法将 '{energy_str2}' 转换为浮点数，已跳过")
                continue
        energy_float_list1.extend(energy_float_list2)
        return energy_float_list1

    def _extract_old_coord(self, file_path):
        """查找坐标，最后一个元素是文件类别，电荷和自旋多重度"""
        coordinates = []
        # 遇到恢复词，不写入，直接终止循环
        # 遇到冗余内坐标开始记录
        with open(file_path, mode="r", buffering=-1, encoding="utf-8") as fileObj:
            file_lines = fileObj.readlines()
            start_flag = 0
            count = 0
            for line in file_lines:
                # 防止出现从check文件导入，出现同样关键词干扰，因此大于300
                if count > 300:
                    # 必须要start_flag=1之后，代表写完才可以退出，不然则遍历整个文件结束
                    if self.coordinates_key[1] in line and start_flag == 1:
                        break
                    if start_flag == 1:
                        line = line.strip()
                        coordinates.append(line.replace(",0,", ","))
                    if self.coordinates_key[0] in line:
                        start_flag = 1
                count += 1
        print("文件{}坐标查找完毕\n".format(file_path))
        return coordinates

# ---------对外的接口函数----------
    def get_sp_energy(self, filename):   # Log后面复制的HF能量
        return self._extract_hf_value(filename)

    def get_zpe_energy(self, filename):  # Log后面复制的零点能
        return self._extract_zpe_value(filename)

    def get_freq_energy(self, filename):
        return self._extract_thermal_corrections(filename)

    def get_freqs(self, filename):
        return self._extract_all_frequencies(filename)

    def get_coord(self, filename, combine_symbol="   "):
        return self._extract_last_input_orientation(filename, combine_symbol)

    def get_old_coord(self, filename):
        return self._extract_old_coord(filename)

    def get_others(self, filename):
        return self._extract_rot_mass_dof(filename)

    def get_cbs_energy(self, filename):
        return self._extract_cbs_energy(filename)

    def get_multi_cbs_energy(self, filename):
        return self._extract_multi_cbs_energy(filename)

    def get_g4_energy(self, filename):
        return self._extract_g4_energy(filename)

    def get_w1_energy(self, filename, match_str1, match_str2):
        return self._extract_w1_energy(filename, match_str1, match_str2)

    def get_scan_irc_frames(self, filename):
        return self._extract_irc_scan_frames(filename)

    def get_charge_spin_state(self, filename):
        return self._extract_charge_spin_state(filename)

    def get_out_coord_charge_spin_state(self, filename):
        # 读取文件末尾的坐标和自旋多重度
        xyz_list = self.get_coord(filename)
        charge_spin_state = self.get_charge_spin_state(filename)
        xyz_list.append(charge_spin_state)
        return xyz_list

    def get_input_coord_charge_spin_state(self, filename):
        # 读取文件末尾的坐标和自旋多重度
        return self._extract_input_coord_charge_spin(filename)

    def simple_information(self, filename):
        detail, simple = self._extract_steps_information(filename)
        return simple

    def detail_information(self, filename):
        detail, simple = self._extract_steps_information(filename)
        return detail


# ------------------- 使用示例 -------------------
if __name__ == "__main__":
    A = FindInfo()
    # print(A.get_steps_inform(r'E:\Temp\Quantum_11.09\Demo\full-data-dz\h2o-ts1.log'))
    print(A.get_cbs_energy(r'E:\Python_Files\codehub\Quantum_02.26\Demo\extract-tz-cbs-for-ts\H2O-avtz-cbs.log'))
    # print(A.get_old_coord(r'E:\Learning\Keyin\12KBQC\file\opt\CF3CF2CO_opt.out'))
    # print(A.get_coord(r'E:\Learning\Keyin\12KBQC\file\opt\CF3CF2CO_opt.out'))
    # content = A.get_scan_irc_frames(r'E:\Learning\Keyin\12KBQC\file\IRC\bicbut_IRC.out')
    # print(len(content))

    # content = A.get_scan_frames(r'E:\Learning\Keyin\12KBQC\file\scan\Morse_fit\ethane.out')
    # print(len(content))
    # for item in content:
    #     print(item)
    # print(A.extract_hf_value(r'./Public/ethanol.out'))
    # A = FindInfo(r'./Public/H2O.out')
    # import glob, os
    # directory = r"E:\Research\AlLiClad\RecalGauss\All-data\al4-lioh\extract-tz"
    # log_files = glob.glob(os.path.join(directory, "*.log"))
    # for file in log_files:
    #     print(file)
    #     print(A.get_zpe_energy(file))
    #     print(A.get_sp_energy(file))

    # print(A.extract_thermal_corrections(r'./Public/H2O.out'))
    # print(A.extract_rot_mass_dof(r'./Public/H2O.out'))
    # print(A.get_coord(r'./Public/H2O.out'))
    # write_content = A.get_coord(r'E:\Research\AlLiClad\RecalGauss\All-data\al8-li2o\extract-tz\al8-li2o-ts2-avtz.log', ",")
    # from Files import SaveFile
    # write_file = SaveFile()
    # write_file.save("coord.txt", "\n".join(write_content))
    # print(A.extract_all_frequencies(r'./Public/H2O.out'))
    # print(A.extract_all_frequencies(r'./Public/ethanol_intmodes.out'))
    # print(A.extract_step1_first_block(r'./Public/C2H4F2_TS.out'))
    # gif=A.extract_step1_first_block(r'./Public/C2H4F2_TS.out')
    # import time
    # t0 = time.time()
    # print(t0)
    # with open(r'./Public/H2O.txt', 'w') as f:
    #     f.writelines("\n".join(gif))
    # t1 = time.time()
    # print(t1)
    # print('写入文件耗时:', t1-t0, 's')

    # t0 = time.time()
    # print(t0)
    # with open(r'./Public/H2O.txt', 'w') as f:
    #     for i in range(len(gif)):
    #         f.write(gif[i] + "\n")
    # t1 = time.time()
    # print(t1)
    # print('写入文件耗时:', t1-t0, 's')
