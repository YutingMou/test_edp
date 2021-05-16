import pyomo
import pyomo.environ as pe
from pyomo.opt import SolverStatus, TerminationCondition

from .generator import Generator
from .load import Load


class EconomicDispatch:
    def __init__(self):
        self.generators = dict()
        self.loads = dict()

    def add_generator(self, generator: Generator):
        self.generators[generator.id] = generator

    def add_load(self, load: Load):
        self.loads[load.id] = load

    def run_market_clearing(self):
        ################################################################################
        # Initiate pyomo model
        ################################################################################
        m = pe.ConcreteModel()
        # Make duals available
        m.dual = pe.Suffix(direction=pe.Suffix.IMPORT)
        # Set of all generators
        m.generators = pe.Set(initialize=[g for g in self.generators.values()], dimen=1)
        m.loads = pe.Set(initialize=[load for load in self.loads.values()], dimen=1)
        m.time_steps = pe.Set(initialize=[load.time_step for load in self.loads.values()], dimen=1)

        ################################################################################
        # Variables
        ################################################################################
        # Production of each generator (>= 0)
        m.production = pe.Var(m.generators, m.time_steps, domain=pe.NonNegativeReals)

        ################################################################################
        # Objective
        # Total production cost
        ################################################################################
        def Total_Social_Cost(m):
            return (
                + sum(g.c2 * m.production[g, t] * m.production[g, t]
                      + g.c1 * m.production[g, t] for g in m.generators for t in m.time_steps)
            )

        m.objective = pe.Objective(rule=Total_Social_Cost, sense=pe.minimize)

        ################################################################################
        # Constraints
        ################################################################################
        # Production capacity
        def Production_Upper_Bound_Rule(m, g, t):
            return m.production[g, t] <= g.capacity

        m.Production_Upper_Bound = pe.Constraint(m.generators, m.time_steps, rule=Production_Upper_Bound_Rule)

        # Market balance
        def Market_Balance_Rule(m, t):
            return sum(m.production[g, t] for g in m.generators) == \
                   sum(load.capacity for load in m.loads if load.time_step == t)

        m.Market_Balance = pe.Constraint(m.time_steps, rule=Market_Balance_Rule)

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
            for t in m.time_steps:
                print(f"Time step is {t}.")
                for g in m.generators:
                    g.production = m.production[g,t].value
                    print(f"{str(g):15s} | {g.production:3.4f}|")
                market_clearing_price = m.dual[m.Market_Balance[t]]
                print(f"The market clearing price is {market_clearing_price}.")

            print("-" * 50)
            print("Model has been solved.")
        else:
            print("Something went wrong.")
