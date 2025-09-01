from dataclasses import dataclass

from shared.tables.network_optimization_name_registry import NetworkOptimizationSheetNames, \
    TransportationPoliciesSheet, ExpressionBasedCostSheet
from shared.tables.global_name_registry import SitesSheet, CommonColumnNames


@dataclass
class OutputSheet:

    sheet_name: str

    def __iter__(self) -> str:
        for field, value in self.__dict__.items():
            if field != "sheet_name":
                value: str
                yield value

    @property
    def columns(self):
        return self


@dataclass
class OutputCommon:

    origin_latitude: str = "origin_lat"
    origin_longitude: str = "origin_lon"

    origin: str = "origin"
    scenario_id: str = "runID"
    scenario_name: str = "scenario"
    gap: str = "gap"
    primal_bound: str = "primalBound"
    dual_bound: str = "dualBound"


@dataclass
class OutputNOSummarySheet(OutputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.summary

    scenario_name: str = OutputCommon.scenario_name
    optimization_time: str = "optimizationTime"
    gap: str = "optimizationGap"
    primal_bound: str = OutputCommon.primal_bound
    dual_bound: str = OutputCommon.dual_bound
    optimization_status: str = "optimizationStatus"
    obj_function_value: str = "totalCost"
    total_outbound_cost: str = "totalOutboundCost"
    scenario_id: str = OutputCommon.scenario_id
    transportation_cost: str = "totalTransportationCost"
    total_sites_fixed_cost: str = "totalSitesFixedCost"
    total_sites_variable_cost: str = "totalSitesVariableCost"
    total_production_variable_cost: str = "totalProductionVariableCost"
    total_production_fixed_cost: str = "totalProductionFixedCost"
    date_time: str = "dateTime"
    expression_cost: str = "expressionCost"

    all_columns = [
        scenario_name,
        date_time,
        optimization_time,
        obj_function_value,
        total_outbound_cost,
        total_production_variable_cost,
        total_production_fixed_cost,
        total_sites_fixed_cost,
        total_sites_variable_cost,
        transportation_cost,
        expression_cost,
        gap,
        primal_bound,
        dual_bound,
        optimization_status,
    ]


@dataclass
class OutputExpressionCostSummarySheet(OutputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.expression_cost_summary

    scenario_name: str = OutputCommon.scenario_name
    cost_name: str = ExpressionBasedCostSheet.name
    variable_cost: str = ExpressionBasedCostSheet.variable_cost
    expression_name: str = ExpressionBasedCostSheet.expression
    expression_value: str = "expressionValue"
    type: str = ExpressionBasedCostSheet.notes
    all_columns = [
        scenario_name,
        cost_name,
        expression_name,
        variable_cost,
        expression_value,
        type,
    ]


@dataclass
class OutputNOSitesSheet(OutputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.sites

    scenario_name: str = OutputCommon.scenario_name
    scenario_id: str = OutputCommon.scenario_id
    network_node: str = "networkNode"
    opt_status: str = "optimizedStatus"
    fixed_step_cost: str = "FixedStepCost"
    variable_cost: str = "variableCost"
    step_capacity: str = "stepCapacity"
    step_capacity_uom: str = "stepCapacityUoM"
    period: str = "period"
    final_status: str = "finalStatus"
    inbound_volume: str = "inboundVolume"
    outbound_volume: str = "outboundVolume"
    outbound_cost: str = "outboundCost"
    all_columns = [
        scenario_name,
        period,
        SitesSheet.site_id,
        SitesSheet.type,
        network_node,
        SitesSheet.postal_code,
        SitesSheet.city,
        SitesSheet.state,
        SitesSheet.country,
        SitesSheet.latitude,
        SitesSheet.longitude,
        inbound_volume,
        outbound_volume,
        outbound_cost,
        variable_cost,
        step_capacity,
        step_capacity_uom,
        fixed_step_cost,
        final_status,
    ]


@dataclass
class OutputNetworkFlowsSheet(OutputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.network_flows

    scenario_name: str = OutputCommon.scenario_name
    period: str = "period"
    quantity: str = "quantity"
    transportation_cost: str = "transportationCost"
    all_columns = [
        scenario_name,
        period,
        TransportationPoliciesSheet.origin,
        TransportationPoliciesSheet.destination,
        TransportationPoliciesSheet.product,
        TransportationPoliciesSheet.transportation_mode,
        TransportationPoliciesSheet.cost,
        quantity,
        TransportationPoliciesSheet.distance,
        transportation_cost,
    ]


@dataclass
class OutputProductionSummarySheet(OutputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.production_summary

    scenario_name: str = OutputCommon.scenario_name
    period: str = CommonColumnNames.period
    facility: str = "facility"
    product: str = CommonColumnNames.product
    quantity: str = "quantity"
    total_variable_cost: str = "variableCost"
    fixed_step_cost: str = "fixedStepCost"
    step_capacity: str = "stepCapacity"
    bom_name: str = "bomName"

    all_columns = [
        scenario_name,
        period,
        facility,
        product,
        quantity,
        total_variable_cost,
        fixed_step_cost,
        step_capacity,
        bom_name,
    ]


@dataclass
class OutputNOSitesOptions:

    open_site: str = "open"
    close_site: str = "closed"
    initial_node: str = "Initial"
    final_node: str = "Final"
    intermediary_node: str = "Intermediary"


@dataclass
class SolutionStatus:
    infeasible: str = "infeasible"
    optimal: str = "optimal"
