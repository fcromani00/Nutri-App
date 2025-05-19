import pandas as pd

TACO = pd.read_excel('Nutri-app.xlsx', sheet_name='TACO')
AGtaco = pd.read_excel('Nutri-app.xlsx', sheet_name='AGtaco3')
AAtaco = pd.read_excel('Nutri-app.xlsx', sheet_name='AminoácidosTACO3')

df_merged_1 = pd.merge(TACO, AGtaco, on='id_alimento', how='left')

df_final = pd.merge(df_merged_1, AAtaco, on='id_alimento', how='left')

df_final.to_excel('TACO.xlsx')
print(AAtaco)