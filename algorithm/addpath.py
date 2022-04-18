from os.path import dirname, abspath, join
import sys
algo_path = dirname(__file__)
root_path = dirname(dirname(abspath(__file__)))
data_path = join(root_path, 'data')
result_path = join(root_path, 'results')
config_path = join(root_path, 'config')
portfolio_path = join(data_path, "strategy_temps")

class algo():
    current_portfolio_name = {}
