from dataclasses import dataclass


@dataclass
class GFAObjectiveOptions:
    min_total_weighted_distances_fixed_n_facilities = "1. Minimize the total weighted distance based in a fixed" \
                                                      " quantity of facilities"
    min_total_weighted_distances_and_n_facilities = "2. Minimize the quantity of facilities based in service distances"


@dataclass
class SitesCandidatesGenerationOptions:
    include: str = "Include"
    exclude: str = "Exclude"
    consider: str = "Consider"


@dataclass
class CandidatesGenerationOptions:
    from_existing_nodes: str = "fromexistingnodes"
    new_coordinates: str = "newcoordinates"


@dataclass
class ServDistOptions:
    cumulative: str = "cumulative"
    absolute: str = "absolute"


@dataclass
class OptionsName:

    none = "None"

    # chainedExecution
    backwards_execution = "Backwards"
    forward_execution = "Forward"
    forward_fixed_execution = "Forward Fixed"


@dataclass
class ChainedExecutionOptions:
    backwards_execution = "backwards"
    forward_execution = "forward"
    forward_fixed_execution = "forwardfixed"
    none = "none"


@dataclass
class DistanceOptions:
    real: str = "real"
    geodesic: str = "geodesic"
    euclidean: str = "euclidean"


@dataclass
class FacilityTypes:
    included_facility: str = "Included Facility"
    greenfield_facility: str = "Greenfield Facility"
