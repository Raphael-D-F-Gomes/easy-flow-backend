from typing import Dict, Tuple, List, Set, Any
from dataclasses import dataclass
from itertools import product as prod

import pandas as pd
import numpy as np

from optimization_construction_api.opt_construction_function_names import OptConstructionFunctionName
from optimization_construction_api.etl.types import (
    Period,
    Destination,
    Product,
    Origin,
    Site,
    StepID,
    Step,
    Ratio,
    Status,
    Mode,
    ExpressionName,
    Unit,
)
from optimization_construction_api.etl.user_input.tables.network_optimization_information import (
    NetworkOptimizationSitesTable,
    NetworkOptimizationDemandTable,
    ProductsTable,
    PeriodsTable,
    TransportationModeTable,
    TransportationPoliciesTable,
    GroupsTable,
    GroupMembersTable,
    StepCostTable,
    InventoryPoliciesTable,
    FlowConstraintsTable,
    ExpressionConstraintsTable,
    StepCostDefinitionsTable,
    ExpressionBasedCostsTable,
    SiteConstraintsTable,
    ProductionConstraintsTable,
    BillOfMaterialsTable,
    ProductionPoliciesTable,
)
from optimization_construction_api.etl.user_input.tables.auxiliary_classes import AuxiliaryInfo

from shared.tables.network_optimization_name_registry import NetworkOptimizationSheetNames, StepCostSheet, \
    BillOfMaterialsSheet
from shared.tables.network_optimization_options import OptionsName, UnitOfMeasureOptions
from shared.logs.decorator import thread_log_decorator_function
from shared.tables.global_name_registry import GlobalSheetNames


