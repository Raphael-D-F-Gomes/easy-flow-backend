from typing import Any, Dict, MutableMapping, TypeVar, overload, List, Set

from optimization_construction_api.opt_construction_function_names import OptConstructionFunctionName

from shared.logs.decorator import thread_log_decorator_function


KEYS_TYPE = TypeVar("KEYS_TYPE")
VALUES_TYPE = TypeVar("VALUES_TYPE")


class TupleSliceMetaClass(type):
    def __instancecheck__(cls, __instance: Any) -> bool:
        if not isinstance(__instance, tuple):
            return False
        return any(isinstance(k, slice) for k in __instance.__iter__())


class TupleSliceType(tuple, metaclass=TupleSliceMetaClass):
    pass


class OptimizedDict(dict, MutableMapping[KEYS_TYPE, VALUES_TYPE]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exploded_dict = {}
        self.indexes = []

    def optimize(self) -> List[Set[str]]:
        self.exploded_dict = {}
        index_sets: List[Set[str]] = []

        for i, (key, value) in enumerate(self.items()):
            current_dict = self.exploded_dict

            for index in range(len(key)):
                if i == 0:
                    index_sets.append({key[index]})
                else:
                    index_sets[index].add(key[index])
                if key[index] not in current_dict:
                    current_dict[key[index]] = {}
                current_dict = current_dict[key[index]]

            current_dict[key] = value

        return index_sets

    @overload
    def __getitem__(self, keys: TupleSliceType) -> Dict[Any, VALUES_TYPE]:
        ...

    @overload
    def __getitem__(self, keys: KEYS_TYPE) -> VALUES_TYPE:
        ...

    def __getitem__(self, keys):
        if isinstance(keys, TupleSliceType) or any((isinstance(key, set) or isinstance(key, list)) for key in keys):
            if all(isinstance(key, slice) for key in keys):
                return self.copy()

            if self.exploded_dict:
                filtered_dict = [self.exploded_dict.copy()]
                final_dict = {}
                for index, key in enumerate(keys):
                    current_dict = []
                    for dict_part in filtered_dict:
                        if isinstance(key, set) or isinstance(key, list):
                            indexes_set = set(dict_part.keys()).intersection(set(key))
                            for idx in indexes_set:
                                if index == len(keys) - 1:
                                    final_dict.update(dict_part[idx])
                                else:
                                    current_dict.append(dict_part[idx])

                        elif isinstance(key, slice):
                            if index == len(keys) - 1:
                                for value in dict_part.values():
                                    final_dict.update(value)
                            else:
                                current_dict += list(dict_part.values())

                        else:
                            value = dict_part.get(key, None)
                            if value is not None:

                                if index == len(keys) - 1:
                                    final_dict.update(value)
                                else:
                                    current_dict.append(value)

                    if len(current_dict) == 0 and len(final_dict) == 0:
                        return {}

                    filtered_dict = current_dict

                return final_dict

            else:
                return self.get_values_by_list_comprehension(keys)

        return self.get(keys, {})

    def get_values_by_list_comprehension(self, keys):
        values = [key for key in keys if not isinstance(key, slice)]
        filtered_values = {
            key: value for key, value in self.items() if all(
                key[keys.index(value)] in value if (isinstance(value, set) or isinstance(value, list))
                else key[keys.index(value)] == value for value in values
            )
        }

        return filtered_values


@thread_log_decorator_function(OptConstructionFunctionName().declare_variables)
def optimize_data(dict_to_be_optimized: Dict) -> OptimizedDict:
    optimized_dict = OptimizedDict(dict_to_be_optimized)
    optimized_dict.optimize()

    return optimized_dict


if __name__ == "__main__":
    d = {
        ("a", "d", "g"): 1,
        ("a", "d", "h"): 2,
        ("b", "d", "h"): 3,
        ("b", "e", "h"): 4,
        ("c", "f", "i"): 5,
        ("c", "f", "g"): 6,
    }
    d2 = OptimizedDict(d)
    print(d2.optimize())
    # d2.optimize_dict([0, 1, 2, 3])
    s = ["a", "b"]
    s2 = ["f", "e"]
    print(d2[:, s2, {"h", "i"}])
