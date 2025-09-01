from typing import List, Tuple, Dict, Any, Union

import pandas as pd
from itertools import product as iter_prod

from shared.tables.greenfield_name_registry import (
    ColumnName,
)
from shared.tables.network_optimization_name_registry import GroupMembersSheet, GroupsSheet, ProductionPoliciesSheet, \
    TransportationPoliciesSheet, FlowConstraintsSheet, InventoryPoliciesSheet, ProductsSheet, TransportationModeSheet, \
    PeriodsSheet
from shared.tables.network_optimization_options import GenericGroupsOptions, GroupsTypeOptions
from shared.tables.global_options import StatusOptions
from shared.tables.global_name_registry import CommonColumnNames


def get_extended_items(
    dataframe: pd.DataFrame, index_columns: List[str], group_members: pd.DataFrame
) -> List[Tuple[Any, ...]]:
    try:
        items = list(
            dataframe[dataframe[ColumnName.status] == StatusOptions.include][
                index_columns
            ].itertuples(name=None, index=False)
        )
    except IndexError:
        return []

    if GroupMembersSheet.group_id not in group_members.columns or GroupMembersSheet.member not in group_members.columns:
        return items
    members_by_group = group_members.groupby(GroupMembersSheet.group_id)[GroupMembersSheet.member].apply(list).to_dict()
    extended_items = []

    for row in items:
        possibilities = []
        for index in row:
            if index in members_by_group:
                possibilities.append(members_by_group[index])
            else:
                possibilities.append([index])

        extended_items += list(iter_prod(*tuple(possibilities)))

    return extended_items


def get_extended_items_with_value(
    dataframe: pd.DataFrame,
    index_columns: List[str],
    group_members: pd.DataFrame,
    column_values: List[str] = None
) -> Dict[Tuple[Any, ...], Dict[str, Any]]:
    try:
        items = list(dataframe[index_columns + column_values].itertuples(name=None, index=False))
    except IndexError:
        return {}

    if GroupMembersSheet.group_id not in group_members.columns or GroupMembersSheet.member not in group_members.columns:
        return {
            tuple(list(row)[:-(len(column_values))]): {
                column_values[-i-1]: row[-i-1] for i in range(len(column_values))
            } for row in items}
    members_by_group = group_members.groupby(GroupMembersSheet.group_id)[GroupMembersSheet.member].apply(list).to_dict()
    extended_items = {}

    for row in items:
        possibilities = []
        for index in row[:-len(column_values)]:
            if index in members_by_group:
                possibilities.append(members_by_group[index])
            else:
                possibilities.append([index])

        extended_items.update({combination: {
            column_values[-i-1]: row[-i-1] for i in range(len(column_values))
        } for combination in list(iter_prod(*tuple(possibilities)))})

    return extended_items