@dataclass
class NetworkOptimizationUserInput:
    """
    The tables won't pass through validation here
    therefore the dataframe should already be formatted
    and verified
    """

    @thread_log_decorator_function(OptConstructionFunctionName().init_data_processing_class)
    def __init__(self, tables: Dict[str, pd.DataFrame]):

        self.registry = RegistryUserInput(tables)
        self.attributes = AttributesUserInput(tables)
        self.policies = PoliciesUserInput(tables)
        self.constraints = ConstraintsUserInput(tables)
        self.production = ProductionUserInput(tables)

    def get_sites_step_info(self) -> Dict[Tuple[Period, Site, StepID, Step], Dict[str, float]]:
        """
        Get sites without demand
        """
        all_sites = self.registry.sites.get_sites()
        demands = self.policies.get_clients()
        periods = self.registry.periods.get_periods()
        sites_without_demand = set(prod(periods, all_sites.difference(demands)))
        sites_steps_info: Dict[Tuple[Period, Site, StepID, Step], Dict[str, float]] = {}
        if self.attributes.step_cost.data.empty:
            sites_steps_info = {
                (period, site, StepID(OptionsName.none), Step(0)):
                    {StepCostSheet.capacity: np.nan, StepCostSheet.cost: np.nan}
                for period, site in sites_without_demand
            }
            return sites_steps_info

        step_by_site = self.registry.sites.get_step_by_site()
        step_info = self.attributes.step_cost.get_step_info()
        for period, site in sites_without_demand:
            step_id = step_by_site.get(site, OptionsName.none)
            if step_id == OptionsName.none:
                sites_steps_info[period, site, StepID(OptionsName.none), Step(0)] = {
                    StepCostSheet.capacity: np.nan,
                    StepCostSheet.cost: np.nan,
                }
            else:
                for step in step_info[step_id]:
                    if (period, site, step_by_site[site], step) not in sites_steps_info:
                        capacity = step_info[step_by_site[site]][step][StepCostSheet.capacity]
                        cost = step_info[step_by_site[site]][step][StepCostSheet.cost]
                        sites_steps_info[period, site, step_by_site[site], step] = {
                            StepCostSheet.capacity: capacity,
                            StepCostSheet.cost: cost,
                        }

        return sites_steps_info

    def get_production_step_info(self) -> Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, float]]:
        ratio_by_product = self.registry.products.get_unit_by_products()
        auxiliary_info = AuxiliaryInfo(
            self.attributes.step_cost.get_step_info(),
            self.attributes.step_cost_definitions.get_unit_by_step(),
            ratio_by_product,
            self.production.bill_of_materials.get_components_from_bom(),
        )
        periods = self.registry.periods.get_periods()
        group_members = self.attributes.group_members.data
        self.production.production_policies.construct_production_cost_info(
            group_members, periods, auxiliary_info
        )
        production_step_info = self.production.production_policies.get_production_fixed_step_cost_info()
        return production_step_info

    def get_production_policies_by_raw_material(
            self,
    ) -> Dict[Tuple[Period, Site, Product], Dict[Tuple[Period, Site, Product], float]]:
        ratio_by_product = self.registry.products.get_unit_by_products()
        bill_of_materials = self.production.bill_of_materials.get_bom_with_quantity_by_unit(ratio_by_product)
        production_sites_with_bom = self.production.production_policies.get_production_sites_with_bom()
        production_policies_by_raw_material: Dict[
            Tuple[Period, Site, Product], Dict[Tuple[Period, Site, Product], float]
        ] = {}
        for production_policies, bom_name in production_sites_with_bom.items():
            if pd.notna(bom_name):
                for i, row in bill_of_materials[
                    bill_of_materials[BillOfMaterialsSheet.bom_name] == bom_name
                ].iterrows():
                    if (production_policies[0], production_policies[1], row[BillOfMaterialsSheet.product])\
                            in production_policies_by_raw_material:
                        production_policies_by_raw_material[(
                            production_policies[0], production_policies[1], row[BillOfMaterialsSheet.product]
                        )].update({production_policies: row[BillOfMaterialsSheet.quantity]})
                    else:
                        production_policies_by_raw_material[(
                            production_policies[0], production_policies[1], row[BillOfMaterialsSheet.product]
                        )] = {production_policies: row[BillOfMaterialsSheet.quantity]}

        return production_policies_by_raw_material

    def get_origins(self) -> Dict[Origin, Status]:
        all_sites = self.registry.sites.get_sites_with_status()
        demands = self.policies.get_clients()
        sites_without_demand: Dict[Origin, Status] = {Origin(site): Status(status)
                                                      for site, status in all_sites.items() if site not in demands}
        return sites_without_demand

    def get_flows(self) -> List[Tuple[Period, Origin, Destination, Mode, Product]]:
        flows = list(self.policies.transportation_policies.flows_cost)

        return flows

    def get_flows_cost(self) -> Dict[Tuple[Period, Origin, Destination, Mode, Product], float]:
        group_members = self.attributes.group_members.data
        periods = self.registry.periods.get_periods()
        ratio_by_products = self.registry.products.get_unit_by_products()
        return self.policies.get_flows_cost(group_members, periods, ratio_by_products)

    def get_sites_variable_cost(self) -> Dict[Tuple[Period, Origin], float]:
        periods = self.get_periods()
        variable_cost = self.registry.sites.get_variable_costs()
        variable_cost_by_period: Dict[Tuple[Period, Origin], float] = {}
        for period, origin in prod(periods, list(variable_cost)):
            variable_cost_by_period[period, origin] = variable_cost[origin]
        return variable_cost_by_period

    def get_periods(self) -> List[Period]:
        return self.registry.periods.get_periods()

    def get_outbound_costs(self) -> Dict[Tuple[Origin, Product], float]:
        ratio_by_product = self.registry.products.get_unit_by_products()
        outbound_costs = self.policies.inventory_policies.get_outbound_costs(
            self.attributes.group_members.data, ratio_by_product
        )

        return outbound_costs

    def get_ratio_by_origin_by_product_capacity_unit_config(self) -> Dict[Origin, Dict[Product, Ratio]]:
        ratio_by_unit = self.registry.products.get_unit_by_products()
        origins = self.policies.transportation_policies.get_origins()
        if self.attributes.step_cost.data.empty:
            origin_steps = [(origin, StepID(OptionsName.none)) for origin in origins]
        else:
            origin_steps = self.registry.sites.get_sites_step_ids(origins)

        unit_by_step = self.attributes.step_cost_definitions.get_unit_by_step()

        ratio_by_origin_by_product: Dict[Origin, Dict[Product, Ratio]] = {}
        for origin, step_id in origin_steps:
            unit = unit_by_step.get(step_id, None)
            if unit:
                ratio_by_origin_by_product[origin] = ratio_by_unit[unit]

        return ratio_by_origin_by_product

    def get_ratio_by_origin_by_product_variable_cost_unit_config(self) -> Dict[Origin, Dict[Product, Ratio]]:
        ratio_by_unit = self.registry.products.get_unit_by_products()
        unit_by_origin = self.registry.sites.get_variable_costs_unit_of_measure()

        ratio_by_origin_by_product: Dict[Origin, Dict[Product, Ratio]] = {}
        for origin, unit in unit_by_origin.items():
            if unit in UnitOfMeasureOptions.units_indexes:
                ratio_by_origin_by_product[origin] = ratio_by_unit[unit]

        return ratio_by_origin_by_product

    def get_production_and_intermediary_nodes(self) -> Set[Tuple[Period, Site, Product]]:

        finished_product_nodes = self.policies.transportation_policies.get_production_and_intermediary_nodes()
        finished_product_nodes = finished_product_nodes.difference(self.policies.customers.destinations_demand)
        production_nodes = set(self.production.production_policies.get_production_sites_with_bom())
        raw_product_nodes = self.production.production_policies.get_raw_product_nodes()
        finished_product_nodes = finished_product_nodes.union(production_nodes)
        finished_product_nodes = finished_product_nodes.union(raw_product_nodes)

        return finished_product_nodes

    def get_big_m(self) -> float:
        demands_summation = self.policies.customers.get_demands_summation()
        if self.production.bill_of_materials.data.empty:
            return demands_summation

        boms = self.production.production_policies.get_production_policies_boms()
        if len(boms) == 0:
            return demands_summation

        ratio_by_product = self.registry.products.get_unit_by_products()
        big_m_factor = self.production.bill_of_materials.get_highest_quantity_between_boms(boms, ratio_by_product)

        return demands_summation * big_m_factor


