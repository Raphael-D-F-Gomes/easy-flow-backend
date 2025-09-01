from typing import Dict, Tuple, List, Set, Any

import pandas as pd

from optimization_construction_api.etl.types import Origin, Product, Period, Destination, Mode, Site, Ratio, Unit
from optimization_construction_api.etl.user_input.tables import NetworkOptimizationTable
from shared.tables.network_optimization_name_registry import (
    TransportationPoliciesSheet,
    InventoryPoliciesSheet,
)
from shared.tables.network_optimization_options import UnitOfMeasureOptions
from shared.utils.group_features import get_extended_items_with_value


class InventoryPoliciesTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(InventoryPoliciesTable, self).__init__(InventoryPoliciesSheet.sheet_name, InventoryPoliciesSheet(), data)
        self.columns: InventoryPoliciesSheet = InventoryPoliciesSheet()

    def get_outbound_costs(
        self,
        group_members: pd.DataFrame,
        ratio_by_product: Dict[Unit, Dict[Product, Ratio]],
    ) -> Dict[Tuple[Origin, Product], float]:
        if self.data.empty:
            return {}
        inventory_indexes = [InventoryPoliciesSheet.location, InventoryPoliciesSheet.product]
        cost_column = InventoryPoliciesSheet.outbound_cost
        unit_column = InventoryPoliciesSheet.product_cost_basis
        extended_items = get_extended_items_with_value(
            self.data, inventory_indexes, group_members, [cost_column, unit_column]
        )
        outbound_costs: Dict[Tuple[Origin, Product], float] = {}
        for keys, values in extended_items.items():
            if values[unit_column] in UnitOfMeasureOptions.units_indexes:
                outbound_costs[(Origin(keys[0]), Product(keys[1]))] = float(
                    values[cost_column] * ratio_by_product[values[unit_column]][keys[1]]
                )
            else:
                outbound_costs[(Origin(keys[0]), Product(keys[1]))] = float(values[cost_column])

        return outbound_costs


class TransportationPoliciesTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        self.flows_cost: Dict[Tuple[Period, Origin, Destination, Mode, Product], float] = {}
        self.finished_product_nodes: Set[Tuple[Period, Site, Product]] = set()
        super(TransportationPoliciesTable, self).__init__(
            TransportationPoliciesSheet.sheet_name, TransportationPoliciesSheet(), data
        )
        self.columns: TransportationPoliciesSheet = TransportationPoliciesSheet()

    def get_production_and_intermediary_nodes(self) -> Set[Tuple[Period, Site, Product]]:
        if len(self.finished_product_nodes) == 0:
            finished_product_nodes: Set[Tuple[Period, Site, Product]] = set()
            for period, origin, destination, mode, product in self.flows_cost:
                finished_product_nodes.add((period, Site(origin), product))
                finished_product_nodes.add((period, Site(destination), product))

            self.finished_product_nodes = finished_product_nodes
            return self.finished_product_nodes
        else:
            return self.finished_product_nodes

    def get_extended_flows(
        self,
        group_members: pd.DataFrame,
    ) -> Dict[Tuple[Any, ...], Dict[str, Any]]:

        flow_columns = [
            self.columns.origin,
            self.columns.destination,
            self.columns.transportation_mode,
            self.columns.product,
        ]

        extended_flows: Dict[Tuple[Any, ...], Dict[str, Any]] = get_extended_items_with_value(
            self.data, flow_columns, group_members, [self.columns.cost, self.columns.product_cost_basis]
        )

        return extended_flows

    def get_origins(self) -> List[Origin]:
        flows = list(self.flows_cost)
        origins: List[Origin] = list(set(origin for _, origin, _, _, _ in flows))
        return origins
