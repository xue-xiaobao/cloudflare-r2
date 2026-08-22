# cloudflare-r2

[中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A vendor-neutral open-source Agent Skill for using Cloudflare R2 as a low-volume image host. It works with any Agent that supports the standard `SKILL.md` layout or the Skills CLI.

It helps you:

- Set up R2 and check free-tier usage, billing, and accidental payment risks;
- Upload images through the dashboard or Wrangler and return public URLs;
- Inspect Cloudflare metrics or estimate current-month free-tier usage with a read-only GraphQL script.

## Installation

Install it with the open-source Skills CLI. `npx` is provided with Node.js. The target directory is chosen by the current Agent and the CLI; this Skill is not tied to Codex, Claude Code, or any single platform.

Install globally for all Agents detected by the CLI:

```bash
npx skills add xue-xiaobao/cloudflare-r2 -g -a '*' -y
```

Install it in the current project for all detected Agents:

```bash
npx skills add xue-xiaobao/cloudflare-r2 -a '*' -y
```

To target specific Agents, replace `*` with names supported by your CLI:

```bash
npx skills add xue-xiaobao/cloudflare-r2 -g -a codex claude-code -y
```

The CLI chooses the installation path based on scope and target Agents. Follow each Agent's own invocation syntax after installation.

Check installed skills:

```bash
npx skills list
```

List available skills in the repository without installing:

```bash
npx skills add xue-xiaobao/cloudflare-r2 --list
```

Example request (the exact prefix depends on your Agent):

```text
Use cloudflare-r2 to upload this image and check the current R2 free-tier usage.
```

## Important notes

1. R2's free tier is not a hard spending cap. Exceeding the free tier, using a non-Standard storage class, or enabling other paid products may incur charges.
2. Never put credit-card details, PayPal details, API tokens, or secret keys in the repository, shell history, or chat messages.
3. The `r2.dev` public URL is intended for low-volume, non-production use. Evaluate a custom domain and CDN costs separately for high-traffic websites.
4. Objects in a public bucket are readable by anyone who obtains the URL. Do not upload private or sensitive files.

## Free-tier usage script

The script only reads Cloudflare GraphQL Analytics and does not modify the account:

```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="account-analytics-read-token"
export R2_BUCKET="your-bucket-name"
python3 scripts/r2_usage.py
```

The API token only needs `Account → Account Analytics → Read`. The script reports an estimate; use Cloudflare **Billable Usage** as the billing source of truth.

## Official resources

- [R2 pricing and free tier](https://developers.cloudflare.com/r2/pricing/)
- [R2 public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Uploading objects to R2](https://developers.cloudflare.com/r2/objects/upload-objects/)
- [R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)
- [Cloudflare GraphQL Analytics tokens](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

## License

[MIT](./LICENSE)
