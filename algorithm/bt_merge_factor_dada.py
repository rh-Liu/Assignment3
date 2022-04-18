import datetime
import os.path
import json
import addpath
import pandas as pd

if __name__ == '__main__':

    with open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'processed_factor_data_json.json'), 'r') as f:
        data = json.load(f)
    for date in data.keys():
        data[date] = pd.DataFrame(data[date])
    factor_data_dict = data
    del data

    dateList = list(factor_data_dict.keys())

    trade_list = list(pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list.csv'), header=0).iloc[:, 0])
    factor_list = factor_data_dict[dateList[-1]].columns.to_list()
    for symbol in trade_list:
        df = pd.DataFrame()
        for date in dateList:
            dat = factor_data_dict[date]
            if symbol in dat.index:
                for factor in factor_list:
                    df.loc[date, factor] = dat.loc[symbol, factor]
        if df.empty is False:
            df.to_csv(os.path.join(addpath.data_path, 'cn_data', 'CS_factors', symbol+'.csv'))

    # merge factor and trading data
    # for symbol in trade_list:
    #     df = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', symbol+'.csv'), index_col=0, parse_dates=True)

    print('done')