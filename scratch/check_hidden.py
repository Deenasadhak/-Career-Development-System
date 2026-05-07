import openpyxl
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
wb = openpyxl.load_workbook(file_path)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f"Sheet: {sheet}, State: {ws.sheet_state}")
