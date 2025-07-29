from enum import Enum


class GenerationJobStatus(str, Enum):
    ready = "ready"
    generating = "generating"
    failed = "failed"

