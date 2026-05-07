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

df_cc = get_df('College_Course_Cutoffs')
print(f"Total mappings in Excel: {len(df_cc)}")
print(f"Unique College IDs in mappings: {df_cc['College ID'].unique().tolist()}")

gec_mappings = df_cc[df_cc['College ID'] == 'COL002']
print(f"Mappings for COL002 (GEC Thrissur): {len(gec_mappings)}")
if len(gec_mappings) > 0:
    print(gec_mappings)
else:
    # Maybe it's missing in the sheet?
    # Let's search for the name instead of ID if it exists there
    print("Searching for 'GEC' or 'Thrissur' in College ID or other columns...")
    mask = df_cc.apply(lambda row: row.astype(str).str.contains('COL002|GEC|Thrissur').any(), axis=1)
    print(df_cc[mask])
