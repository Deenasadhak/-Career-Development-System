import pandas as pd
import os

file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'

def get_df(sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # Detect header row (first row with non-NaN college name or ID)
    for i, row in df.iterrows():
        if not pd.isna(row.iloc[0]):
            df.columns = df.iloc[i]
            df = df.iloc[i+1:].reset_index(drop=True)
            break
    return df

print('--- Mappings Sheet ---')
df_mappings = get_df('College-Course mappings')
print(df_mappings.head(20))

print('\n--- Search for GEC Thrissur in Mappings ---')
# The college name in mappings might be slightly different or use ID
# Let's see the columns
print(f'Columns: {df_mappings.columns.tolist()}')

# GEC Thrissur ID is likely 'COL001' or similar. 
# Let's check College list first to get ID
df_colleges = get_df('Colleges')
gec_id = df_colleges[df_colleges['College Name'].str.contains('Thrissur', na=False)]['College ID'].values
print(f'GEC Thrissur IDs: {gec_id}')

for gid in gec_id:
    m = df_mappings[df_mappings['College ID'] == gid]
    print(f'Mappings for {gid}: {len(m)}')
    print(m)
