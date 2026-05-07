import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)

for sheet in excel.sheet_names:
    df = excel.parse(sheet, header=None)
    mask = df.apply(lambda row: row.astype(str).str.contains('Thrissur', case=False).any(), axis=1)
    if mask.any():
        print(f"--- Sheet: {sheet} ---")
        print(df[mask])
