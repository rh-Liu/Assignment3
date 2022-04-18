import datetime
import os
import json
import addpath
import pandas as pd
import backtrader as bt
import pMatrix
import matplotlib.pyplot as plt
# import multiprocessing
from dateutil.relativedelta import relativedelta
import numpy as np

# 佣金及印花税
class stampDutyCommissionScheme(bt.CommissionInfo):
    params = (
        ('stamp_duty', 0.001),
        ('commission', 0.0005),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        '''
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        '''
        # print('self.p.commission', self.p.commission)
        if size > 0:  # 买入，不考虑印花税
            return size * price * self.p.commission * 100
        elif size < 0:  # 卖出，考虑印花税
            return - size * price * (self.p.stamp_duty + self.p.commission * 100)
        else:
            return 0


# main strategy
class rf_strategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        self.bar_num = 0
        self.last = []
        self.order_list = []

        self.order = None
        self.buyprice = None
        self.buycomm = None


    def next(self):

        # import pickle as pickle
        # with open('normal_future_data.pkl', 'rb') as f:
        #     df = pickle.load(f)

        date = self.datas[0].datetime.date(0)
        try:
            next_date = self.datas[0].datetime.date(1)
            next_mon = next_date.month
        except:
            next_mon = date.month
        # 换仓日
        # if (date + datetime.timedelta(days=1)).day == 1: # 不行
        # if date.strftime('%Y-%m-%d') in port.keys(): # 不行
        if date.month != next_mon:
        # if 1:
            # 取消以往所下订单（已成交的不起作用）
            for o in self.order_list:
                self.cancel(o)
            # 重置订单列表
            self.order_list = []
            try:
                long_list = port[date.strftime('%Y-%m-%d')]
            except:
                long_list = []
            # 若上期股票未出现在本期交易列表中，则平仓
            for i in self.last:
                if i not in long_list:
                    d = self.getdatabyname(i)
                    # print('平仓 ', d._name, self.getposition(d).size)
                    o = self.close(data=d)
                    self.order_list.append(o)

            # 当前账户价值
            total_value = self.broker.get_value()
            # print(self.broker.getposition(data=d))
            self.log('当前总市值 %.2f' % total_value)

            # if date.year == 2014 and date.month == 12:
            #     print('!')
            #     print('!')

            if np.isnan(total_value):
                print('?')
                print('?')

            if len(long_list):
                # 每支股票等权买入，预留5%资金应付佣金和误差
                buy_percentage = (1-0.05)/len(long_list)
                # 目标市值
                target_value = buy_percentage * total_value

                # 买入
                for d in long_list:

                    data = self.getdatabyname(d)
                    # 按次日开盘价计算下单量，100的整数倍
                    try:
                        size = int(abs(target_value / data.open[1] // 100 * 100))
                    except:
                        try:
                            size = int(abs(target_value / data.close[0] // 100 * 100))
                        except:
                            size = 0
                            # print(buy_percentage, total_value)
                    o = self.order_target_size(data=d, target=size)
                    self.order_list.append(o)

            self.last = list(set(long_list))
    # # 交易日志
    # def notify_order(self, order):
    #     if order.status in [order.Submitted, order.Accepted]:
    #         # Buy/Sell order submitted/accepted to/by broker - Nothing to do
    #         return
    #
    #     Check if an order has been completed
    #     Attention: broker could reject order if not enougth cash
    #     if order.status in [order.Completed, order.Canceled, order.Margin]:
    #         if order.isbuy():
    #             self.log(
    #                 'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
    #                 (order.executed.price,
    #                  order.executed.value,
    #                  order.executed.comm,
    #                  order.executed.size,
    #                  order.data._name))
    #         else:  # Sell
    #             self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
    #                      (order.executed.price,
    #                       order.executed.value,
    #                       order.executed.comm,
    #                       order.executed.size,
    #                       order.data._name))
    #
    # def notify_trade(self, trade):
    #     if trade.isclosed:
    #         self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
    #                  (trade.pnl, trade.pnlcomm))

# def value_cal(init_cash, ret_df):
#     value_df = pd.DataFrame()
#     value_df.loc[ret_df.index[0], 'value'] = init_cash
#     for i, date in enumerate(ret_df.index[1:]):
#         value_df.loc[date, 'value'] = (1+ret_df.iloc[i, 0]) * value_df.iloc[i, 0]
#     return value_df

def value_cal(init_cash, ret_df):
    '''
    calculate the net value from the percent return
    '''
    ret_mat = np.array(ret_df)
    value_mat = np.ones([ret_df.shape[0], ret_df.shape[1]])
    for i in range(1, value_mat.shape[0]):
        value_mat[i] = value_mat[i - 1] * (ret_mat[i - 1] + 1)
    value_df = pd.DataFrame(value_mat, index=ret_df.index, columns=ret_df.columns)
    return value_df


def get_all_symbol(port_list):
    '''
    get all the symbol from the json, which is prepared before.
    '''
    all_symbol = []
    for port_name in port_list:
        with open(os.path.join(addpath.data_path, 'strategy_temps', port_name + '.json'), 'r') as f:
            data = json.load(f)
        port = data
        del data
        for k in port.keys():
            all_symbol += port[k]
    all_symbol = list(set(all_symbol))
    return all_symbol


def pre_load_data(symbol_list, start, end, pkl_path):
    '''
    preload the data for all the strategies.
    :return: the programm will rise assert because I modified the Cerebro, but the job is done.
    '''
    cb = bt.Cerebro()
    for symbol in symbol_list:
        trading = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', symbol + '.csv'), parse_dates=True,
                              index_col=0)
        bt_end1 = datetime.datetime.strptime(bt_end, '%Y-%m-%d') \
                  + datetime.timedelta(1) + relativedelta(months=1) - datetime.timedelta(1)
        bt_end1 = bt_end1.strftime('%Y-%m-%d')
        trading = trading[bt_start: bt_end1].ffill()
        trading = bt.feeds.PandasData(dataname=trading, name=symbol)
        cb.adddata(trading, name=symbol)
    print('Data feed done')
    cb.run(save_my_data=True, pkl_path=pkl_path)
    print('Data preload done')


def bt_of_port(port_name, bt_start, bt_end):
    '''
    backtest for one portfolio, using the data preloaded by last function.
    '''
    print(port_name, ' backtest begin')

    cb = bt.Cerebro()
    # 设置佣金及印花税
    # comminfo = stampDutyCommissionScheme(stamp_duty=0.001, commission=0.0005)
    # cb.broker.addcommissioninfo(comminfo)
    cb.broker.setcommission(commission=0.001)

    all_symbol = []
    for k in port.keys():
        all_symbol += port[k]
    all_symbol = list(set(all_symbol))

    for symbol in all_symbol:
        trading = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', symbol + '.csv'), parse_dates=True,
                              index_col=0)
        bt_end1 = datetime.datetime.strptime(bt_end, '%Y-%m-%d')\
                  +datetime.timedelta(1)+relativedelta(months=1)-datetime.timedelta(1)
        bt_end1 = bt_end1.strftime('%Y-%m-%d')
        trading = trading[bt_start: bt_end1].ffill()
        trading = bt.feeds.PandasData(dataname=trading, name=symbol)
        cb.adddata(trading, name=symbol)
    print('Data feed done')

    # ### multiprocessing for feeding data
    # def data_feed(symbol):
    #     trading = pd.read_csv(os.path.join(addpath.data_path, 'cn_data', 'trading', symbol + '.csv'), parse_dates=True,
    #                           index_col=0)
    #     trading = trading[bt_start: bt_end]
    #     trading = bt.feeds.PandasData(dataname=trading, name=symbol)
    #     cb.adddata(trading)
    #     return trading
    # pool = multiprocessing.Pool(10)
    # res_list = []
    # for symbol in all_symbol:
    #     res = pool.apply_async(data_feed, args=(symbol,))
    #     res_list.append(res)
    # pool.close()
    # pool.join()
    #
    # for i in range(len(all_symbol)):
    #     res_list[i].get()
    #     # cb.adddata(res_list[i].get())
    # print('Data feed done')
    # ### multiprocessing for feeding data

    # 初始资金
    startcash = 100000000.0
    cb.broker.setcash(startcash)
    # 防止下单时现金不够被拒绝。只在执行时检查现金够不够。
    # cb.broker.set_checksubmit(True)

    # 导入策略
    cb.addstrategy(rf_strategy)

    # 获取策略运行的指标
    print('Starting Portfolio Value: %.2f' % cb.broker.getvalue())
    cb.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')

    strats = cb.run(save_my_data=False, load_my_data=True, pkl_path='all_preload_data.pkl')
    strat = strats[0]
    print(port_name, ' run done')

    # # 获取回测结束后的总资金
    portvalue = cb.broker.getvalue()
    pnl = portvalue - startcash
    # # 打印结果
    print(f'总资金: {round(portvalue, 2)}')
    print(f'净收益: {round(pnl, 2)}')

    ret = strat.analyzers.timereturn.get_analysis()
    ret_df = pd.DataFrame({'datetime': ret.keys(), 'ret': ret.values()})
    ret_df.set_index('datetime', inplace=True)
    val_df = value_cal(startcash, ret_df)
    # val_df.to_csv(os.path.join(addpath.data_path, 'strategy_temps', 'pv_'+port_name+'.csv'))

    performance_mat = pMatrix.p_matrix(val_df, freq='D', start=bt_start, end=bt_end, exchange='CN')
    print(port_name)
    print(performance_mat)
    val_df.plot()
    plt.title(port_name)
    plt.show()


if __name__ == '__main__':

    ts = datetime.datetime.now()

    bt_start = '2011-12-31'
    bt_end = '2021-11-30'
    port_list = ['rf_ind_port_1', 'rf_ind_port_2', 'rf_ind_port_3', 'rf_ind_port_4', 'rf_ind_port_5',
                 'rf_port_1', 'rf_port_2', 'rf_port_3', 'rf_port_4', 'rf_port_5',
                 'xgb_ind_port_1', 'xgb_ind_port_2', 'xgb_ind_port_3', 'xgb_ind_port_4', 'xgb_ind_port_5',
                 'xgb_port_1', 'xgb_port_2', 'xgb_port_3', 'xgb_port_4', 'xgb_port_5']

    ### preload all the data, reducing the time running the strategy
    # all_symbol = get_all_symbol(port_list)
    # pre_load_data(symbol_list=all_symbol, start=bt_start, end=bt_end, pkl_path='all_preload_data.pkl')

    ### backtest for all the portfolios
    for port_name in port_list:
        ts1 = datetime.datetime.now()

        # 交易清单
        with open(os.path.join(addpath.data_path, 'strategy_temps', port_name + '.json'), 'r') as f:
            data = json.load(f)
        port = data
        del data

        try:
            bt_of_port(port_name=port_name, bt_start=bt_start, bt_end=bt_end)
        except:
            continue

        te1 = datetime.datetime.now()
        print('One portfolio backtest time: ', te1 - ts1)

    te = datetime.datetime.now()
    print('Time: ', te-ts)