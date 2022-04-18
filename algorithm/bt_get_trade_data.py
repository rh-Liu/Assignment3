import datetime
import os.path
import json
import addpath
import pandas as pd
from jqdatasdk import *
auth('13350103318', '87654321wW')

if __name__ == '__main__':

    with open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'processed_factor_data_json.json'), 'r') as f:
        data = json.load(f)
    for date in data.keys():
        data[date] = pd.DataFrame(data[date])
    factor_data_dict = data
    del data

    dateList = list(factor_data_dict.keys())
    ## 所有可能交易的symbol
    # trade_set = set()
    #
    # for date in dateList:
    #     securities_list = get_index_stocks('000300.XSHG', date)
    #     trade_set = trade_set.union(set(securities_list))
    #
    # trade_list = list(trade_set)
    # pd.DataFrame(trade_list).to_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list.csv'), index=None, columns=None)
    trade_list = list(pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list.csv'), header=0).iloc[:, 0])

    # 获取上述所有的价格数据
    for symbol in trade_list[870:871]:
        df = get_price(symbol, start_date=dateList[0], end_date=dateList[-1], fields=['open', 'close', 'high', 'low', 'volume'])
        df.to_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', symbol+'.csv'))

    print('done')