class RegistryUserInput:
    def __init__(self, tables: Dict[str, pd.DataFrame]) -> None:
        self.sites = NetworkOptimizationSitesTable(tables.get(NetworkOptimizationSheetNames.sites, pd.DataFrame({})))
        self.products = ProductsTable(tables.get(NetworkOptimizationSheetNames.products, pd.DataFrame({})))
        self.periods = PeriodsTable(tables.get(NetworkOptimizationSheetNames.periods, pd.DataFrame({})))
        self.transportation_modes = TransportationModeTable(
            tables.get(NetworkOptimizationSheetNames.transportation_modes, pd.DataFrame({}))
        )


class AttributesUserInput:
    def __init__(self, tables: Dict[str, pd.DataFrame]) -> None:
        self.groups = GroupsTable(tables.get(NetworkOptimizationSheetNames.groups, pd.DataFrame({})))
        self.group_members = GroupMembersTable(
            tables.get(NetworkOptimizationSheetNames.group_members, pd.DataFrame({}))
        )
        self.step_cost = StepCostTable(tables.get(NetworkOptimizationSheetNames.step_cost, pd.DataFrame({})))
        self.step_cost_definitions = StepCostDefinitionsTable(
            tables.get(NetworkOptimizationSheetNames.step_cost_definitions, pd.DataFrame())
        )


class ProductionUserInput:
    def __init__(self, tables: Dict[str, pd.DataFrame]) -> None:
        self.production_policies = ProductionPoliciesTable(
            tables.get(NetworkOptimizationSheetNames.production_policies, pd.DataFrame({}))
        )
        self.bill_of_materials = BillOfMaterialsTable(
            tables.get(NetworkOptimizationSheetNames.bill_of_materials, pd.DataFrame({}))
        )


