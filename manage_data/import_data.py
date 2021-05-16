import pandas as pd

from blocks.economic_dispatch import EconomicDispatch
from blocks.generator import Generator
from blocks.load import Load


def import_data(file_path: str):
    edp = EconomicDispatch()

    df_generator = pd.read_excel(file_path, sheet_name="Generators", index_col=[0])
    for row_idx, row in df_generator.iterrows():
        generator = Generator(row_idx, row)
        edp.add_generator(generator)

    df_load = pd.read_excel(file_path, sheet_name="Load", index_col=[0])
    for row_idx, row in df_load.iterrows():
        load = Load(row_idx, row)
        edp.add_load(load)

    return edp
