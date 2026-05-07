import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
df = excel.parse('College_Course_Cutoffs', header=None)
for i, row in df.head(3).iterrows():
    print(f"Row {i}: {[str(x) for x in row.values]}")