class PoliciesUserInput:
    def __init__(self, tables: Dict[str, pd.DataFrame]) -> None:
        self.customers = NetworkOptimizationDemandTable(
            tables.get(GlobalSheetNames.demand, pd.DataFrame({}))
        )
        self.transportation_policies = TransportationPoliciesTable(
            tables.get(NetworkOptimizationSheetNames.transportation_policies, pd.DataFrame({}))
        )
        self.inventory_policies = InventoryPoliciesTable(
            tables.get(NetworkOptimizationSheetNames.inventory_policies, pd.DataFrame({}))
        )

    def get_flows_cost(
        self,
        group_members: pd.DataFrame,
        periods: List[Period],
        ratio_by_product: Dict[Unit, Dict[Product, Ratio]],
    ) -> Dict[Tuple[Period, Origin, Destination, Mode, Product], float]:

        if len(self.transportation_policies.flows_cost) > 0:
            return self.transportation_policies.flows_cost

        extended_flows = self.transportation_policies.get_extended_flows(group_members)

        flows_cost_by_period: Dict[Tuple[Period, Origin, Destination, Mode, Product], float] = {}
        for period, flow in prod(periods, extended_flows):
            unit_of_measure = extended_flows[flow][self.transportation_policies.columns.product_cost_basis]
            if unit_of_measure in UnitOfMeasureOptions.units_indexes:
                flows_cost_by_period[
                    period, Origin(flow[0]), Destination(flow[1]), Mode(flow[2]), Product(flow[3])
                ] = float(
                    extended_flows[flow][self.transportation_policies.columns.cost] *
                    ratio_by_product[unit_of_measure][flow[3]]
                )
            else:
                flows_cost_by_period[
                    period, Origin(flow[0]), Destination(flow[1]), Mode(flow[2]), Product(flow[3])
                ] = float(
                    extended_flows[flow][self.transportation_policies.columns.cost]
                )

        self.transportation_policies.flows_cost = flows_cost_by_period

        return flows_cost_by_period

    @staticmethod
    def get_origins_and_destinations(
            extended_flows: Dict[Tuple[Any, ...], Dict[str, Any]],
    ) -> Tuple[Set[Tuple[Origin, Product]], Set[Tuple[Destination, Product]]]:

        origins = set()
        destinations = set()

        for flow in extended_flows:
            origins.add((flow[0], flow[3]))
            destinations.add((flow[1], flow[3]))

        return origins, destinations

    def get_destinations_demand(self) -> Dict[Tuple[Period, Destination, Product], float]:
        return self.customers.get_destinations_demand()

    def get_clients(self) -> Set[Destination]:
        return self.customers.get_clients()


class ConstraintsUserInput:
    def __init__(self, tables: Dict[str, pd.DataFrame]) -> None:
        self.flow_constraints = FlowConstraintsTable(
            tables.get(NetworkOptimizationSheetNames.flow_constraints, pd.DataFrame({}))
        )
        self.site_constraints = SiteConstraintsTable(
            tables.get(NetworkOptimizationSheetNames.site_constraints, pd.DataFrame({}))
        )
        self.expression_constraints = ExpressionConstraintsTable(
            tables.get(NetworkOptimizationSheetNames.expression_constraints, pd.DataFrame({}))
        )

        self.expression_based_costs = ExpressionBasedCostsTable(
            tables.get(NetworkOptimizationSheetNames.expression_based_costs, pd.DataFrame({}))
        )

        self.production_constraints = ProductionConstraintsTable(
            tables.get(NetworkOptimizationSheetNames.production_constraints, pd.DataFrame({}))
        )

    def get_defined_constraints(self) -> List[ExpressionName]:
        define_constraints: List[ExpressionName] = []
        define_constraints += self.expression_constraints.get_define_expression_constraints()
        define_constraints += self.flow_constraints.get_defined_flow_constraints()
        define_constraints += self.site_constraints.get_defined_site_constraints()
        define_constraints += self.production_constraints.get_defined_production_constraints()
        return define_constraints

    def get_cond_min_expression_constraints(self) -> List[ExpressionName]:
        return self.expression_constraints.get_cond_min_expression_constraints()
