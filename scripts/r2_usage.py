#!/usr/bin/env python3
"""Estimate current-month Cloudflare R2 free-tier consumption.

This is read-only. It queries R2 Operations and Storage analytics via the
Cloudflare GraphQL API. Billing & Licensing remains the source of truth for
actual charges.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request


GRAPHQL_ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"
FREE_STORAGE_BYTES = 10_000_000_000  # Cloudflare pricing uses decimal GB.
FREE_CLASS_A = 1_000_000
FREE_CLASS_B = 10_000_000

OPERATIONS_QUERY = """
query R2Operations(
  $accountTag: String!
  $startDate: Time
  $endDate: Time
  $bucketName: String
) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      r2OperationsAdaptiveGroups(
        limit: 10000
        filter: {
          datetime_geq: $startDate
          datetime_leq: $endDate
          bucketName: $bucketName
        }
      ) {
        sum { requests }
        dimensions { actionType }
      }
    }
  }
}
"""

STORAGE_QUERY = """
query R2Storage(
  $accountTag: String!
  $startDate: Time
  $endDate: Time
  $bucketName: String
) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      r2StorageAdaptiveGroups(
        limit: 10000
        filter: {
          datetime_geq: $startDate
          datetime_leq: $endDate
          bucketName: $bucketName
        }
        orderBy: [datetime_DESC]
      ) {
        max { objectCount uploadCount payloadSize metadataSize }
        dimensions { datetime }
      }
    }
  }
}
"""

# Names are normalized before matching, so PutObject and put_object both work.
CLASS_A = {
    "listbuckets",
    "putbucket",
    "listobjects",
    "putobject",
    "copyobject",
    "completemultipartupload",
    "createmultipartupload",
    "lifecyclestoragetiertransition",
    "listmultipartuploads",
    "uploadpart",
    "uploadpartcopy",
    "listparts",
    "putbucketencryption",
    "putbucketcors",
    "putbucketlifecycleconfiguration",
}
CLASS_B = {
    "headbucket",
    "headobject",
    "getobject",
    "usagesummary",
    "getbucketencryption",
    "getbucketlocation",
    "getbucketcors",
    "getbucketlifecycleconfiguration",
}
FREE_OPERATIONS = {"deleteobject", "deletebucket", "abortmultipartupload"}


def normalize_operation(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def current_month_range(now: dt.datetime | None = None) -> tuple[str, str]:
    now = now or dt.datetime.now(dt.timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start.isoformat().replace("+00:00", "Z"), now.isoformat().replace("+00:00", "Z")


def post_graphql(token: str, query: str, variables: dict[str, str | None]) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cloudflare API request failed: {exc.reason}") from exc

    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
    return payload.get("data", {})


def one_account(data: dict) -> dict:
    accounts = data.get("viewer", {}).get("accounts", [])
    if not accounts:
        raise RuntimeError("No account data returned; check account ID and Analytics Read permission")
    return accounts[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-id", default=os.getenv("CF_ACCOUNT_ID"))
    parser.add_argument("--api-token", default=os.getenv("CF_API_TOKEN"))
    parser.add_argument("--bucket", default=os.getenv("R2_BUCKET"))
    parser.add_argument("--start", help="ISO-8601 UTC start, default: first day of current UTC month")
    parser.add_argument("--end", help="ISO-8601 UTC end, default: now")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    missing = [name for name, value in (("CF_ACCOUNT_ID", args.account_id), ("CF_API_TOKEN", args.api_token), ("R2_BUCKET", args.bucket)) if not value]
    if missing:
        parser.error("missing environment variables or flags: " + ", ".join(missing))

    default_start, default_end = current_month_range()
    start = args.start or default_start
    end = args.end or default_end
    variables = {
        "accountTag": args.account_id,
        "startDate": start,
        "endDate": end,
        "bucketName": args.bucket,
    }

    operations = one_account(post_graphql(args.api_token, OPERATIONS_QUERY, variables)).get("r2OperationsAdaptiveGroups", [])
    storage = one_account(post_graphql(args.api_token, STORAGE_QUERY, variables)).get("r2StorageAdaptiveGroups", [])

    by_operation: dict[str, int] = {}
    for row in operations:
        action = row.get("dimensions", {}).get("actionType") or "unknown"
        count = int((row.get("sum") or {}).get("requests") or 0)
        by_operation[action] = by_operation.get(action, 0) + count

    class_a = class_b = free = unknown = 0
    for action, count in by_operation.items():
        normalized = normalize_operation(action)
        if normalized in CLASS_A:
            class_a += count
        elif normalized in CLASS_B:
            class_b += count
        elif normalized in FREE_OPERATIONS:
            free += count
        else:
            unknown += count

    peak = {
        "payloadSize": 0,
        "metadataSize": 0,
        "objectCount": 0,
        "uploadCount": 0,
    }
    for row in storage:
        values = row.get("max") or {}
        for key in peak:
            peak[key] = max(peak[key], int(values.get(key) or 0))

    result = {
        "period": {"start": start, "end": end},
        "bucket": args.bucket,
        "peak_storage_bytes": peak["payloadSize"] + peak["metadataSize"],
        "peak_payload_bytes": peak["payloadSize"],
        "peak_metadata_bytes": peak["metadataSize"],
        "peak_object_count": peak["objectCount"],
        "operations": {
            "class_a": class_a,
            "class_b": class_b,
            "free": free,
            "unclassified": unknown,
            "by_action": dict(sorted(by_operation.items())),
        },
        "free_tier": {
            "storage_bytes": FREE_STORAGE_BYTES,
            "class_a": FREE_CLASS_A,
            "class_b": FREE_CLASS_B,
            "storage_percent_estimate": round((peak["payloadSize"] + peak["metadataSize"]) / FREE_STORAGE_BYTES * 100, 3),
            "class_a_percent_estimate": round(class_a / FREE_CLASS_A * 100, 3),
            "class_b_percent_estimate": round(class_b / FREE_CLASS_B * 100, 3),
        },
        "warning": "Analytics is an estimate; verify actual charges in Cloudflare Billable Usage.",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"R2 usage estimate: {args.bucket}")
    print(f"period: {start} → {end}")
    print(f"peak storage: {result['peak_storage_bytes'] / 1_000_000_000:.6f} GB ({result['free_tier']['storage_percent_estimate']:.3f}% of 10 GB)")
    print(f"objects: {peak['objectCount']}")
    print(f"Class A: {class_a:,} ({result['free_tier']['class_a_percent_estimate']:.3f}% of 1,000,000)")
    print(f"Class B: {class_b:,} ({result['free_tier']['class_b_percent_estimate']:.3f}% of 10,000,000)")
    print(f"free operations: {free:,}; unclassified: {unknown:,}")
    if unknown:
        print("unclassified actions:", ", ".join(sorted(action for action in by_operation if normalize_operation(action) not in CLASS_A | CLASS_B | FREE_OPERATIONS)))
    print("NOTE: verify actual charges in Cloudflare Billable Usage.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
