from abc import abstractmethod, ABC

from services.common.user_input import GreenfieldUserInput


class SOCPModel(ABC):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)

    @abstractmethod
    def set_sets(self, data: GreenfieldUserInput) -> None:
        pass

    @abstractmethod
    def set_parameters(self, data: GreenfieldUserInput) -> None:
        pass
