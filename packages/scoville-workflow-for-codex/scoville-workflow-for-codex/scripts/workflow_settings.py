"""Fixed Workflow pairs and explicit legacy-migration boundary."""
import sys
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or newer is required for Workflow helpers')
from pathlib import Path
import tomllib

from scoville_config import merge, section as config_section

EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
PAIR_KEYS = ("main", "review", "explore")


def validate_pair(pair: dict, field: str) -> None:
    if not isinstance(pair, dict) or set(pair) != {"model", "reasoning"}:
        raise ValueError(f"{field} must contain exactly model and reasoning; "
                         "e.g. {\"model\": \"gpt-6.1-sol\", \"reasoning\": \"high\"}")
    if not isinstance(pair["model"], str) or not pair["model"].strip() or any(c in pair["model"] for c in "\r\n"):
        raise ValueError(f"{field}.model must be a nonempty single-line model ID")
    if not isinstance(pair["reasoning"], str) or pair["reasoning"] not in EFFORTS:
        raise ValueError(f"{field}.reasoning must be one of {', '.join(sorted(EFFORTS))}")


def needs_cleanup(value: dict) -> bool:
    if "schema_version" in value and (type(value["schema_version"]) is not int or value["schema_version"] != 2):
        return value["schema_version"] == 1
    if set(value) & {"execute", "context", "manager", "pin_threads", "context_threshold_percent"}:
        return True
    old_routes = {"ultra_low", "low", "medium", "high", "ultra_high"}
    return any(isinstance(value.get(key), dict) and set(value[key]) & old_routes
               for key in ("review", "explore"))


def validate_config(config: dict) -> dict:
    if type(config.get("schema_version")) is not int or config["schema_version"] != 2:
        raise ValueError("workflow.schema_version must be integer 2; migrate old settings with Scoville Setup cleanup")
    if set(config) != {"schema_version", *PAIR_KEYS}:
        raise ValueError("workflow must contain exactly schema_version, main, review and explore; "
                         f"unexpected={sorted(set(config) - {'schema_version', *PAIR_KEYS})}, "
                         f"missing={sorted({'schema_version', *PAIR_KEYS} - set(config))}")
    for key in PAIR_KEYS:
        validate_pair(config[key], "workflow." + key)
    return config


def load_config(path: Path, project_root: Path | str | None = None) -> dict:
    with path.open("rb") as stream:
        defaults = validate_config(tomllib.load(stream))
    override = config_section("workflow", project_root)
    if needs_cleanup(override):
        raise ValueError("workflow uses the old configuration; run Scoville Setup cleanup before coding. "
                         "Reading Workflow settings never migrates them")
    return validate_config(merge(defaults, override))
