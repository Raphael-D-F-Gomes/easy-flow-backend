from pyomo.core.base.set import Binary
from pyomo.core.base.var import Var
from pyomo.core.base.constraint import ConstraintList

from services.common.user_input import GreenfieldUserInput
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.builder import MILPBuilder
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.pmedian_discrete.model import (
    PMedianDiscreteModel,
)
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.constraints.constraints import (
    Constraints,
)
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.objectives.objectives import (
    Objectives,
)


class PMedianDiscreteBuilder(MILPBuilder):
    """
    This model considers existent facilities
    """

    def __init__(self) -> None:
        repr_name = "p-median concrete"
        name = "pMedian_Concrete"
        self.model = PMedianDiscreteModel("pMedian_Concrete")
        super(PMedianDiscreteBuilder, self).__init__(repr_name, name)

    def create_milp_model(self, data: GreenfieldUserInput) -> PMedianDiscreteModel:
        model = self.model
        model.set_sets(data)
        model.set_parameters(data)
        all_facilities = set(model.set.candidates).union(model.set.included_sites)
        model.var.flow_variables = Var(all_facilities, model.set.customers, domain=Binary)
        model.var.open_variable = Var(model.set.candidate_sites, domain=Binary)
        self.set_objective(model)
        self.set_constraints(model)
        return model

    @staticmethod
    def set_objective(model: PMedianDiscreteModel) -> None:
        model.obj.total_weighted_distance = Objectives.total_weighted_distance(
            model.var.gfa_flow_variables,
            model.param.distances,
            model.param.demand,
            model.set.candidate_sites,
        )

    @staticmethod
    def set_constraints(model: PMedianDiscreteModel) -> None:
        gfa_flow_variables = model.var.gfa_flow_variables
        opening_variable = model.var.opening_variable
        candidate_sites = model.set.candidate_sites
        considering_sites = model.set.considering_candidates_sites
        demand_sites = model.set.demand_sites
        number_of_facilities = model.param.number_of_facilities

        model.const.fixed_include_sites = ConstraintList()
        constraints_expressions = Constraints.set_forced_candidates(
            opening_variable, candidate_sites, considering_sites
        )
        for expression in constraints_expressions:
            model.const.fixed_include_sites.add(expression)

        if not (len(model.set.considering_candidates_sites) == 0 and model.param.number_of_facilities == 0):
            model.const.fixed_number_of_facilities = Constraints.set_fixed_number_of_facilities(
                opening_variable, considering_sites, number_of_facilities
            )

        model.const.linking_constraints = ConstraintList()
        constraint_expressions = Constraints.set_linking_constraint(
            gfa_flow_variables, opening_variable, demand_sites, candidate_sites
        )
        for expression in constraint_expressions:
            model.const.linking_constraints.add(expression)

        model.const.single_sourcing_constraints = ConstraintList()
        constraint_expressions = Constraints.set_single_sourcing(gfa_flow_variables, demand_sites, candidate_sites)
        for expression in constraint_expressions:
            model.const.single_sourcing_constraints.add(expression)
