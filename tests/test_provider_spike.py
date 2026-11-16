import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from icloud_photo_archiver.provider_spike import inspect_pages


def asset(name, master):
    return {"recordType": "CPLAsset", "recordName": name,
            "fields": {"masterRef": {"value": {"recordName": master}}}}


def master(name):
    return {"recordType": "CPLMaster", "recordName": name}


class ProviderSpikeTests(unittest.TestCase):
    def test_shared_master_and_rank_pagination(self):
        pages = {0: [asset("a", "m"), asset("b", "m"), master("m")],
                 2: [asset("c", "m")], 3: []}
        result = inspect_pages(pages.__getitem__)
        self.assertTrue(result.complete)
        self.assertEqual([a.asset_id for a in result.assets], ["a", "b", "c"])

    def test_missing_master_and_duplicate_are_not_complete(self):
        pages = {0: [asset("a", "missing")], 1: [asset("a", "m"), master("m")], 2: []}
        result = inspect_pages(pages.__getitem__)
        self.assertFalse(result.complete)
        self.assertEqual(result.issues, ("asset missing master", "duplicate asset identity"))

    def test_nonempty_nonasset_page_and_page_limit_are_incomplete(self):
        self.assertFalse(inspect_pages(lambda _: [master("m")]).complete)
        self.assertFalse(inspect_pages(lambda _: [asset("a", "m"), master("m")], 1).complete)

    def test_fetch_failure_propagates(self):
        def fetch(rank):
            if rank:
                raise OSError("disconnected")
            return [asset("a", "m"), master("m")]
        with self.assertRaises(OSError):
            inspect_pages(fetch)


if __name__ == "__main__":
    unittest.main()
