import os
import numpy as np
import pandas as pd
import addpath
import json
import datetime
from jqdatasdk import *
import statsmodels.api as sm
# from get_factors import *

auth('13350103318', '87654321wW')

pd.set_option('display.max_columns', None) #显示所有行
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 4000) #页面宽度

with open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'factor_data_json_new.json'), 'r') as f:
    data = json.load(f)
for date in data.keys():
    data[date] = pd.DataFrame(data[date])
factor_data_dict = data
del data
print('json read done')

start_date = '2006-01-01'
end_date = '2021-12-31'
period = 'M'

# ----------------------------------------------------------------------------------------
def get_period_date(peroid,start_date, end_date):
    #设定转换周期period_type  转换为周是'W',月'M',季度线'Q',五分钟'5min',12天'12D'
    stock_data = get_price('000001.XSHE',start_date,end_date,'daily',fields=['close'])
    #记录每个周期中最后一个交易日
    stock_data['date']=stock_data.index
    #进行转换，周线的每个变量都等于那一周中最后一个交易日的变量值
    period_stock_data=stock_data.resample(peroid).last()
    date = period_stock_data.index
    pydate_array = date.to_pydatetime()
    date_only_array = np.vectorize(lambda s: s.strftime('%Y-%m-%d'))(pydate_array )
    date_only_series = pd.Series(date_only_array)
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    start_date = start_date-datetime.timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%d")
    date_list = date_only_series.values.tolist()
    date_list.insert(0,start_date)
    return date_list

# 去除上市距beginDate不到3个月的stocks
def delect_stop(stocks, beginDate, n=30*3):
    stockList = []
    beginDate = datetime.datetime.strptime(beginDate, '%Y-%m-%d')
    for stock in stocks:
        start_date = get_security_info(stock).start_date
        if start_date < (beginDate - datetime.timedelta(days=n)).date():
            stockList.append(stock)
    return stockList

def delect_st(stocks, beginDate):
    st_data = get_extras('is_st', stocks, count=1, end_date=beginDate)
    stockList = [stock for stock in stocks if st_data[stock][0] == False]
    return stockList

# l = get_index_stocks('000300.XSHG', '2021-12-31')
# l1 = delect_stop(l, start_date, 90)
# print(len(l1))
# l2 = delect_st(l1, start_date)
# print(len(l2))

def winorize_med(factor_data, scale, axis=0):
    '''
    中位数去极值：设第 T 期某因子在所有个股上的暴露度序列为𝐷𝑖，𝐷𝑀为该序列
    中位数，𝐷𝑀1为序列|𝐷𝑖 − 𝐷𝑀|的中位数，则将序列𝐷𝑖中所有大于𝐷𝑀 + 5𝐷𝑀1的数
    重设为𝐷𝑀 +5𝐷𝑀1，将序列𝐷𝑖中所有小于𝐷𝑀 − 5𝐷𝑀1的数重设为𝐷𝑀 −5𝐷𝑀1；
    :param factor_data: 因子df，columns为因子，raw为symbol
    :param scale: 几倍标准差
    :param axis: 默认columns为因子，raw为symbol
    :return: 去极值后的factor df
    '''
    def func(col):
        med = col.median()
        med1 = abs(col - med).median()
        col[col > med + scale*med1] = med + scale*med1
        col[col < med - scale*med1] = med - scale*med1
        return col
    win_factor_data = factor_data.apply(func, axis=axis)
    # print('winorization done')
    return win_factor_data

def get_industry_name(i_Constituent_Stocks, value):
    return [k for k, v in i_Constituent_Stocks.items() if value in v]

def replace_nan_indu(factor_data,stockList,industry_code,date):
    '''
    缺失值处理：得到新的因子暴露度序列后，将因子暴露度缺失的地方设为中信一
    级行业相同个股的平均值。
    依赖聚宽get_industry_stocks，一级行业选的聚宽一级
    :param factor_data: 因子df，columns为因子，raw为symbol
    :param stockList: 代码list
    :param industry_code: 聚宽的industry list
    :param date: 日期
    :return: 缺失值处理后的factor df
    '''
    #把nan用行业平均值代替，依然会有nan，此时用所有股票平均值代替
    i_Constituent_Stocks = {}
    data_temp = pd.DataFrame(index=industry_code, columns=factor_data.columns)

    for i in industry_code:
        temp = get_industry_stocks(i, date)
        # i_Constituent_Stocks[i] = list(set(temp).intersection(set(stockList)))
        i_Constituent_Stocks[i] = list(set(temp).intersection(set(factor_data.index)))
        data_temp.loc[i] = np.mean(factor_data.loc[i_Constituent_Stocks[i], :])
    for factor in data_temp.columns:
        # 行业缺失值用所有行业平均值代替
        null_industry = list(data_temp.loc[pd.isnull(data_temp[factor]), factor].keys())
        for i in null_industry:
            data_temp.loc[i, factor] = np.mean(data_temp[factor])
        null_stock = list(factor_data.loc[pd.isnull(factor_data[factor]), factor].keys())
        for i in null_stock:
            industry = get_industry_name(i_Constituent_Stocks, i)
            if industry:
                factor_data.loc[i, factor] = data_temp.loc[industry[0], factor]
            else:
                factor_data.loc[i, factor] = np.mean(factor_data[factor])
    # print('replacing nan done')
    return factor_data

