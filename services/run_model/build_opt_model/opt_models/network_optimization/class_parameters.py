from dataclasses import dataclass


from shared.utils.optimized_dictionary import OptimizedDict


@dataclass
class OptimizedVariables:
    flow_variables: OptimizedDict
    total_production: OptimizedDict
    production_binary_variables: OptimizedDict
    open_variables: OptimizedDict
