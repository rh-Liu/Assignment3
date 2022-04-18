# Assignment3
刘瑞涵 221040051
# 代码简介：

由于数据获取源为聚宽，非会员有流量限制，因此很多步骤选择分开处理，略显繁杂。数据量较大，没有传上github，
如果需要运行可以联系我发数据，不然聚宽的几个数据获取处理比较花时间。

get_factors.py: 从聚宽获得因子数据，并写入本地。

data_preprocess.py: 通过自建函数对因子数据进行去极值、行业市值中性化、标准化，因子数据写入到本地。（运行时间较长）

bt_get_trade_data.py: 得到trading data，没聚宽会员需要运行多次，储存至本地

bt_merge_factor_data.py: 处理因子数据，整合为dict写入json，方便后续回测调用

bt_merge_ret.py: 将因子数据与下一期收益率整合，方便选取portfolios时训练模型

bt_get_industry_list: 得到股票的industry方便之后行业中性

bt_portfolios_select.py: 根据历史数据训练模型，每个模型按打分分五组portfolios，生成每个交易日的交易列表，写入json方便回测调用

bt_backtest.py: 回测，直接调用之前生成的各portfolios数据

# 研究简介
参考：《人工智能3：人工智能选股之支撑向量机模型》——华泰金工

这里用相同的思路回测了随机森林及XGBoost模型，旨在熟悉整个研究实践流程，所用的因子因为聚宽权限的原因只选取了小部分，因此结果会有差异，重在研究流程。

# 研究流程
简要流程见report
