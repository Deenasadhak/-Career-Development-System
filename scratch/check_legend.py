import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\Vite_Practice\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
# Wait, I should use the correct path
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)
df = excel.parse('Ranking_Legend', header=None)
print(df)
