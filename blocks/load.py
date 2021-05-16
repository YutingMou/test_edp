import pandas as pd


class Load:
    def __init__(self, load_id: int, data: pd.Series):
        self.id = load_id
        self.time_step = int(data["Time"])
        self.capacity = data["Capacity"]

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self) -> str:
        return f"Load[{self.id},{self.value}]"
