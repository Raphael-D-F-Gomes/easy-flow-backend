from typing import Dict, Tuple, List, Any, Set
from itertools import product as prod

import numpy as np
import pandas as pd

from optimization_construction_api.etl.types import Product, Period, Unit, BOMName, StepID, Step, Ratio, Site
from optimization_construction_api.etl.user_input.tables import NetworkOptimizationTable
from shared.tables.network_optimization_name_registry import (
    ProductionPoliciesSheet,
    BillOfMaterialsSheet,
    StepCostSheet,
)
from optimization_construction_api.etl.user_input.tables.auxiliary_classes import AuxiliaryInfo
from shared.utils.group_features import get_extended_items_with_value


class ProductionPoliciesTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        self.production_variable_cost: Dict[Tuple[Period, Site, Product], float] = {}
        self.production_sites_with_bom: Dict[Tuple[Period, Site, Product], BOMName] = {}
        self.production_step_info: Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, Any]] = {}
        self.raw_product_nodes: Set[Tuple[Period, Site, Product]] = set()
        super(ProductionPoliciesTable, self).__init__(
            ProductionPoliciesSheet.sheet_name, ProductionPoliciesSheet(), data
        )

    def construct_production_cost_info(
            self,
            group_members: pd.DataFrame,
            periods: List[Period],
            auxiliary_info: AuxiliaryInfo
    ) -> None:
        if len(self.production_step_info) > 0:
            return None

        production_indexes = [ProductionPoliciesSheet.location, ProductionPoliciesSheet.product]
        components_from_bom = auxiliary_info.components_from_bom
        extended_production = get_extended_items_with_value(
            self.data,
            production_indexes,
            group_members,
            [
                ProductionPoliciesSheet.production_variable_cost,
                ProductionPoliciesSheet.production_fixed_step_cost,
                ProductionPoliciesSheet.production_cost_basis,
                ProductionPoliciesSheet.bom_name,
            ]
        )
        production_variable_cost: Dict[Tuple[Period, Site, Product], float] = {}
        production_step_info: Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, Any]] = {}
        for period, production in prod(periods, extended_production):
            bom_name = extended_production[production][ProductionPoliciesSheet.bom_name]
            self.production_sites_with_bom[(period, production[0], production[1])] = bom_name
            if pd.notna(bom_name):
                self.raw_product_nodes.union(
                    self.get_nodes_from_bom_with_raw_product(components_from_bom, bom_name, period, production[1])
                )
            production_variable_cost.update(self.update_production_variable_cost_dict(
                extended_production,
                (Period(period), Site(production[0]), Product(production[1])),
                auxiliary_info.ratio_by_product,
            ))
            production_step_info.update(self.update_production_fixed_step_cost_dict(
                auxiliary_info,
                extended_production,
                (Period(period), Site(production[0]), Product(production[1])),
            ))

        self.production_variable_cost = production_variable_cost
        self.production_step_info = production_step_info

    @staticmethod
    def get_nodes_from_bom_with_raw_product(
            components_from_bom: Dict[BOMName, List[Product]],
            bom_name: BOMName,
            period: Period,
            site: Site,
    ) -> Set[Tuple[Period, Site, Product]]:
        nodes: Set[Tuple[Period, Site, Product]] = set()
        for product in components_from_bom[bom_name]:
            nodes.add((period, site, product))

        return nodes

    def get_raw_product_nodes(self) -> Set[Tuple[Period, Site, Product]]:
        return self.raw_product_nodes

    @staticmethod
    def update_production_variable_cost_dict(
            extended_production: Dict[Tuple[Any, ...], Dict[str, Any]],
            production_indexes: Tuple[Period, Site, Product],
            ratio_by_product: Dict[Unit, Dict[Product, float]],
    ) -> Dict[Tuple[Period, Site, Product], float]:
        production_variable_cost: Dict[Tuple[Period, Site, Product], float] = {}
        period, origin, product = production_indexes
        unit_of_measure = extended_production[(origin, product)][ProductionPoliciesSheet.production_cost_basis]
        variable_cost = extended_production[(origin, product)][ProductionPoliciesSheet.production_variable_cost]
        if not pd.isna(variable_cost):
            if pd.isna(unit_of_measure):
                ratio = 1
            else:
                ratio = ratio_by_product[unit_of_measure][product]
            production_variable_cost[
                period, origin, product
            ] = extended_production[(origin, product)][ProductionPoliciesSheet.production_variable_cost] * ratio

        return production_variable_cost

    @staticmethod
    def update_production_fixed_step_cost_dict(
            auxiliary_info: AuxiliaryInfo,
            extended_production: Dict[Tuple[Any, ...], Dict[str, Any]],
            production_indexes: Tuple[Period, Site, Product],
    ) -> Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, Any]]:
        step_info = auxiliary_info.step_info
        unit_by_step = auxiliary_info.unit_by_step
        ratio_by_product = auxiliary_info.ratio_by_product
        period, origin, product = production_indexes
        production_step_info: Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, Any]] = {}
        step_id = extended_production[(origin, product)][ProductionPoliciesSheet.production_fixed_step_cost]
        if not pd.isna(step_id):
            for step, step_values in step_info[step_id].items():
                unit = unit_by_step.get(step_id, None)
                if unit is None:
                    ratio = 1
                else:
                    ratio = ratio_by_product.get(unit, {})[product]

                capacity = step_values[StepCostSheet.capacity]
                if not pd.isna(capacity):
                    capacity /= ratio
                production_step_info[
                    period, origin, product, StepID(step_id), Step(step)
                ] = {
                    StepCostSheet.capacity: capacity,
                    StepCostSheet.cost: step_values[StepCostSheet.cost]
                }

        return production_step_info

    def get_production_sites_with_bom(
            self
    ) -> Dict[Tuple[Period, Site, Product], BOMName]:
        """
        This method must be called after construct_production_cost_info
        """
        return self.production_sites_with_bom

    def get_production_variable_cost(
            self
    ) -> Dict[Tuple[Period, Site, Product], float]:
        """
        This method must be called after construct_production_cost_info
        """
        return self.production_variable_cost

    def get_production_fixed_step_cost_info(
            self
    ) -> Dict[Tuple[Period, Site, Product, StepID, Step], Dict[str, Any]]:
        """
        This method must be called after construct_production_cost_info
        """
        return self.production_step_info

    def get_production_policies_boms(self) -> Set[BOMName]:
        boms: Set[BOMName] = set(self.data[ProductionPoliciesSheet.bom_name].dropna().unique())
        return boms


class BillOfMaterialsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(BillOfMaterialsTable, self).__init__(
            BillOfMaterialsSheet.sheet_name, BillOfMaterialsSheet(), data
        )

    def get_bom_with_quantity_by_unit(
            self,
            ratio_by_unit: Dict[Unit, Dict[Product, Ratio]],
    ) -> pd.DataFrame:
        bill_of_materials = self.data.copy()
        if self.data.empty:
            return self.data

        bill_of_materials[BillOfMaterialsSheet.quantity] /= np.array([
            ratio_by_unit.get(
                bill_of_materials[BillOfMaterialsSheet.quantity_uom][i], {}
            ).get(
                bill_of_materials[BillOfMaterialsSheet.product][i], 1
            ) for i in bill_of_materials.index
        ])
        return bill_of_materials

    def get_components_from_bom(self) -> Dict[BOMName, List[Product]]:
        if self.data.empty:
            return {}
        components_from_bom: Dict[BOMName, List[Product]] = self.data.groupby(
            BillOfMaterialsSheet.bom_name
        )[BillOfMaterialsSheet.product].apply(list).to_dict()
        return components_from_bom

    def get_highest_quantity_between_boms(
            self,
            boms: Set[BOMName],
            ratio_by_product: Dict[Unit, Dict[Product, Ratio]],
    ) -> float:
        columns = [BillOfMaterialsSheet.product, BillOfMaterialsSheet.quantity, BillOfMaterialsSheet.quantity_uom]
        highest_quantity: float = max(
            quantity / ratio_by_product.get(unit, {}).get(product, 1)
            for product, quantity, unit in self.data[
                self.data[BillOfMaterialsSheet.bom_name].isin(boms)
            ][columns].itertuples(index=False, name=None)
        )
        return highest_quantity
