from dataclasses import dataclass

from shared.tables.network_optimization_name_registry import NetworkOptimizationSheetNames, ProductsSheet
from shared.tables.global_name_registry import CommonColumnNames


@dataclass
class GroupsTypeOptions:
    site: str = NetworkOptimizationSheetNames.sites
    period: str = NetworkOptimizationSheetNames.periods
    product: str = NetworkOptimizationSheetNames.products
    transportation_mode: str = NetworkOptimizationSheetNames.transportation_modes
    type_by_index = {
        CommonColumnNames.product: product,
        CommonColumnNames.period: period,
        CommonColumnNames.mode: transportation_mode,
    }


@dataclass
class ConstraintsOptions:
    max: str = "Max"
    min: str = "Min"
    fixed: str = "Fixed"
    cond_min: str = "CondMin"
    define: str = "Define"


@dataclass
class ConstraintIndexTreatmentOptions:
    individual: str = "Individual"
    group: str = "Group"


@dataclass
class UnitOfMeasureOptions:
    alternative_unit1: str = ProductsSheet.alternative_unit1
    alternative_unit2: str = ProductsSheet.alternative_unit2
    default: str = "default"
    units_indexes = {alternative_unit1: 0, alternative_unit2: 1}


@dataclass
class ProductTypeOptions:

    component = "component"
    by_product = "byproduct"


@dataclass
class OptionsName:

    none = "None"


@dataclass
class GenericGroupsOptions:
    any_product = "ANY_PRODUCT"
    any_period = "ANY_PERIOD"
    any_mode = "ANY_MODE"
    any = "ANY"
    group_by_index = {
        CommonColumnNames.product: any_product,
        CommonColumnNames.period: any_period,
        CommonColumnNames.mode: any_mode,
    }
