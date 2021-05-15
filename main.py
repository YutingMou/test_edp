import os

from manage_data.import_data import import_data

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    file_name = "test.xlsx"
    file_path = os.path.join(data_dir, file_name)
    edp_test = import_data(file_path)
    edp_test.run_market_clearing()
