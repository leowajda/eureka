from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from automation.utils import normalize_path

CATALOG_METADATA_FIELDS = ("name", "url", "difficulty", "categories")
APPROACH_ORDER = {"iterative": 0, "recursive": 1}


@dataclass(frozen=True, order=True)
class CatalogLanguage:
    name: str
    label: str
    code_language: str

    @classmethod
    def from_payload(cls, name: str, payload: Mapping[str, object]) -> Self:
        return cls(
            name=str(name),
            label=str(payload["label"]),
            code_language=str(payload["code_language"]),
        )

    def to_payload(self) -> dict[str, str]:
        return {
            "label": self.label,
            "code_language": self.code_language,
        }


@dataclass(frozen=True, order=True)
class ProblemImplementation:
    language: str
    approach: str
    source_url: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.language, self.approach)

    @property
    def sort_key(self) -> tuple[str, int, str]:
        return (self.language, APPROACH_ORDER.get(self.approach, 99), self.approach)


@dataclass(frozen=True)
class CatalogProblem:
    slug: str
    name: str
    url: str
    difficulty: str
    categories: tuple[str, ...]
    implementations: tuple[ProblemImplementation, ...] = field(default_factory=tuple)

    @classmethod
    def from_metadata(cls, metadata: ProblemMetadata) -> Self:
        return cls(
            slug=metadata.slug,
            name=metadata.name,
            url=metadata.url,
            difficulty=metadata.difficulty,
            categories=metadata.categories,
        )

    @classmethod
    def from_payload(cls, slug: str, payload: Mapping[str, object]) -> Self:
        missing_fields = [field_name for field_name in CATALOG_METADATA_FIELDS if field_name not in payload]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Problem '{slug}' is missing required fields: {missing}.")

        implementations: list[ProblemImplementation] = []
        for key, value in payload.items():
            if key in CATALOG_METADATA_FIELDS:
                continue
            if not isinstance(value, Mapping):
                raise TypeError(f"Problem '{slug}' language entry '{key}' must be a mapping of approaches.")
            for approach, source_url in value.items():
                implementations.append(
                    ProblemImplementation(
                        language=str(key),
                        approach=str(approach),
                        source_url=str(source_url),
                    )
                )

        return cls(
            slug=slug,
            name=str(payload["name"]),
            url=str(payload["url"]),
            difficulty=str(payload["difficulty"]),
            categories=_normalize_categories(payload["categories"]),
            implementations=_sort_implementations(implementations),
        )

    def with_implementation(self, implementation: ProblemImplementation) -> Self:
        implementation_map = {entry.key: entry for entry in self.implementations}
        if implementation.key in implementation_map:
            raise ValueError(
                f"Duplicate implementation detected for {self.slug} "
                f"({implementation.language}/{implementation.approach})."
            )
        implementation_map[implementation.key] = implementation
        return replace(self, implementations=_sort_implementations(implementation_map.values()))

    def without_source_url(self, source_url: str) -> Self | None:
        implementations = tuple(
            implementation
            for implementation in self.implementations
            if implementation.source_url != source_url
        )
        if len(implementations) == len(self.implementations):
            return self
        if not implementations:
            return None
        return replace(self, implementations=implementations)

    def to_payload(self, *, language_order: tuple[str, ...]) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "url": self.url,
            "difficulty": self.difficulty,
            "categories": list(self.categories),
        }

        implementations_by_language: dict[str, dict[str, str]] = {}
        for implementation in self.implementations:
            implementations = implementations_by_language.setdefault(implementation.language, {})
            implementations[implementation.approach] = implementation.source_url

        for language in language_order:
            implementations = implementations_by_language.get(language)
            if implementations:
                payload[language] = implementations
        return payload


@dataclass(frozen=True)
class GeneratedCatalog:
    languages: tuple[CatalogLanguage, ...]
    problems: tuple[CatalogProblem, ...]

    @classmethod
    def empty(cls) -> Self:
        return cls(languages=(), problems=())

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        languages_payload = payload.get("languages", {})
        problems_payload = payload.get("problems", {})

        if not isinstance(languages_payload, Mapping) or not isinstance(problems_payload, Mapping):
            raise TypeError("Generated catalog must contain 'languages' and 'problems' mappings.")

        languages = tuple(
            CatalogLanguage.from_payload(language, value)
            for language, value in languages_payload.items()
        )
        problems = tuple(
            sorted(
                (
                    CatalogProblem.from_payload(slug, value)
                    for slug, value in problems_payload.items()
                ),
                key=lambda problem: problem.slug,
            )
        )
        return cls(languages=languages, problems=problems)

    @property
    def language_order(self) -> tuple[str, ...]:
        return tuple(language.name for language in self.languages)

    def to_payload(self) -> dict[str, object]:
        return {
            "languages": {
                language.name: language.to_payload()
                for language in self.languages
            },
            "problems": {
                problem.slug: problem.to_payload(language_order=self.language_order)
                for problem in self.problems
            },
        }


class LanguageTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    language: str = Field(min_length=1)
    label: str = Field(min_length=1)
    code_language: str = Field(min_length=1)
    path_prefix: str = Field(min_length=1)
    path_glob: str = Field(min_length=1)

    @field_validator("path_prefix", "path_glob")
    @classmethod
    def normalize_path_field(cls, value: str) -> str:
        return normalize_path(value)

    def matches(self, file_path: str) -> bool:
        from fnmatch import fnmatchcase

        normalized = normalize_path(file_path)
        return normalized.startswith(f"{self.path_prefix}/") and fnmatchcase(normalized, self.path_glob)

    def source_url(self, source_url_base: str, file_path: str) -> str:
        return f"{source_url_base.rstrip('/')}/{normalize_path(file_path)}"

    def catalog_language(self) -> CatalogLanguage:
        return CatalogLanguage(
            name=self.language,
            label=self.label,
            code_language=self.code_language,
        )


class ProblemMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    difficulty: str = ""
    categories: tuple[str, ...] = ()

    @field_validator("categories", mode="before")
    @classmethod
    def normalize_categories(cls, value: object) -> tuple[str, ...]:
        return _normalize_categories(value)

    @property
    def url(self) -> str:
        return f"https://leetcode.com/problems/{self.slug}"

    @classmethod
    def from_problem(cls, problem: CatalogProblem) -> Self:
        return cls(
            slug=problem.slug,
            name=problem.name,
            difficulty=problem.difficulty,
            categories=problem.categories,
        )


class TargetsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    targets: tuple[LanguageTarget, ...]

    @model_validator(mode="after")
    def validate_uniqueness(self) -> Self:
        languages = [target.language for target in self.targets]
        prefixes = [target.path_prefix for target in self.targets]
        if len(languages) != len(set(languages)):
            raise ValueError("Duplicate languages detected in targets configuration.")
        if len(prefixes) != len(set(prefixes)):
            raise ValueError("Duplicate path prefixes detected in targets configuration.")
        return self


@dataclass(frozen=True)
class SolutionCommit:
    file_path: str
    language: str
    approach: str
    slug: str
    source_url: str


def _normalize_categories(value: object) -> tuple[str, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    raise TypeError("Problem categories must be a string or a list of strings.")


def _sort_implementations(
    implementations: Iterable[ProblemImplementation],
) -> tuple[ProblemImplementation, ...]:
    return tuple(sorted(implementations, key=lambda implementation: implementation.sort_key))
