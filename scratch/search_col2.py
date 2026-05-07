import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
df_cc = excel.parse('College_Course_Cutoffs', header=1)
print(df_cc[df_cc['College ID'].astype(str).str.contains('COL2|COL 2|COL002|GEC', case=False, na=False)])
