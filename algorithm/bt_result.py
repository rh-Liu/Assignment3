import pandas as pd
import matplotlib.pyplot as plt
import os
import addpath
import pandas as pd
import pMatrix
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 4000)

if __name__ == '__main__':

    index = pd.read_excel(os.path.join(addpath.data_path, 'cn_data', 'reference', 'HS300.xlsx'), parse_dates=True, index_col=1)

    port_list1 = ['rf_ind_port_1', 'rf_ind_port_2', 'rf_ind_port_3', 'rf_ind_port_4', 'rf_ind_port_5']
    port_list2 = ['rf_port_1', 'rf_port_2', 'rf_port_3', 'rf_port_4', 'rf_port_5']
    port_list3 = ['xgb_ind_port_1', 'xgb_ind_port_2', 'xgb_ind_port_3', 'xgb_ind_port_4', 'xgb_ind_port_5']
    port_list4 = ['xgb_port_1', 'xgb_port_2', 'xgb_port_3', 'xgb_port_4', 'xgb_port_5']
    port_list = [port_list1, port_list2, port_list3, port_list4]

    res_df = pd.DataFrame()
    fig = plt.figure(tight_layout=True)

    for port in port_list:
        hs = pd.DataFrame()
        for p in port:
            pv = pd.read_csv(os.path.join(addpath.data_path, 'strategy_temps', 'pv_'+p+'.csv'),
                             parse_dates=True, index_col=0).dropna()
            pv = pv / pv.iloc[0, 0]
            pv.rename(columns={pv.columns[0]: p}, inplace=True)
            plt.plot(pv, label=p)

            if hs.empty:
                hs = index[pv.index[0]: pv.index[-1]][['close']].rename(columns={'close': 'HS300'})
                hs = hs / hs.iloc[0, 0]

            res_df = res_df.append(pMatrix.p_matrix(pv, freq='D', start=pv.index[0].strftime('%Y-%m-%d'),
                                           end=pv.index[-1].strftime('%Y-%m-%d'), exchange='CN'))
        res_df = res_df.append(pMatrix.p_matrix(hs, freq='D', start=pv.index[0].strftime('%Y-%m-%d'),
                                           end=pv.index[-1].strftime('%Y-%m-%d'), exchange='CN'))
        plt.plot(hs, label='HS300')
        plt.title(port[0][:-2])
        plt.legend()
        plt.show()

    print(res_df)
    print('done')