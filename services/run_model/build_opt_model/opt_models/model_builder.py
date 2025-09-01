from abc import abstractmethod, ABC

from services.common.user_input import GreenfieldUserInput


class ModelBuilder(ABC):
    @abstractmethod
    def build_model(self, user_input: GreenfieldUserInput) -> str:
        pass
