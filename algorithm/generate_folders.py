import os
import addpath

def generate_new_folder(folder):
    if not os.path.exists(folder):
        print(f"Create new folder {folder}")
        os.makedirs(folder)
    else:
        print(f"Folder {folder} already existed.")

def data_path_generate(path_name):
    generate_new_folder(os.path.join(addpath.data_path,path_name))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'trading'))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'financial'))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'reference'))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'investment_univ'))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'factors'))
    generate_new_folder(os.path.join(addpath.data_path,path_name,'CS_factors'))

def generate_new_folders():
    generate_new_folder(addpath.data_path)
    generate_new_folder(addpath.portfolio_path)
    data_path_generate('cn_data')
    data_path_generate('hk_data')
    data_path_generate('us_data')
    generate_new_folder(addpath.result_path)
    generate_new_folder(os.path.join(addpath.result_path,'backtesting'))
    generate_new_folder(os.path.join(addpath.result_path,'algo_space_data'))

if __name__ == "__main__":
    generate_new_folders()