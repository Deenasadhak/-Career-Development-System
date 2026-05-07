import pandas as pd
import os

file_path = r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_Colleges_and_Courses.xlsx'

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nShape:", df.shape)
    except Exception as e:
        print("Error reading excel:", e)
else:
    print("File not found")
