import pandas as pd
import os

file_path = r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_Colleges_and_Courses.xlsx'

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(df.head(20).to_string())
