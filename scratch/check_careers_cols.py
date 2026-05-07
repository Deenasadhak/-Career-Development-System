import pandas as pd
file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
excel = pd.ExcelFile(file_path)

def get_df(sheet_name):
    df_full = excel.parse(sheet_name, header=None)
    header_idx = 0
    for i, row in df_full.iterrows():
        row_vals = [str(x).strip() for x in row.values if pd.notnull(x)]
        if len(row_vals) >= 3 and any(k in " ".join(row_vals) for k in ['ID', 'Name', 'District', 'Course', 'College']):
            header_idx = i
            break
    df = excel.parse(sheet_name, header=header_idx)
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_careers = get_df('Career_Paths')
print(df_careers.columns.tolist())
print(df_careers.head())
