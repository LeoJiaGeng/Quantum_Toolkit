from GetGaussData import FindInfo

import glob
import os

g16_obj = FindInfo()
directory = r"C:\Users\熊孩子\Desktop\EPPS"
log_files = glob.glob(os.path.join(directory, "*.log"))
for filename in log_files:
    print(filename)
    xyz = g16_obj.get_coord(filename)
    length = len(xyz)
    title = os.path.splitext(os.path.basename(filename))[0]
    with open(filename.replace(".log", ".xyz"), "w") as f:
        f.write(f"{length}\n{title}\n")
        for atom in xyz:
            f.write(f"{atom}\n")
