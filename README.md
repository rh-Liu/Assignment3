# Assignment3
刘瑞涵 221040051
# 代码简介：

由于数据获取源为聚宽，非会员有流量限制，因此很多步骤选择分开处理，略显繁杂。

get_factors.py: 从聚宽获得因子数据，并写入本地。

data_preprocess.py: 通过自建函数对因子数据进行去极值、行业市值中性化、标准化，因子数据写入到本地。（运行时间较长）

bt_get_trade_data.py: 得到trading data，没聚宽会员需要运行多次，储存至本地

bt_merge_factor_data.py: 处理因子数据，整合为dict写入json，方便后续回测调用

bt_merge_ret.py: 将因子数据与下一期收益率整合，方便选取portfolios时训练模型

bt_get_industry_list: 得到股票的industry方便之后行业中性

bt_portfolios_select.py: 根据历史数据训练模型，每个模型按打分分五组portfolios，生成每个交易日的交易列表，写入json方便回测调用

bt_backtest.py: 回测，直接调用之前生成的各portfolios数据
