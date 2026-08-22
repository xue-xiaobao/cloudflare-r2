---
name: cloudflare-r2
description: "Use Cloudflare R2 as a low-volume image host: set up a bucket and public URL, upload images, return links, and check free-tier usage while preventing accidental billing. Use when the user asks to create, use, or monitor a Cloudflare R2 image host."
---

# Cloudflare R2 图床

这是一个遵循 Agent Skills 规范的 R2 图床 Skill。Agent 读取标准 `SKILL.md` 目录即可复用下面的流程；`agents/openai.yaml` 是可选的 OpenAI/Codex 界面元数据。

R2 的定位是“图片源站/中转图床”。公众号外链图片通常会在编辑器中由微信重新托管，因此文章内展示速度以微信服务器为准。

## 安全边界

- 创建存储桶、开启公开访问、上传或删除对象前，先确认用户已明确授权。
- 凭据、支付信息和密钥通过环境变量、`wrangler login` 或安全账户设置处理；命令输出和文档仅展示占位符。
- 任何付款方式、自动扣款、套餐、预算或订阅变更都属于高风险操作。先展示当前状态和影响，等用户明确授权后再修改；预算告警用于提示，实际计费以 Billable Usage 为准。
- 公共桶里的对象可被任何拿到链接的人读取；上传范围限定为适合公开访问的对象，敏感文件由私有存储管理。
- 优先复用已有桶，避免同一用途重复创建；图床默认使用 R2 **Standard** 存储。

## 1. 申请和零意外扣费检查

