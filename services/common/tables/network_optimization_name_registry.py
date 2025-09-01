from dataclasses import dataclass

from shared.tables.global_name_registry import InputSheet
from shared.tables.global_name_registry import CommonColumnNames

NO_REQUIRED_TABLES = [
    "sites",
    "demand",
    "transportationPolicies",
    "products",
    "transportationModes",
    "periods",
    "productionPolicies",
]


@dataclass
class NetworkOptimizationSheetNames:
    sites: str = "sites"
    flows: str = "flows"
    summary: str = "summary"
    network_flows: str = "networkFlows"
    expression_cost_summary: str = "expressionCostSummary"
    production_summary: str = "productionSummary"

    transportation_modes: str = "transportationModes"
    products: str = "products"
    transportation_policies: str = "transportationPolicies"
    production_policies: str = "productionPolicies"
    groups: str = "groups"
    group_members: str = "groupMembers"
    periods: str = "periods"
    step_cost_definitions: str = "stepCostDefinitions"
    step_cost: str = "stepCost"
    units_of_measure: str = "unitsOfMeasure"
    no_scenarios: str = "networkOptimizationScenarios"
    flow_constraints: str = "flowConstraints"
    inventory_policies: str = "inventoryPolicies"
    expression_constraints: str = "expressionConstraints"
    expression_based_costs: str = "expressionBasedCosts"
    scenario_items: str = "scenarioItems"
    scenarios: str = "scenarios"
    run_config: str = "runConfig"
    site_constraints: str = "siteConstraints"
    production_constraints: str = "productionConstraints"
    bill_of_materials: str = "billOfMaterials"


@dataclass
class TransportationModeSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.transportation_modes

    mode_id: str = "transportationModeID"
    name: str = "name"
    mode: str = "mode"
    mode_type = "type"


@dataclass
class ProductsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.products

    product_id: str = "productID"
    name: str = "name"
    type: str = "type"
    alternative_unit1: str = "uomAlt1"
    alternative_unit2: str = "uomAlt2"


@dataclass
class TransportationPoliciesSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.transportation_policies

    origin: str = "origin"
    destination: str = "destination"
    product: str = CommonColumnNames.product
    transportation_mode: str = CommonColumnNames.mode
    cost: str = "cost"
    product_cost_basis: str = "productCostBasis"
    distance: str = "distance"
    flow_id: str = "flow_id"


@dataclass
class NetworkOptimizationScenariosSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.no_scenarios

    type: str = "type"
    status: str = CommonColumnNames.status
    scenario: str = "scenarioID"
    include: str = "include"


@dataclass
class ProductionPoliciesSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.production_policies

    period: str = CommonColumnNames.period
    location: str = CommonColumnNames.site
    product: str = CommonColumnNames.product
    production_variable_cost: str = "variableProductionCost"
    production_cost_basis: str = "variableCostBasis"
    production_fixed_step_cost: str = "fixedProductionStepCost"
    bom_name: str = "bomName"


@dataclass
class GroupsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.groups

    name: str = "name"
    group_id: str = "groupID"
    type: str = "type"


@dataclass
class GroupMembersSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.group_members

    name: str = "name"
    group_id: str = "group"
    member: str = "groupMember"


@dataclass
class PeriodsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.periods

    period: str = "periodID"
    name: str = "name"
    initial_date: str = "initialDate"


@dataclass
class StepCostDefinitionsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.step_cost_definitions

    name: str = "stepCostName"
    step_cost_id: str = "stepCostID"
    unit_of_measure: str = "unitOfMeasure"
    type: str = "type"


@dataclass
class StepCostSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.step_cost

    name: str = "stepCostName"
    step_cost_id: str = "stepCost"
    step: str = "step"
    capacity: str = "capacity"
    cost: str = "cost"


@dataclass
class UnitsOfMeasureSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.units_of_measure

    name: str = "unitOfMeasureName"
    unit_id: str = "unitOfMeasureID"
    description: str = "description"
    ratio: str = "ratio"
    type: str = "type"


