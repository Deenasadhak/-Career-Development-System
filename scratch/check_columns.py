import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
for sheet in excel.sheet_names:
    print(f"Sheet: {sheet}")
    df = excel.parse(sheet, header=1)
    print(df.columns.tolist())
    print("-" * 20)