def neutralize(factor_data, stockList, industry_code, date):
    '''
    市值行业中性化，对某一时间截面的因子对市值及行业哑变量线性回归，取残差作为新的因子值
    依赖聚宽get_industry_stocks，后续可寻找其他好分行业的资源
    :param factor_data: 某一时间界面的因子数据
    :param stockList: 交易标的
    :param industry_code: 用哪些行业划分
    :param date: 当前时间点
    :return: 中性化处理后的因子数据
    '''
    i_Constituent_Stocks = {}
    data_temp = pd.DataFrame(index=industry_code, columns=factor_data.columns)
    # d = pd.get_dummies(industry_code)
    q = query(valuation.code, valuation.market_cap).filter(valuation.code.in_(stockList))
    market_cap = get_fundamentals(q, date=date)
    market_cap.set_index(market_cap['code'], inplace=True)
    del market_cap['code']
    for i in industry_code:
        temp_stock_list = get_industry_stocks(i, date)
        if len(temp_stock_list) == 0:
            temp_stock_list = get_industry_stocks(i)
        i_Constituent_Stocks[i] = list(set(temp_stock_list).intersection(set(stockList)))
        market_cap.loc[i_Constituent_Stocks[i], i] = 1
    market_cap.fillna(0, inplace=True)
    df = pd.merge(market_cap, factor_data, left_index=True, right_index=True, how='inner')
    factor_list = list(set(df.columns).intersection(set(factor_data.columns)))
    newx = pd.DataFrame(index=df.index)
    for factor in factor_list:
        x = df.iloc[:, 0:10]
        y = df.loc[:, factor]
        model = sm.OLS(y,x).fit()
        newx[factor] = model.resid
    # print('neutralization done')
    return newx

def standardlize(factor_data):
    '''
    标准化，原数据减去均值除以标准差，得到近似正态序列
    :param factor_data: 因子数据
    :return: 处理后序列
    '''
    factor_data = (factor_data-factor_data.mean())/factor_data.std()
    # print('standardlization done')
    return factor_data

def factor_preprocessing(factor_data, stockList, industrt_code, date):
    print(date)
    factor_data = winorize_med(factor_data, scale=5, axis=0)
    factor_data = replace_nan_indu(factor_data, stockList, industrt_code, date)
    factor_data = neutralize(factor_data, stockList, industry_code, date)
    factor_data = standardlize(factor_data)
    return factor_data
# ----------------------------------------------------------------------------------------

dateList = get_period_date('M', start_date, end_date)
# securities_list = delect_stop(get_index_stocks('000300.XSHG'), start_date, 90)
# securities_list = delect_st(securities_list, start_date)
# 聚宽一级行业
industry_code = ['HY001', 'HY002', 'HY003', 'HY004', 'HY005', 'HY006', 'HY007', 'HY008', 'HY009', 'HY010', 'HY011']

ts = datetime.datetime.now()
for date in dateList:
    securities_list = delect_stop(get_index_stocks('000300.XSHG', date), date, 90)
    securities_list = delect_st(securities_list, date)
    factor_data_dict[date] = factor_preprocessing(factor_data_dict[date], securities_list, industry_code, date).to_dict()

del_date = list(set(factor_data_dict.keys()) - set(dateList))
for date in del_date:
    del factor_data_dict[date]
te = datetime.datetime.now()
print('preprocessing time: ', te - ts)

jsonObj = json.dumps(factor_data_dict)
fileObj = open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'processed_factor_data_json.json'), 'w', encoding='utf-8')
fileObj.write(jsonObj)
fileObj.close()

print('done')

# date = '2010-07-31'
# dat = factor_data_dict[date]
#
# dat = winorize_med(dat, scale=5, axis=0)
# dat = replace_nan_indu(dat, securities_list, industry_code=industry_code, date=date)
# dat = neutralize(dat, stockList=securities_list, industry_code=industry_code, date=date, axis=0)
# dat = standardlize(dat, axis=0)