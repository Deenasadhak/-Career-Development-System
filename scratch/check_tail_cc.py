import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
df_raw = excel.parse('College_Course_Cutoffs', header=None)
print(f"Shape of raw sheet: {df_raw.shape}")
print(df_raw.tail(20))