先打开 [Cloudflare Dashboard](https://dash.cloudflare.com/)，进入 **Storage & databases → R2 → Overview**。

首次使用时，Cloudflare 会要求完成 R2 subscription/checkout。当前 Standard 免费额度为每月 10 GB-month 存储、100 万 Class A 操作、1000 万 Class B 操作，R2 直接出站流量免费；超出额度或使用其他收费产品时，账户可能产生账单。以[官方定价](https://developers.cloudflare.com/r2/pricing/)为准。

在允许上传前检查：

1. 当前 R2 订阅是否已开通、是否为 Standard 存储。
2. **Billing & Licensing / Billable Usage** 中当前周期是否已有 R2 或其他产品费用。
3. 是否绑定了信用卡或 PayPal、是否开启了自动支付。
4. 是否有余额、未结账单或预算限制。

如果用户要求“绝不扣费”，先检查支付方式、账单和账户开通条件，再决定是否继续。免费额度与预算告警属于提示机制，账户实际计费由用量与账单规则决定；账单页面是最终依据。若账户开通要求支付方式，应将其作为账户前置条件处理，不对绕过条件作承诺。

图床场景只启用 Standard R2 对象；Workers、Images、Cache Reserve、R2 Data Catalog、Infrequent Access、第三方 CDN 和其他按量付费服务需单独评估成本。

## 2. 创建桶和公开链接

如果没有可复用的桶：

1. R2 → **Create bucket**。
2. 使用小写字母、数字和连字符命名，例如 `xiaobao-gzh-images`。
3. 选择 Standard 存储，图床使用单一桶即可。

公众号或网页需要直接读取图片时，在桶的 **Settings → Public Development URL** 开启 `r2.dev`，输入 `allow` 确认。`r2.dev` 是开发用途、具有访问限速的公开地址，适合低频公众号素材中转；高流量生产站点应采用更适合的部署方案。[公共桶说明](https://developers.cloudflare.com/r2/buckets/public-buckets/)

生产网页需要缓存、WAF 或稳定域名时，使用 **Settings → Custom Domains → Add** 绑定自己账户中的域名。自定义域名会使请求经过 Cloudflare Cache；`r2.dev` 作为独立地址使用。[R2 缓存说明](https://developers.cloudflare.com/cache/interaction-cloudflare-products/r2/)

记录三项公开配置；密钥单独存放在安全的环境变量或凭据管理器中：

- bucket name
- public base URL（例如 `https://pub-xxxx.r2.dev/`）
- 当前存储类（应为 Standard）

## 3. 上传图片并返回图床链接

### 网页后台（默认）

进入 R2 → 目标 bucket → **Upload**，拖入图片或选择文件。用前缀整理对象，例如：

```text
2026/08/article-cover.png
2026/08/article-01.png
```

R2 的“文件夹”只是对象 key 中的 `/` 前缀；上传成功后，把 `public base URL + object key` 拼成链接，并对空格、中文等特殊字符做 URL 编码。

例如：

```text
https://pub-xxxx.r2.dev/2026/08/article-cover.png
```

上传后至少做一次外部验证：

```bash
curl -I "https://pub-xxxx.r2.dev/2026/08/article-cover.png"
```

应看到 HTTP 200 和正确的 `Content-Type`（PNG 为 `image/png`，JPEG 为 `image/jpeg`）。如果用于微信公众号，先把链接粘贴进编辑器，确认微信能抓取；发布后以微信文章内的图片为准。

### 命令行（批量或重复上传）

优先使用 Wrangler，避免在命令行参数中暴露密钥：

```bash
npx wrangler login
npx wrangler r2 object put \
  <bucket>/<object-key> \
  --file="/absolute/path/to/image.png" \
  --remote \
  --content-type="image/png"
```

单文件小于约 100 MB 时适合普通上传；大量文件或大文件使用 `rclone` 等支持 multipart 的 S3 工具。[官方上传说明](https://developers.cloudflare.com/r2/objects/upload-objects/) [CLI 说明](https://developers.cloudflare.com/r2/get-started/cli/)

如果使用 S3 API，需要 R2 API Token 的 Object Read & Write 权限；token 放在安全的环境变量或本地凭据文件中，Skill、仓库和聊天记录只保留占位符。[R2 认证说明](https://developers.cloudflare.com/r2/api/tokens/)

## 4. 查询免费额度和实际费用

### 先看控制台（权威）

- **R2 → bucket → Metrics**：查看最近 24 小时或自定义时间范围的存储和操作数量。
- **Billing & Licensing → Billable Usage**：查看当前账单周期的实际费用、账单日期和产品明细。

R2 的 free tier 当前为：

| 项目 | 每月免费额度 |
|---|---:|
| Standard 存储 | 10 GB-month |
| Class A 操作 | 1,000,000 次 |
| Class B 操作 | 10,000,000 次 |
| 直接出站流量 | 免费 |

`Metrics` 用于分析，Cloudflare 的 GraphQL 指标保留约 31 天；最终费用以 Billable Usage/发票为准。[R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/) [Cloudflare 计费说明](https://developers.cloudflare.com/billing/understand/usage-based-billing/)

### 脚本估算（可选）

用户要求在终端查询时，使用本 Skill 的 `scripts/r2_usage.py`。它读取当前 UTC 月份的 R2 Operations/Storage GraphQL 数据，输出 Class A、Class B、免费操作、存储峰值和相对于免费额度的估算比例；账单支付信息由 Cloudflare 控制台管理。

运行前需要一个只读的 **Account → Account Analytics → Read** API Token，以及环境变量：

```bash
export CF_ACCOUNT_ID="你的_account_id"
export CF_API_TOKEN="只读_analytics_token"
export R2_BUCKET="你的_bucket_name"
python3 scripts/r2_usage.py
```

也可以指定时间范围：

```bash
python3 scripts/r2_usage.py \
  --start "2026-08-01T00:00:00Z" \
  --end "2026-08-31T23:59:59Z"
```

创建 Analytics Token 时将权限范围设为 Account → Account Analytics → Read，查询额度使用只读权限即可。[Analytics Token 说明](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

脚本输出标注“估算”，并提醒用户回到 **Billable Usage** 复核；GraphQL 指标仅作估算依据，零费用状态以账单页面为准。

## 5. 常见故障处理

- **链接 403/404**：检查对象 key、桶的 public access、`r2.dev` 是否仍为 Allowed，以及 URL 是否正确编码。
- **图片能下载但浏览器不显示**：检查 `Content-Type` 是否为 `image/png`、`image/jpeg` 或 `image/webp`。
- **公众号抓取失败**：先用 `curl -I` 验证公网可达，再检查链接是否带临时签名、是否被防盗链或访问控制拦截。
- **国内访问体验**：`r2.dev` 定位为通用公开地址；公众号导入后，文章内展示通常由微信服务器负责。外部网页长期使用时，再评估自定义域名和国内 CDN。
- **额度接近上限**：暂停批量上传和低优先级自动读取，先查看 Billable Usage，并结合预算告警安排后续用量。
