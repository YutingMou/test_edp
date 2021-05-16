import pyomo
import pyomo.environ as pe
from pyomo.opt import SolverStatus, TerminationCondition

from .generator import Generator


class EconomicDispatch:
    def __init__(self):
        self.generators = dict()
        self.load = float  # extend it to pd.Series to consider multiple steps

    def add_generator(self, generator: Generator):
        self.generators[generator.id] = generator

    def add_load(self, load: float):
        self.load = load

    def run_market_clearing(self):
        ################################################################################
        # Initiate pyomo model
        ################################################################################
        m = pe.ConcreteModel()
        # Make duals available
        m.dual = pe.Suffix(direction=pe.Suffix.IMPORT)
        # Set of all generators
        m.generators = pe.Set(initialize=[g for g in self.generators.values()], dimen=1)

        ################################################################################
        # Variables
        ################################################################################
        # Production of each generator (>= 0)
        m.production = pe.Var(m.generators, domain=pe.NonNegativeReals)

        ################################################################################
        # Objective
        # Total production cost
        ################################################################################
        def Total_Social_Cost(m):
            return (
                + sum(g.c2 * m.production[g] * m.production[g]
                      + g.c1 * m.production[g] for g in m.generators)
            )

        m.objective = pe.Objective(rule=Total_Social_Cost, sense=pe.minimize)

        ################################################################################
        # Constraints
        ################################################################################
        # Production capacity
        def Production_Upper_Bound_Rule(m, g):
            return m.production[g] <= g.capacity

        m.Production_Upper_Bound = pe.Constraint(m.generators, rule=Production_Upper_Bound_Rule)

        # Market balance
        def Market_Balance_Rule(m):
            return sum(m.production[g] for g in m.generators) == self.load

        m.Market_Balance = pe.Constraint(rule=Market_Balance_Rule)

        ################################################################################
        # solve the model
        ################################################################################
        solver = pyomo.opt.SolverFactory('gams')
        result = solver.solve(m, tee=False, keepfiles=False)  # tee: show solver info or not

        if result.solver.termination_condition == TerminationCondition.optimal or \
                result.solver.termination_condition == TerminationCondition.locallyOptimal:
            # m.display()  # display all the results
            print("-" * 50)
            print(" " * 10 + "Generator| Production |")
            print("-" * 50)

            for g in m.generators:
                g.production = round(m.production[g].value, ndigits=6)
                print(f"{str(g):15s} | {g.production:3.4f}|")
            market_clearing_price = round(m.dual[m.Market_Balance], ndigits=6)

            print("-" * 50)

            print(f"The market clearing price is {market_clearing_price}.")

            print("Model has been solved.")
        else:
            print("Something went wrong.")
