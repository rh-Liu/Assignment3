import os
import pandas as pd
import addpath
import json
from dateutil.relativedelta import relativedelta
from sklearn.ensemble import RandomForestClassifier
from xgboost.sklearn import XGBClassifier

'''
Using the model to select 5 portfolios, without considering the industry.
'''

def port_generate(date, model):
    '''
    date is the trading date, using the last 3 year data (exclude date) to train,
    and predict on date, using the prob as the rule to divide the portfolios
    :return: port_df for the date, containing the prob prediction for each stocks on date
    '''

    print(date)

    train_dates = pd.date_range(start=date - relativedelta(months=12 * 3), end=date, freq='m').strftime('%Y-%m-%d')
    train_dates = list(train_dates)[:-1]
    train_data = pd.DataFrame()
    for t in train_dates:
        train_df = factor_data_dict[t].copy()
        train_df.drop(['close', 'next_close', 'next_return'], axis=1, inplace=True)
        train_data = train_data.append(train_df.loc[train_df['label'].dropna().index, :])
    if m == 'xgb':
        train_data.loc[train_data['label']==-1] = 0
    model.fit(train_data.iloc[:, :-1], train_data.iloc[:, -1])
    fac_date = factor_data_dict[date.strftime('%Y-%m-%d')].iloc[:, :-4]
    prob_df = pd.DataFrame(model.predict_proba(fac_date), columns=['-1', '1'], index=fac_date.index)
    return prob_df



if __name__ == '__main__':
    with open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'labeled_processed_factor_data_json.json'), 'r') as f:
        data = json.load(f)
    for date in data.keys():
        data[date] = pd.DataFrame(data[date]).drop(['DP'], axis=1)
    factor_data_dict = data
    del data

    bt_start = '2011-12-31'
    bt_end = '2021-11-30'
    bt_period = pd.date_range(start=bt_start, end=bt_end, freq='m')
    # all_period = pd.date_range(start=list(factor_data_dict.keys())[0], end=list(factor_data_dict.keys())[-1], freq='m')
    port_1 = {}
    port_2 = {}
    port_3 = {}
    port_4 = {}
    port_5 = {}

    ind_port_1 = {}
    ind_port_2 = {}
    ind_port_3 = {}
    ind_port_4 = {}
    ind_port_5 = {}

    ind_info = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'investment_univ', 'cn_symbol_list_with_ind.csv'), index_col=0)

    for m in ['rf', 'xgb']:

        for date in bt_period:
            if m == 'rf':
                model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=0)
            elif m == 'xgb':
                model = XGBClassifier(max_depth=8, subsample=1, random_state=0, use_label_encoder=False)
            prob_df = port_generate(date, model)
            date = date.strftime('%Y-%m-%d')

            # divide without considering industry
            port_1[date] = prob_df[prob_df['1'] >= prob_df['1'].quantile(0.8)].index.tolist()
            port_2[date] = [s for s in prob_df[prob_df['1'] >= prob_df['1'].quantile(0.6)].index.tolist() if s not in port_1[date]]
            port_5[date] = prob_df[prob_df['1'] < prob_df['1'].quantile(0.2)].index.tolist()
            port_4[date] = [s for s in prob_df[prob_df['1'] < prob_df['1'].quantile(0.4)].index.tolist() if s not in port_5[date]]
            port_3[date] = [s for s in prob_df.index.tolist() if s not in (port_1[date] + port_2[date] + port_4[date] + port_5[date])]

            # divide considering industry
            ind_port_1[date] = []
            ind_port_2[date] = []
            ind_port_3[date] = []
            ind_port_4[date] = []
            ind_port_5[date] = []
            prob_df['industry'] = ind_info['industry']
            ind_list = list(set(prob_df['industry'].dropna()))
            for ind in ind_list:
                ind_prob_df = prob_df[prob_df['industry']==ind]
                ind_port_1[date] += ind_prob_df[ind_prob_df['1'] >= ind_prob_df['1'].quantile(0.8)].index.tolist()
                ind_port_2[date] += [s for s in ind_prob_df[ind_prob_df['1'] >= ind_prob_df['1'].quantile(0.6)].index.tolist() if s not in ind_port_1[date]]
                ind_port_5[date] += ind_prob_df[ind_prob_df['1'] < ind_prob_df['1'].quantile(0.2)].index.tolist()
                ind_port_4[date] += [s for s in ind_prob_df[ind_prob_df['1'] < ind_prob_df['1'].quantile(0.4)].index.tolist() if s not in ind_port_5[date]]
                ind_port_3[date] += [s for s in ind_prob_df.index.tolist() if s not in (ind_port_1[date] + ind_port_2[date] + ind_port_4[date] + ind_port_5[date])]


        for i in range(1, 6):
            jsonObj = None
            json_path = None
            exec('jsonObj = json.dumps(port_%s)' % i)
            if m == 'rf':
                exec("json_path = os.path.join(addpath.data_path, 'strategy_temps', 'rf_port_%s.json')" % i)
            elif m == 'xgb':
                exec("json_path = os.path.join(addpath.data_path, 'strategy_temps', 'xgb_port_%s.json')" % i)
            fileObj = open(json_path, 'w', encoding='utf-8')
            fileObj.write(jsonObj)
            fileObj.close()

        for i in range(1, 6):
            exec('jsonObj = json.dumps(ind_port_%s)' % i)
            if m == 'rf':
                exec("json_path = os.path.join(addpath.data_path, 'strategy_temps', 'rf_ind_port_%s.json')" % i)
            elif m == 'xgb':
                exec("json_path = os.path.join(addpath.data_path, 'strategy_temps', 'xgb_ind_port_%s.json')" % i)
            fileObj = open(json_path, 'w', encoding='utf-8')
            fileObj.write(jsonObj)
            fileObj.close()

        print('done')