import pandas as pd
import os
import addpath
from jqdatasdk import *
auth('13350103318', '87654321wW')

symbol_list = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list.csv'), index_col=0)

for symbol in symbol_list.index.tolist():
    try:
        symbol_list.loc[symbol, 'industry'] = get_industry(symbol)[symbol]['jq_l1']['industry_code']
    except:
        print(symbol)
        symbol_list.drop(symbol, axis=0, inplace=True)

symbol_list.to_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list_with_ind.csv'))