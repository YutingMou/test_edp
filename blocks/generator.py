import pandas as pd


class Generator:
    def __init__(self, generator_id: int, data: pd.Series):
        self.id = generator_id
        self.market_zone = str(data["MarketZone"]).upper()
        self.capacity = data["Capacity"]
        self.c2 = data["c2"]
        self.c1 = data["c1"]
        self.c0 = data["c0"]  # start-up cost, assume to be 0 here

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self) -> str:
        return f"Generator[{self.id},{self.capacity}]"
