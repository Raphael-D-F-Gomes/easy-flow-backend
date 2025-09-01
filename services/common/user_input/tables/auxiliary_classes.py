from typing import Dict, List

from dataclasses import dataclass

from optimization_construction_api.etl.types import StepID, Step, Product, Unit, Ratio, BOMName


@dataclass
class AuxiliaryInfo:
    step_info: Dict[StepID, Dict[Step, Dict[str, float]]]
    unit_by_step: Dict[StepID, Unit]
    ratio_by_product: Dict[Unit, Dict[Product, Ratio]]
    components_from_bom: Dict[BOMName, List[Product]]
