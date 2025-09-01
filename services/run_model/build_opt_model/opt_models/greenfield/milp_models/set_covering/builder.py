from pyomo.core.base import Binary
from pyomo.core.base.var import Var
from pyomo.core.base.constraint import ConstraintList

from services.common.user_input import GreenfieldUserInput
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.builder import MILPBuilder
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.constraints.constraints import (
    Constraints,
)
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.set_covering.model import (
    SetCoveringModel,
)
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.pmedian_discrete.builder import (
    PMedianDiscreteBuilder,
)
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.objectives.objectives import (
    Objectives,
)


class SetCoveringBuilder(MILPBuilder):
    def __init__(self) -> None:
        repr_name = "p-median concrete"
        name = "pMedian_Concrete"
        super(SetCoveringBuilder, self).__init__(repr_name, name)
        self.model = SetCoveringModel(name)

    def create_milp_model(self, data: GreenfieldUserInput) -> SetCoveringModel:
        model = self.model
        model.set_sets(data)
        model.set_parameters(data)
        model.var.gfa_flow_variables = Var(model.set.candidate_sites, model.set.demand_sites, domain=Binary)
        model.var.opening_variable = Var(model.set.candidate_sites, domain=Binary)
        self.set_objective(model)
        self.set_constraints(model)
        return model

    @staticmethod
    def set_objective_(model: SetCoveringModel) -> None:
        PMedianDiscreteBuilder.set_objective(model)

    @staticmethod
    def set_objective(model: SetCoveringModel) -> None:
        model.obj.total_weighted_distance = Objectives.total_number_of_facilities_and_total_weighted_distance(
            model.var.gfa_flow_variables,
            model.param.distances,
            model.param.demand,
            model.set.candidate_sites,
            model.var.opening_variable,
            model.param.total_number_of_facilities_weight,
        )

    @staticmethod
    def set_constraints(model: SetCoveringModel) -> None:
        gfa_flow_variables = model.var.gfa_flow_variables
        opening_variable = model.var.opening_variable
        candidate_sites = model.set.candidate_sites
        considering_sites = model.set.considering_candidates_sites
        demand_sites = model.set.demand_sites

        model.const.fixed_include_sites = ConstraintList()
        constraints_expressions = Constraints.set_forced_candidates(
            opening_variable, candidate_sites, considering_sites
        )
        for expression in constraints_expressions:
            model.const.fixed_include_sites.add(expression)

        model.const.serv_distance = ConstraintList()
        constraints_expressions = Constraints.set_service_distance(
            model.var.gfa_flow_variables,
            model.param.serv_distance,
            model.param.distance_demand_percentage,
            model.param.demand,
        )
        for expression in constraints_expressions:
            model.const.serv_distance.add(expression)

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
