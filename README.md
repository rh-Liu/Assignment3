# Assignment3
刘瑞涵 221040051
# 代码简介：

由于数据获取源为聚宽，非会员有流量限制，因此很多步骤选择分开处理，略显繁杂。数据量较大，没有传上github，
如果需要运行可以联系我发数据，不然聚宽的几个数据获取处理比较花时间。

1. get_factors.py: 从聚宽获得因子数据，并写入本地。
2. data_preprocess.py: 通过自建函数对因子数据进行去极值、行业市值中性化、标准化，因子数据写入到本地。（运行时间较长）
3. bt_get_trade_data.py: 得到trading data，没聚宽会员需要运行多次，储存至本地
4. bt_merge_factor_data.py: 处理因子数据，整合为dict写入json，方便后续回测调用
5. bt_merge_ret.py: 将因子数据与下一期收益率整合，方便选取portfolios时训练模型
6. bt_get_industry_list: 得到股票的industry方便之后行业中性
7. bt_portfolios_select.py: 根据历史数据训练模型，每个模型按打分分五组portfolios，生成每个交易日的交易列表，写入json方便回测调用
8. bt_backtest.py: 回测，直接调用之前生成的各portfolios数据
9. bt_result.py: 结果分析

# 研究简介
参考：《人工智能3：人工智能选股之支撑向量机模型》——华泰金工

这里用相同的思路回测了随机森林及XGBoost模型，旨在熟悉整个研究实践流程，所用的因子因为聚宽权限的原因只选取了小部分，因此结果会有差异，重在研究流程。

# 研究流程
月调仓，在每月往前看三年数据，使用随机森林或XGBoost模型对因子数据与其对应的下个月的收益标签进行训练，预测下一个月收益率处于上涨或下跌标签的概率，将其作为打分方法，对本月的股票进行概率打分，并排序，将其分为5组作为不同的portfolios。

# 回测结果

<img src="https://github.com/algo21-221040051/Assignment3/blob/main/rf_port.png" width="300"><img src="https://github.com/algo21-221040051/Assignment3/blob/main/rf_ind_port.png" width="300"><img src="https://github.com/algo21-221040051/Assignment3/blob/main/xgb_port.png" width="300"><img src="https://github.com/algo21-221040051/Assignment3/blob/main/xgb_ind_port.png" width="300">
<img src="https://github.com/algo21-221040051/Assignment3/blob/main/res_df.png" width="600">  
(其中带有_ind_的为配权时区分了行业的情况）

可以看到RandomForest分组出现了我们想要的结果，并且第一组均战胜了HS300指数，而XGBoost效果就非常差了，这跟Assignment2中的研究结论是不太相符的，之后有精力我也会再检查一下研究过程、回测流程的准确性。（实际上这个时候更新Assignment3正是由于在project的研究中发现了这里的回测有一个错误，因此重新回测总结此研究，并且把结果展示放到了Readme，就当练习markdown了）

# 改进思路
1. 在做project时研究的一篇研报提供了除五分组以外新的审视策略的方法——用第一组对冲第五组，期末考完有精力后我也会加上这一部分（实际上在project中我已经实现了这一部分，不用做过多改动，但目前我还是更想把精力花在期末复习上面）  
2. 同时，如研究简介中所说，本文重在实现方法，未来在实际生产中计划自己慢慢积累有效因子，并结合这些使用因子的方法构建策略。
3. 我还要学习Github相关的使用，目前还是不太熟练，并没有体会到使用Git的便利，还有jupyter、markdown的相关操作等等。  
4. 长路漫漫~
