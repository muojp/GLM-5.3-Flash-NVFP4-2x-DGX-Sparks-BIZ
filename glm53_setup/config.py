"""Resolve checkout assets independently of the caller's working directory."""

import json
import os
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
RECORDS = ROOT / "records"
LOCK_PATH = ROOT / "config/runtime.lock.json"
MODEL_LAYERS = 45
HIDDEN_SIZE = 4096
FIXTURE_LAYERS = 4
TEACHER_PRECISION = "NVFP4-Marlin-W4A16"


def cache_root():
    """The Hugging Face cache this host actually uses.

    `HF_HOME` is that directory for huggingface_hub, and the launcher composes
    `hub/` and the MTP view under the same root before mounting it read-only, so
    honouring it keeps download, preflight and mount on one path. A host whose
    default `~/.cache/huggingface` belongs to another user — an old sudo
    download leaves exactly that — otherwise has nowhere to put the weights.
    `HF_HUB_CACHE` alone is not enough: it names `hub/` and leaves the view root
    unstated, so it is not read here.
    """
    home = os.environ.get("HF_HOME")
    return Path(home).expanduser() if home else Path.home() / ".cache/huggingface"


def load_lock():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[0-9a-f]{40}", lock["revision"]):
        raise ValueError("Model revision must be a full commit hash")
    if not re.fullmatch(r"[\w./-]+@sha256:[0-9a-f]{64}", lock["image"]):
        raise ValueError("Base image must be digest-pinned")
    return lock


def version():
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]


MODEL = load_lock()["model"]
REVISION = load_lock()["revision"]
