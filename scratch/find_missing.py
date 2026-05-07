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
df_colleges = get_df('Colleges')

cc_ids = set(df_cc['College ID'].unique())
coll_ids = set(df_colleges['College ID'].unique())

missing_in_cc = coll_ids - cc_ids
print(f"Colleges missing mappings: {len(missing_in_cc)}")
for cid in sorted(list(missing_in_cc)):
    name = df_colleges[df_colleges['College ID'] == cid]['College Name'].values[0]
    print(f"  {cid}: {name}")
