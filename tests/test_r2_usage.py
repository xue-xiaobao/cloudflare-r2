import importlib.util
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "r2_usage.py"
SPEC = importlib.util.spec_from_file_location("r2_usage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class R2UsageTests(unittest.TestCase):
    def test_normalize_operation(self):
        self.assertEqual(MODULE.normalize_operation("Put_Object"), "putobject")
        self.assertEqual(MODULE.normalize_operation("GetObject"), "getobject")

    def test_main_classifies_operations_and_peak_storage(self):
        responses = [
            {
                "viewer": {
                    "accounts": [
                        {
                            "r2OperationsAdaptiveGroups": [
                                {"sum": {"requests": 3}, "dimensions": {"actionType": "PutObject"}},
                                {"sum": {"requests": 20}, "dimensions": {"actionType": "GetObject"}},
                                {"sum": {"requests": 4}, "dimensions": {"actionType": "DeleteObject"}},
                                {"sum": {"requests": 2}, "dimensions": {"actionType": "FutureOperation"}},
                            ]
                        }
                    ]
                }
            },
            {
                "viewer": {
                    "accounts": [
                        {
                            "r2StorageAdaptiveGroups": [
                                {
                                    "max": {
                                        "objectCount": 4,
                                        "uploadCount": 0,
                                        "payloadSize": 700_000_000,
                                        "metadataSize": 3_000_000,
                                    },
                                    "dimensions": {"datetime": "2026-08-22T00:00:00Z"},
                                },
                                {
                                    "max": {
                                        "objectCount": 3,
                                        "uploadCount": 0,
                                        "payloadSize": 500_000_000,
                                        "metadataSize": 2_000_000,
                                    },
                                    "dimensions": {"datetime": "2026-08-21T00:00:00Z"},
                                },
                            ]
                        }
                    ]
                }
            },
        ]

        original = MODULE.post_graphql
        MODULE.post_graphql = lambda *args, **kwargs: responses.pop(0)
        old_env = os.environ.copy()
        old_argv = sys.argv
        try:
            os.environ.update(
                {
                    "CF_ACCOUNT_ID": "account-test",
                    "CF_API_TOKEN": "token-test",
                    "R2_BUCKET": "bucket-test",
                }
            )
            sys.argv = ["r2_usage.py", "--json"]
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(MODULE.main(), 0)
            result = json.loads(output.getvalue())
        finally:
            MODULE.post_graphql = original
            os.environ.clear()
            os.environ.update(old_env)
            sys.argv = old_argv

        self.assertEqual(result["operations"]["class_a"], 3)
        self.assertEqual(result["operations"]["class_b"], 20)
        self.assertEqual(result["operations"]["free"], 4)
        self.assertEqual(result["operations"]["unclassified"], 2)
        self.assertEqual(result["peak_storage_bytes"], 703_000_000)


if __name__ == "__main__":
    unittest.main()
