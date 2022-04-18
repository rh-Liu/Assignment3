import numpy as np
import pandas as pd
import json
import os
from multiprocessing import Pool
import addpath
from jqdatasdk import *
import datetime
import statsmodels.api as sm
from statsmodels import regression
from jqdatasdk.technical_analysis import *
auth('13350103318', '87654321wW')

# ----------------------------------------------------------------------------------------
# 获取指定周期的日期列表 'W、M、Q'
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
# get_period_data('M', '2019-12-31', '2020-07-31')

# 去除上市距beginDate不到3个月的stocks
def delect_stop(stocks, beginDate, n=30*3):
    stockList = []
    beginDate = datetime.datetime.strptime(beginDate, '%Y-%m-%d')
    for stock in stocks:
        start_date = get_security_info(stock).start_date
        if start_date < (beginDate - datetime.timedelta(days=n)).date():
            stockList.append(stock)
    return stockList
# 获得股票池
# def get_stock(stockPool, begin_date):
#     if stockPool == 'HS300':
#         stockList = get_index_stocks('000300.XSHG', begin_date)
#     elif stockPool == 'ZZ500':
#         stockList = get_index_stocks('399905.XSHE', begin_date)
#     elif stockPool == 'ZZ800':
#         stockList = get_index_stocks('399906.XSHE', begin_date)
#     elif stockPool == 'CYBZ':
#         stockList = get_index_stocks('399006.XSHE', begin_date)
#     elif stockPool == 'ZXBZ':
#         stockList = get_index_stocks('399005.XSHE', begin_date)
#     elif stockPool == 'A':
#         stockList = get_index_stocks('000002.XSHG', begin_date) + get_index_stocks('399107.XSHE', begin_date)
#         # 剔除ST股
#     st_data = get_extras('is_st', stockList, count=1, end_date=begin_date)
#     stockList = [stock for stock in stockList if not st_data[stock][0]]
#     # 剔除停牌、新股及退市股票
#     stockList = delect_stop(stockList, begin_date)
#     return stockList
# # get_stock('HS300', '2017-01-31')
# # ----------------------------------------------------------------------------------------
#
# # 辅助线性回归的函数
# def linreg(X, Y, columns=3):
#     X = sm.add_constant(np.array(X))
#     Y = np.array(Y)
#     if len(Y) > 1:
#         # results = regression.linear_model.OLS(Y, X).fit()
#         results = sm.OLS(Y, X).fit()
#         # print('debug')
#         return results.params
#     else:
#         return [float('nan')]*(columns+1)
# # linreg([1,2,3], [2,4,7])
#
# # 或取行业的股票
# # def get_industry_name(i_Constituent_Stocks, value):
# #     return [k for k, v in i_Constituent_Stocks.items() if value in v]
# # # 缺失值处理
# # def replace_nan_indu(factor_data, stockList, industry_code, date):
# #     # 把nan用行业平均值代替，依然会有nan，此时用所有股票平均值代替
# #     i_Constituent_Stock = {}
# #     data_temp = pd.DataFrame(index=industry_code, columns=factor_data.columns)
# #     for i in industry_code:
# #         temp = get_index_stocks(i, date)
# #         i_Constituent_Stock[i] = list(set(temp).interesection(set(stockList)))
# #         data_temp.loc[i] = np.mean(factor_data.loc[i_Constituent_Stock[i], :])
# #     for factor in data_temp.columns:
# #         # 行业缺失值用所有行业平均值代替
# #         null_industry = list(data_temp.loc[pd.isnull(data_temp[factor]), factor].keys())
# #         for i in null_industry:
# #             data_temp.loc[i, factor] = np.mean(data_temp[factor])
#         null_stock = list(factor_data.loc[pd.isnull(factor_data[factor]), factor].keys())
#         for i in null_stock:
#             industry = get_industry_name(i_Constituent_Stock, i)
#             if industry:
#                 factor_data.loc[i, factor] = data_temp.loc[industry[0], factor]
#             else:
#                 factor_data.loc[i, factor] = np.mean(factor_data[factor])
#     return factor_data
# # def get_factor_data(stock, date):
# #     # data = pd.DataFrame(index=stock)
# #     q = query(valuation, balance, cash_flow, income, indicator).filter(valuation.code.in_(stock))
# #     df = get_fundamentals(q, date)
# #     df['market_cap'] = df['market_cap']*100000000
# # # get_factor_data('600519.XSHG', '2020-01-31')
# # q = query(valuation).filter(valuation.code == '600519.XSHG')
# # df = get_fundamentals(q, '2020-12-31')
def delect_st(stocks, beginDate):
    st_data = get_extras('is_st', stocks, count=1, end_date=beginDate)
    stockList = [stock for stock in stocks if st_data[stock][0] == False]
    return stockList

