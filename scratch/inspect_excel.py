import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
print(f"Sheets: {excel.sheet_names}")
for sheet in excel.sheet_names:
    df = excel.parse(sheet)
    print(f"Sheet '{sheet}' columns: {list(df.columns)}")
    print(f"Rows: {len(df)}")