@dataclass
class FlowConstraintsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.flow_constraints

    flow_constraint_name: str = "flowConstraintName"
    period: str = CommonColumnNames.period
    treat_period_as: str = "treatPeriodAs"
    origin: str = TransportationPoliciesSheet.origin
    treat_origin_as: str = "treatOriginAs"
    destination: str = TransportationPoliciesSheet.destination
    treat_destination_as: str = "treatDestinationAs"
    product: str = CommonColumnNames.product
    treat_product_as: str = "treatProductAs"
    transportation_mode: str = TransportationPoliciesSheet.transportation_mode
    treat_mode_as: str = "treatTransportationModeAs"
    constraint_type: str = "constraintType"
    value: str = "value"
    treatment_columns = {
        treat_period_as: period,
        treat_origin_as: origin,
        treat_destination_as: destination,
        treat_mode_as: transportation_mode,
        treat_product_as: product,
    }
    obligatory_columns = [
        flow_constraint_name,
        period,
        treat_period_as,
        origin,
        treat_origin_as,
        destination,
        treat_destination_as,
        product,
        treat_product_as,
        transportation_mode,
        treat_mode_as,
        constraint_type,
        value,
    ]
    taxes_related_columns = [
        "type",
        "category",
        "originState",
        "destinationState",
        "originType",
        "destinationType",
        "PC_Mono",
        "Portaria195",
        "I01",
        "I02",
        "I03",
        "I04",
        "I05",
        "PrecoLiquido",
        "AliqIPI",
        "AliqICMS",
        "AliqPC",
        "BaseCalculoPC",
        "BaseCalculoICMS",
        "ValorIPI",
        "ValorICMS",
        "ValorPC",
        "PrecoComIPI",
        "IncideST",
        "MVA",
        "AliqICMSInternaST",
        "BaseCalculoST",
        "ValorST",
        "ValorNF",
        "F01",
        "F02",
        "F03",
        "F04",
        "F05",
    ]


@dataclass
class SiteConstraintsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.site_constraints

    site_constraint_name: str = "siteConstraintName"
    period: str = CommonColumnNames.period
    treat_period_as: str = "treatPeriodAs"
    site: str = "site"
    treat_site_as: str = "treatSiteAs"
    constraint_type: str = "constraintType"
    value: str = "value"
    treatment_columns = {
        treat_period_as: period,
        treat_site_as: site,
    }


@dataclass
class ExpressionBasedCostSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.expression_based_costs

    name: str = "expressionCostName"
    expression: str = "expression"
    variable_cost: str = "variableCost"
    notes: str = "notes"
    value: str = "value"


@dataclass
class ProductionConstraintsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.production_constraints

    production_constraint_name: str = "productionConstraintName"
    period: str = CommonColumnNames.period
    treat_period_as: str = "treatPeriodAs"
    site: str = CommonColumnNames.site
    treat_site_as: str = "treatSiteAs"
    product: str = CommonColumnNames.product
    treat_product_as: str = "treatProductAs"
    constraint_type: str = "constraintType"
    value: str = "value"
    treatment_columns = {
        treat_period_as: period,
        treat_site_as: site,
        treat_product_as: product,
    }


@dataclass
class ExpressionConstraintsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.expression_constraints

    expression_constraint_name: str = "expressionConstraintName"
    coefficient1: str = "coefficient1"
    expression1: str = "expression1"
    coefficient2: str = "coefficient2"
    expression2: str = "expression2"
    constraint_type: str = "constraintType"
    value: str = "value"


@dataclass
class InventoryPoliciesSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.inventory_policies

    location: str = CommonColumnNames.site
    product: str = CommonColumnNames.product
    outbound_cost: str = "outboundCost"
    product_cost_basis: str = "productCostBasis"


@dataclass
class BillOfMaterialsSheet(InputSheet):

    sheet_name: str = NetworkOptimizationSheetNames.bill_of_materials

    bom_name: str = "bomName"
    product: str = CommonColumnNames.product
    product_type: str = "productType"
    quantity: str = "quantity"
    quantity_uom: str = "quantityUOM"
