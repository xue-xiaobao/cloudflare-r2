# Cloudflare R2 官方资料

按需要阅读，不要把这里的链接当作当前账户账单的替代品。

- [R2 定价与免费额度](https://developers.cloudflare.com/r2/pricing/)
- [R2 存储桶公共访问](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [R2 上传对象](https://developers.cloudflare.com/r2/objects/upload-objects/)
- [R2 CLI](https://developers.cloudflare.com/r2/get-started/cli/)
- [R2 API Token](https://developers.cloudflare.com/r2/api/tokens/)
- [R2 Metrics 与 GraphQL](https://developers.cloudflare.com/r2/platform/metrics-analytics/)
- [GraphQL Analytics Token](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)
- [Cloudflare 按量计费](https://developers.cloudflare.com/billing/understand/usage-based-billing/)

## 关键口径

- Standard R2 当前免费额度：10 GB-month 存储、100 万 Class A 操作、1000 万 Class B 操作；直接出站流量免费。
- Infrequent Access 不享受同一免费额度，并且可能产生数据取回费用；图床默认不要选择它。
- `r2.dev` 是开发用途并会限速；自定义域名才能使用 Cloudflare Cache、WAF 等能力。
- R2 Metrics 的 GraphQL 数据通常只保留约 31 天，而且是分析数据；实际扣费以 Cloudflare 的 Billable Usage/发票为准。
- Analytics API Token 只需要 `Account → Account Analytics → Read`，查询额度不需要对象读写权限。
