from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ForgeCycleInputModel")


@_attrs_define
class ForgeCycleInputModel:
    """
    Attributes:
        forge_description (Union[None, Unset, str]):
        forge_name (Union[None, Unset, str]):
        n_agents_in_population (Union[Unset, int]):
        n_selected_agents_from_ecosystem (Union[Unset, int]):
        n_best_agents_to_return (Union[Unset, int]):
        replacement_ratio (Union[Unset, float]):
        tournament_size_ratio (Union[Unset, float]):
        local_results_path (Union[None, Unset, str]):
        budget (Union[Unset, float]):
    """

    forge_description: Union[None, Unset, str] = UNSET
    forge_name: Union[None, Unset, str] = UNSET
    n_agents_in_population: Union[Unset, int] = UNSET
    n_selected_agents_from_ecosystem: Union[Unset, int] = UNSET
    n_best_agents_to_return: Union[Unset, int] = UNSET
    replacement_ratio: Union[Unset, float] = UNSET
    tournament_size_ratio: Union[Unset, float] = UNSET
    local_results_path: Union[None, Unset, str] = UNSET
    budget: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        forge_description: Union[None, Unset, str]
        if isinstance(self.forge_description, Unset):
            forge_description = UNSET
        else:
            forge_description = self.forge_description

        forge_name: Union[None, Unset, str]
        if isinstance(self.forge_name, Unset):
            forge_name = UNSET
        else:
            forge_name = self.forge_name

        n_agents_in_population = self.n_agents_in_population

        n_selected_agents_from_ecosystem = self.n_selected_agents_from_ecosystem

        n_best_agents_to_return = self.n_best_agents_to_return

        replacement_ratio = self.replacement_ratio

        tournament_size_ratio = self.tournament_size_ratio

        local_results_path: Union[None, Unset, str]
        if isinstance(self.local_results_path, Unset):
            local_results_path = UNSET
        else:
            local_results_path = self.local_results_path

        budget = self.budget

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if forge_description is not UNSET:
            field_dict["forgeDescription"] = forge_description
        if forge_name is not UNSET:
            field_dict["forgeName"] = forge_name
        if n_agents_in_population is not UNSET:
            field_dict["nAgentsInPopulation"] = n_agents_in_population
        if n_selected_agents_from_ecosystem is not UNSET:
            field_dict["nSelectedAgentsFromEcosystem"] = n_selected_agents_from_ecosystem
        if n_best_agents_to_return is not UNSET:
            field_dict["nBestAgentsToReturn"] = n_best_agents_to_return
        if replacement_ratio is not UNSET:
            field_dict["replacementRatio"] = replacement_ratio
        if tournament_size_ratio is not UNSET:
            field_dict["tournamentSizeRatio"] = tournament_size_ratio
        if local_results_path is not UNSET:
            field_dict["localResultsPath"] = local_results_path
        if budget is not UNSET:
            field_dict["budget"] = budget

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_forge_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        forge_description = _parse_forge_description(d.pop("forgeDescription", UNSET))

        def _parse_forge_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        forge_name = _parse_forge_name(d.pop("forgeName", UNSET))

        n_agents_in_population = d.pop("nAgentsInPopulation", UNSET)

        n_selected_agents_from_ecosystem = d.pop("nSelectedAgentsFromEcosystem", UNSET)

        n_best_agents_to_return = d.pop("nBestAgentsToReturn", UNSET)

        replacement_ratio = d.pop("replacementRatio", UNSET)

        tournament_size_ratio = d.pop("tournamentSizeRatio", UNSET)

        def _parse_local_results_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        local_results_path = _parse_local_results_path(d.pop("localResultsPath", UNSET))

        budget = d.pop("budget", UNSET)

        forge_cycle_input_model = cls(
            forge_description=forge_description,
            forge_name=forge_name,
            n_agents_in_population=n_agents_in_population,
            n_selected_agents_from_ecosystem=n_selected_agents_from_ecosystem,
            n_best_agents_to_return=n_best_agents_to_return,
            replacement_ratio=replacement_ratio,
            tournament_size_ratio=tournament_size_ratio,
            local_results_path=local_results_path,
            budget=budget,
        )

        return forge_cycle_input_model