# start_date = '2006-01-01'
start_date = '2006-01-01'
end_date = '2021-12-31'
period = 'M'
# securities_list = delect_stop(get_index_stocks('000300.XSHG'), start_date, 90)
# securities_list = delect_st(securities_list, start_date)
jqfactor_list = ['current_ratio',
                  'net_profit_to_total_operate_revenue_ttm',
                  'gross_income_ratio',
                  'roe_ttm',
                  'roa_ttm',
                  'total_asset_turnover_rate',\
                  'net_operating_cash_flow_coverage',
                  'net_operate_cash_flow_ttm',
                  'net_profit_ttm',\
                  'cash_to_current_liability',
                  'operating_revenue_growth_rate',
                  'non_recurring_gain_loss',\
                  'operating_revenue_ttm',
                  'net_profit_growth_rate']
def get_jq_factor(securities_list, date):
    # securities_list = delect_stop(get_index_stocks('000300.XSHG'), start_date, 90)
    # securities_list = delect_st(securities_list, start_date)
    factor_data = get_factor_values(securities=securities_list,
                                    factors=jqfactor_list,
                                    count=1,
                                    end_date=date)
    jq_factor_df = pd.DataFrame(index=securities_list)
    for i in factor_data.keys():
        jq_factor_df[i] = factor_data[i].iloc[0,:]
    return jq_factor_df
# get_jq_factor('2020-01-01')

# q = query(valuation.code,
#       valuation.market_cap,#市值
#       valuation.circulating_market_cap,
#       valuation.pe_ratio, #市盈率（TTM）
#       valuation.pb_ratio, #市净率（TTM）
#
#       valuation.pcf_ratio, #CFP
#       valuation.ps_ratio, #PS
#       balance.total_assets,
#       balance.total_liability,
#       balance.development_expenditure, #RD
#       balance.dividend_payable,
#       balance.fixed_assets,
#       balance.total_non_current_liability,
#       income.operating_profit,
#       income.total_profit, #OPTP
#       #
#       indicator.net_profit_to_total_revenue, #净利润/营业总收入
#       indicator.inc_revenue_year_on_year,  #营业收入增长率（同比）
#       indicator.inc_net_profit_year_on_year,#净利润增长率（同比）
#       indicator.roe,
#       indicator.roa,
#       indicator.gross_profit_margin #销售毛利率GPM
#     ).filter(
#       valuation.code.in_(securities_list)
#     )
def get_q(securities_list):
    q = query(valuation.code,
          valuation.market_cap,#市值
          valuation.circulating_market_cap,
          valuation.pe_ratio, #市盈率（TTM）
          valuation.pb_ratio, #市净率（TTM）

          valuation.pcf_ratio, #CFP
          valuation.ps_ratio, #PS
          balance.total_assets,
          balance.total_liability,
          balance.development_expenditure, #RD
          balance.dividend_payable,
          balance.fixed_assets,
          balance.total_non_current_liability,
          income.operating_profit,
          income.total_profit, #OPTP
          #
          indicator.net_profit_to_total_revenue, #净利润/营业总收入
          indicator.inc_revenue_year_on_year,  #营业收入增长率（同比）
          indicator.inc_net_profit_year_on_year,#净利润增长率（同比）
          indicator.roe,
          indicator.roa,
          indicator.gross_profit_margin #销售毛利率GPM
        ).filter(
          valuation.code.in_(securities_list)
        )
    return q

