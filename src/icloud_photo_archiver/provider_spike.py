"""Experimental raw-page inspection; not an authenticated provider implementation."""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence


Record = Mapping[str, Any]


@dataclass(frozen=True)
class AssetPair:
    asset_id: str
    master_id: str
    asset: Record
    master: Record


@dataclass(frozen=True)
class ScanResult:
    assets: tuple[AssetPair, ...]
    issues: tuple[str, ...]
    reached_end: bool

    @property
    def complete(self) -> bool:
        # This only describes the observed page sequence, not snapshot consistency.
        return self.reached_end and not self.issues


def inspect_pages(fetch: Callable[[int], Sequence[Record]], max_pages: int = 10000) -> ScanResult:
    """Inspect rank pages while retaining missing-master and duplicate evidence.

    The callback receives an asset rank and returns one raw provider page. Network
    exceptions propagate: callers must never treat a failed request as an end page.
    """
    if max_pages < 1:
        raise ValueError("max_pages must be positive")
    found: list[AssetPair] = []
    issues: list[str] = []
    seen: set[str] = set()
    previous_masters: dict[str, Record] = {}
    rank = 0
    for _ in range(max_pages):
        records = fetch(rank)
        assets = [r for r in records if r.get("recordType") == "CPLAsset"]
        masters = {r.get("recordName"): r for r in records
                   if r.get("recordType") == "CPLMaster" and isinstance(r.get("recordName"), str)}
        if not assets:
            if records:
                issues.append("nonempty page without assets")
            return ScanResult(tuple(found), tuple(issues), not records)
        for asset in assets:
            asset_id = asset.get("recordName")
            try:
                master_id = asset["fields"]["masterRef"]["value"]["recordName"]
            except (KeyError, TypeError):
                issues.append("asset missing master reference")
                continue
            if not isinstance(asset_id, str) or not asset_id or not isinstance(master_id, str) or not master_id:
                issues.append("asset or master identity missing")
                continue
            if asset_id in seen:
                issues.append("duplicate asset identity")
                continue
            seen.add(asset_id)
            master = masters.get(master_id) or previous_masters.get(master_id)
            if master is None:
                issues.append("asset missing master")
                continue
            found.append(AssetPair(asset_id, master_id, asset, master))
        rank += len(assets)
        previous_masters = masters
    issues.append("page limit reached")
    return ScanResult(tuple(found), tuple(issues), False)
