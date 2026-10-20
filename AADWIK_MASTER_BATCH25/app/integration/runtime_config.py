from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    enabled: bool = False
    dry_run: bool = True
    preserve_existing_runner: bool = True


def production_config():
    return RuntimeConfig(
        enabled=True,
        dry_run=False,
        preserve_existing_runner=True,
    )