def get_generic_groups(
        indexes: Dict[str, List[str]],
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    group_members_id = []
    members = []
    groups_id = []
    types = []

    for index, references in indexes.items():
        group_members_id += [GenericGroupsOptions.group_by_index[index]] * len(references)
        members += references
        groups_id += [GenericGroupsOptions.group_by_index[index]]
        types += [GroupsTypeOptions.type_by_index[index]]

    generic_group_members = {
        GroupMembersSheet.group_id: group_members_id,
        GroupMembersSheet.member: members,
    }
    generic_groups = {
        GroupsSheet.group_id: groups_id,
        GroupsSheet.type: types,
        GroupsSheet.status: [StatusOptions.include] * len(types),
    }

    return pd.DataFrame(generic_groups), pd.DataFrame(generic_group_members)


def change_generic_group_key(
        dataframe: pd.DataFrame,
        columns: List[str],
        generic_groups: Union[List[str], None] = None
) -> pd.DataFrame:
    if generic_groups is None:
        generic_groups = [None] * len(columns)
    for column, group in zip(columns, generic_groups):
        if group is None:
            dataframe.loc[
                dataframe[column].str.upper().str.strip() == GenericGroupsOptions.any, column
            ] = GenericGroupsOptions.group_by_index[column]
        else:
            dataframe.loc[
                dataframe[column].str.upper().str.strip() == GenericGroupsOptions.any, column
            ] = group
    return dataframe


def format_generic_groups(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    transportation_policies = tables.get(TransportationPoliciesSheet.sheet_name, None)
    production_policies = tables.get(ProductionPoliciesSheet.sheet_name, None)
    inventory_policies = tables.get(InventoryPoliciesSheet.sheet_name, None)
    flow_constraints = tables.get(FlowConstraintsSheet.sheet_name, None)
    if transportation_policies is not None:
        columns = TransportationPoliciesSheet().columns
        tables[TransportationPoliciesSheet.sheet_name] = change_generic_group_key(
            transportation_policies,
            [columns.product, columns.transportation_mode],
            [GenericGroupsOptions.any_product, GenericGroupsOptions.any_mode],
        )
    if production_policies is not None:
        columns = ProductionPoliciesSheet().columns
        tables[ProductionPoliciesSheet.sheet_name] = change_generic_group_key(
            production_policies, [columns.product], [GenericGroupsOptions.any_product]
        )
    if inventory_policies is not None:
        columns = InventoryPoliciesSheet().columns
        tables[InventoryPoliciesSheet.sheet_name] = change_generic_group_key(
            inventory_policies, [columns.product], [GenericGroupsOptions.any_product]
        )
    if flow_constraints is not None:
        columns = FlowConstraintsSheet().columns
        tables[FlowConstraintsSheet.sheet_name] = change_generic_group_key(
            flow_constraints,
            [columns.origin, columns.destination, columns.product, columns.transportation_mode],
            [GenericGroupsOptions.any] * 4,
        )
    return tables


def get_extended_rows_due_groups(
        reference_table: pd.DataFrame,
        group_members: pd.DataFrame,
        indexes: Dict[str, List[str]],
        index_columns: List[str],
) -> List[Tuple[Any, ...]]:

    _, generic_groups = get_generic_groups(indexes)
    all_groups = pd.concat([group_members, generic_groups])

    dataframe = reference_table.copy()
    dataframe = change_generic_group_key(dataframe, list(indexes))

    extended_flows: List[Tuple[Any, ...]] = get_extended_items(dataframe, index_columns, all_groups)

    return extended_flows


def get_extended_rows_due_groups_with_value(
        reference_table: pd.DataFrame,
        group_members: pd.DataFrame,
        indexes: Dict[str, List[str]],
        index_columns: List[str],
        column_value: str
) -> Dict[Tuple[Any, ...], Dict[str, Any]]:

    _, generic_groups = get_generic_groups(indexes)
    all_groups = pd.concat([group_members, generic_groups])

    dataframe = reference_table.copy()
    dataframe = change_generic_group_key(dataframe, list(indexes))

    extended_flows = get_extended_items_with_value(
        dataframe,
        index_columns,
        all_groups,
        [column_value]
    )

    return extended_flows


def add_generic_groups_in_validated_input(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    group_members = tables.get(GroupMembersSheet.sheet_name, None)
    groups = tables.get(GroupsSheet.sheet_name, None)
    products_table = tables.get(ProductsSheet.sheet_name, None)
    modes_table = tables.get(TransportationModeSheet.sheet_name, None)
    periods_table = tables.get(PeriodsSheet.sheet_name, None)
    if any(table is None for table in [products_table, modes_table, periods_table]):
        return tables

    products = products_table[ProductsSheet.product_id].tolist()
    modes = modes_table[TransportationModeSheet.mode_id].tolist()
    periods = periods_table[PeriodsSheet.period].tolist()
    generic_groups, generic_group_members = get_generic_groups(
        {
            CommonColumnNames.product: products,
            CommonColumnNames.mode: modes,
            CommonColumnNames.period: periods,
        }
    )
    if group_members is None:
        tables[GroupMembersSheet.sheet_name] = generic_group_members
    else:
        tables[GroupMembersSheet.sheet_name] = pd.concat([group_members, generic_group_members])

    if groups is None:
        tables[GroupsSheet.sheet_name] = generic_groups
    else:
        tables[GroupsSheet.sheet_name] = pd.concat([groups, generic_groups])

    tables[GroupMembersSheet.sheet_name].reset_index(drop=True, inplace=True)
    tables[GroupsSheet.sheet_name].reset_index(drop=True, inplace=True)

    return tables
