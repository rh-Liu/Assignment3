import os
import numpy as np
import pandas as pd
import addpath
import json
import datetime
from dateutil.relativedelta import relativedelta
import multiprocessing

def process_date(date, factor_data_dict):
    print(date)
    next_date = datetime.datetime.strptime(date, '%Y-%m-%d') \
                + datetime.timedelta(days=1) + relativedelta(months=1) - datetime.timedelta(days=1)
    next_date = next_date.strftime('%Y-%m-%d')

    df = factor_data_dict[date]
    df['close'] = None
    df['next_close'] = None
    df['next_return'] = None

    s_l = df.index.tolist()
    for s in s_l:
        try:
            trading = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', s + '.csv'),
                                  parse_dates=True, index_col=0).resample('m').last()
            df.loc[s, 'close'] = trading.loc[date, 'close']
            df.loc[s, 'next_close'] = trading.loc[next_date, 'close']
            df.loc[s, 'next_return'] = trading.loc[next_date, 'close'] \
                                                           / trading.loc[date, 'close'] - 1
        except:
            print(date, s)
            continue

    df['label'] = None
    if df['next_return'].isna().all() == False:
        df.loc[
            df['next_return'] > df['next_return'].quantile(0.7), 'label'] = 1
        df.loc[
            df['next_return'] < df['next_return'].quantile(0.3), 'label'] = -1
    return df

if __name__ == '__main__':
    with open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'processed_factor_data_json.json'), 'r') as f:
        data = json.load(f)
    for date in data.keys():
        data[date] = pd.DataFrame(data[date])
    factor_data_dict = data
    del data

    pool = multiprocessing.Pool(9)


    date_list = list(factor_data_dict.keys())[1:-1]
    res_list = []
    for date in date_list:
        # df = process_date(date, factor_data_dict)
        res = pool.apply_async(process_date, args=(date, factor_data_dict,))
        res_list.append(res)
    pool.close()
    pool.join()
    print('Sub-process done')

    labeled_factor_data_dict = {}
    for i, date in enumerate(date_list):
        labeled_factor_data_dict[date] = res_list[i].get().to_dict()

    jsonObj = json.dumps(labeled_factor_data_dict)
    fileObj = open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'labeled_processed_factor_data_json.json'),
                   'w', encoding='utf-8')
    fileObj.write(jsonObj)
    fileObj.close()