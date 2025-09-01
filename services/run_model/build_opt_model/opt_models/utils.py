import os
import tempfile
from typing import Iterable

from pulp import LpAffineExpression, LpConstraint, LpProblem


class MILPOutput:
    @staticmethod
    def write_model(objective: LpAffineExpression, constraints: Iterable[LpConstraint]) -> str:
        model = LpProblem()
        for constraint in constraints:
            model.addConstraint(constraint)

        model.setObjective(objective)

        file_path = os.path.join(tempfile.mkdtemp(), "model.mps")
        model.writeMPS(file_path)
        return file_path
