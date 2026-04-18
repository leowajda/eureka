from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from automation.utils import normalize_path

CATALOG_VERSION = 2
IMPLEMENTATION_FIELDS = ("language", "approach", "file_path")
PROBLEM_METADATA_FIELDS = ("name", "url", "difficulty", "categories", "implementations")
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
    file_path: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        missing_fields = [field_name for field_name in IMPLEMENTATION_FIELDS if field_name not in payload]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Implementation entry is missing required fields: {missing}.")

        return cls(
            language=str(payload["language"]),
            approach=str(payload["approach"]),
            file_path=normalize_path(str(payload["file_path"])),
        )

    def to_payload(self) -> dict[str, str]:
        return {
            "language": self.language,
            "approach": self.approach,
            "file_path": self.file_path,
        }

    @property
    def key(self) -> tuple[str, str]:
        return (self.language, self.approach)

    @property
    def sort_key(self) -> tuple[str, int, str, str]:
        return (self.language, APPROACH_ORDER.get(self.approach, 99), self.approach, self.file_path)


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
        missing_fields = [field_name for field_name in PROBLEM_METADATA_FIELDS if field_name not in payload]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Problem '{slug}' is missing required fields: {missing}.")

        implementations_payload = payload["implementations"]
        if not isinstance(implementations_payload, Iterable) or isinstance(
            implementations_payload,
            (str, bytes, Mapping),
        ):
            raise TypeError(f"Problem '{slug}' implementations must be a list of mappings.")

        implementations = [
            ProblemImplementation.from_payload(implementation)
            for implementation in implementations_payload
        ]

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

    def without_file_path(self, file_path: str) -> Self | None:
        implementations = tuple(
            implementation
            for implementation in self.implementations
            if implementation.file_path != normalize_path(file_path)
        )
        if len(implementations) == len(self.implementations):
            return self
        if not implementations:
            return None
        return replace(self, implementations=implementations)

    def to_payload(self, *, language_order: tuple[str, ...]) -> dict[str, object]:
        language_index = {language: index for index, language in enumerate(language_order)}
        payload: dict[str, object] = {
            "name": self.name,
            "url": self.url,
            "difficulty": self.difficulty,
            "categories": list(self.categories),
            "implementations": [
                implementation.to_payload()
                for implementation in sorted(
                    self.implementations,
                    key=lambda implementation: (
                        language_index.get(implementation.language, len(language_index)),
                        APPROACH_ORDER.get(implementation.approach, 99),
                        implementation.approach,
                        implementation.file_path,
                    ),
                )
            ],
        }
        return payload


@dataclass(frozen=True)
class GeneratedCatalog:
    source_url_base: str
    languages: tuple[CatalogLanguage, ...]
    problems: tuple[CatalogProblem, ...]

    @classmethod
    def empty(cls, *, source_url_base: str = "") -> Self:
        return cls(source_url_base=source_url_base, languages=(), problems=())

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        version = payload.get("version")
        languages_payload = payload.get("languages", {})
        problems_payload = payload.get("problems", {})
        source_url_base = payload.get("source_url_base")

        if version != CATALOG_VERSION:
            raise ValueError(f"Generated catalog version must be {CATALOG_VERSION}.")
        if not isinstance(source_url_base, str):
            raise TypeError("Generated catalog must contain a string 'source_url_base'.")
        if not isinstance(languages_payload, Mapping) or not isinstance(problems_payload, Mapping):
            raise TypeError(
                "Generated catalog must contain 'languages' and 'problems' mappings."
            )

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
        return cls(
            source_url_base=source_url_base,
            languages=languages,
            problems=problems,
        )

    @property
    def language_order(self) -> tuple[str, ...]:
        return tuple(language.name for language in self.languages)

    def to_payload(self) -> dict[str, object]:
        return {
            "version": CATALOG_VERSION,
            "source_url_base": self.source_url_base,
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


class SolutionActionLabel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    label: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().lower()


class SolutionActionLabelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    actions: tuple[SolutionActionLabel, ...]

    @model_validator(mode="after")
    def validate_uniqueness(self) -> Self:
        names = [action.name for action in self.actions]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate action names detected in solution action labels.")
        return self


@dataclass(frozen=True)
class SolutionCommit:
    file_path: str
    language: str
    approach: str
    slug: str


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