def initialize_df(df, securities_list, date):
    # securities_list = delect_stop(get_index_stocks('000300.XSHG'), start_date, 90)
    # securities_list = delect_st(securities_list, start_date)

    # 净资产
    df['net_assets'] = df['total_assets'] - df['total_liability']

    df_new = pd.DataFrame(index=securities_list)

    # 估值因子
    df_new['EP'] = df['pe_ratio'].apply(lambda x: 1 / x)
    df_new['BP'] = df['pb_ratio'].apply(lambda x: 1 / x)
    df_new['SP'] = df['ps_ratio'].apply(lambda x: 1 / x)
    df_new['DP'] = df['dividend_payable'] / (df['market_cap'] * 100000000)
    df_new['RD'] = df['development_expenditure'] / (df['market_cap'] * 100000000)
    df_new['CFP'] = df['pcf_ratio'].apply(lambda x: 1 / x)

    # 杠杆因子
    # 对数流通市值
    df_new['CMV'] = np.log(df['circulating_market_cap'])
    # 总资产/净资产
    df_new['financial_leverage'] = df['total_assets'] / df['net_assets']
    # 非流动负债/净资产
    df_new['debtequityratio'] = df['total_non_current_liability'] / df['net_assets']
    # 现金比率=(货币资金+有价证券)÷流动负债
    df_new['cashratio'] = df['cash_to_current_liability']
    # 流动比率=流动资产/流动负债*100%
    df_new['currentratio'] = df['current_ratio']

    # 财务质量因子
    # 净利润与营业总收入之比
    df_new['NI'] = df['net_profit_to_total_operate_revenue_ttm']
    df_new['GPM'] = df['gross_income_ratio']
    df_new['ROE'] = df['roe_ttm']
    df_new['ROA'] = df['roa_ttm']
    df_new['asset_turnover'] = df['total_asset_turnover_rate']
    df_new['net_operating_cash_flow'] = df['net_operating_cash_flow_coverage']

    # 成长因子
    df_new['Sales_G_q'] = df['operating_revenue_growth_rate']
    df_new['Profit_G_q'] = df['net_profit_growth_rate']

    # 技术指标
    df_new['RSI'] = pd.Series(RSI(securities_list, date, N1=20))
    dif, dea, macd = MACD(securities_list, date, SHORT=10, LONG=30, MID=15)
    df_new['DIF'] = pd.Series(dif)
    df_new['DEA'] = pd.Series(dea)
    df_new['MACD'] = pd.Series(macd)

    return df_new

# ----------------------------------------------------------------------------------------
dateList = get_period_date(period, start_date, end_date)

# (jqdata)因子
df_jq_factor = {}
# （财务数据）因子
df_q_factor = {}
# 预处理前的原始因子训练集
df_factor_pre_train = {}

for date in dateList:
    print(date)
    securities_list = delect_stop(get_index_stocks('000300.XSHG', date), date, 90)
    securities_list = delect_st(securities_list, date)
    q = get_q(securities_list)
    df_jq_factor = get_jq_factor(securities_list, date)
    df_q_factor = get_fundamentals(q, date=date)
    df_q_factor.index = df_q_factor['code']
    # 合并
    df_factor_pre_train[date] = pd.concat([df_q_factor, df_jq_factor], axis=1)
    # 初始化
    df_factor_pre_train[date] = initialize_df(df_factor_pre_train[date],
                                              securities_list, date).to_dict()

jsonObj = json.dumps(df_factor_pre_train)
fileObj = open(os.path.join(addpath.data_path, 'cn_data', 'factors', 'factor_data_json_new.json'), 'w', encoding='utf-8')
fileObj.write(jsonObj)
fileObj.close()
print('done')