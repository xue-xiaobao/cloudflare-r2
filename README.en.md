<h1 align="center">Cloudflare R2 Image Host</h1>

<p align="center"><strong>Agent Skills · Low-volume image hosting · Cloudflare R2</strong></p>
<p align="center"><em>Upload once, reuse reliably.</em></p>

<p align="center">
  <a href="./README.md">中文</a> · <strong>English</strong>
</p>
<p align="center">
  <a href="https://github.com/xue-xiaobao/cloudflare-r2/stargazers"><img src="https://img.shields.io/github/stars/xue-xiaobao/cloudflare-r2?style=flat&amp;logo=github" alt="GitHub stars"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/xue-xiaobao/cloudflare-r2" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Agent%20Skills-compatible-4F46E5" alt="Agent Skills compatible">
  <img src="https://img.shields.io/badge/docs-English-E11D48" alt="English documentation">
</p>
<p align="center">
  <a href="#about">About</a> ·
  <a href="#install">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#boundary">Billing &amp; safety</a> ·
  <a href="#metrics">Usage metrics</a> ·
  <a href="#license">License</a> ·
  <a href="#feedback">Feedback</a>
</p>

---

<a id="about"></a>
## About

`cloudflare-r2` is an open-source Agent Skill built on the standard Agent Skills layout. It uses Cloudflare R2 as a low-volume image host and can be installed into compatible Agents with the Skills CLI.

It helps you:

- Set up R2 and check free-tier usage, billing, and accidental payment risks;
- Upload images through the dashboard or Wrangler and return public URLs;
- Inspect Cloudflare metrics or estimate current-month free-tier usage with a read-only GraphQL script.

<a id="install"></a>
## Installation

Install it with the Skills CLI for the current user's compatible Agents:

```bash
npx skills add xue-xiaobao/cloudflare-r2 -g -a '*' -y
```

For project scope, remove `-g`:

```bash
npx skills add xue-xiaobao/cloudflare-r2 -a '*' -y
```

The CLI selects the installation path. Follow your Agent's invocation syntax, then check the installation:

```bash
npx skills list
```

<a id="usage"></a>
## Usage

Example request (the exact prefix depends on your Agent):

```text
Use cloudflare-r2 to upload this image and check the current R2 free-tier usage.
```

When uploading an image, the Skill guides you to confirm the bucket, public URL, and object key. For usage checks, treat Cloudflare's Billable Usage page as the source of truth.

<a id="boundary"></a>
## Billing and safety

1. R2 free-tier allowances are calculated monthly. Exceeding the free tier, using a non-Standard storage class, or enabling other paid products may incur charges.
2. Keep credit-card details, PayPal details, API tokens, and secret keys in secure account storage or environment variables. Do not put them in the repository, shell history, or chat messages.
3. The `r2.dev` public URL is intended for low-volume, development use. Evaluate a custom domain and CDN costs separately for high-traffic websites.
4. Objects in a public bucket are readable by anyone who obtains the URL. Upload files that are suitable for public access.

<a id="metrics"></a>
## Free-tier usage

The script reads Cloudflare GraphQL Analytics to estimate current-month R2 operation and storage usage:

```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="account-analytics-read-token"
export R2_BUCKET="your-bucket-name"
python3 scripts/r2_usage.py
```

The API token needs `Account → Account Analytics → Read`. The script reports an estimate; use Cloudflare **Billable Usage** as the billing source of truth.

## Official resources

- [R2 pricing and free tier](https://developers.cloudflare.com/r2/pricing/)
- [R2 public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Uploading objects to R2](https://developers.cloudflare.com/r2/objects/upload-objects/)
- [R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)
- [Cloudflare GraphQL Analytics tokens](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

<a id="license"></a>
## License

[MIT](./LICENSE)

<a id="feedback"></a>
## Feedback

Use [GitHub Issues](https://github.com/xue-xiaobao/cloudflare-r2/issues) to report problems or suggest improvements. Remove credentials, personal information, and internal project names before submitting.
