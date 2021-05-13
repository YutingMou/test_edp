from .generator import Generator


class EconomicDispatch:
    def __init__(self):
        self.generators = dict()
        self.load = float  # extend it to pd.Series to consider multiple steps

    def add_generator(self, generator: Generator):
        self.generators[generator.id] = generator

    def add_load(self, load: float):
        self.load = load
