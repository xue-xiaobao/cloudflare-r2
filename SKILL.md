---
name: cloudflare-r2
description: "Use Cloudflare R2 as a low-volume image host: set up a bucket and public URL, upload images, return links, and check free-tier usage while preventing accidental billing. Use when the user asks to create, use, or monitor a Cloudflare R2 image host."
---

# Cloudflare R2 图床

把 R2 当作“图片源站/中转图床”，不要把它描述成国内 CDN。对微信公众号，外链图片通常会在编辑器中被微信重新托管，因此 R2 的国内访问速度不是发布后展示速度的唯一决定因素。

## 安全边界

- 只在用户明确要求时创建存储桶、开启公开访问、上传或删除对象。
- 不要索要、打印或写入聊天中的 API Token、Access Key、Secret Key、信用卡号或 PayPal 信息；命令行使用环境变量或 `wrangler login`。
- 任何付款方式、自动扣款、套餐、预算或订阅变更都属于高风险操作。先展示当前状态和影响，等用户明确授权后再修改；不能把“告警”当成硬限额。
- 公共桶里的对象可被任何拿到链接的人读取。禁止上传身份证、合同、私人照片、密钥和其他不应公开的文件。
- 上传前先确认已有桶和公开 URL，避免为同一用途重复创建桶。默认使用 R2 **Standard** 存储，不要为图床选择 Infrequent Access。

## 1. 申请和零意外扣费检查

先打开 [Cloudflare Dashboard](https://dash.cloudflare.com/)，进入 **Storage & databases → R2 → Overview**。

首次使用时，Cloudflare 会要求完成 R2 subscription/checkout。说明“免费额度”不等于账户永远不会产生账单：当前 Standard 免费额度为每月 10 GB-month 存储、100 万 Class A 操作、1000 万 Class B 操作，R2 直接出站流量免费；超出额度或使用其他收费产品后仍可能计费。以[官方定价](https://developers.cloudflare.com/r2/pricing/)为准。

在允许上传前检查：

1. 当前 R2 订阅是否已开通、是否为 Standard 存储。
2. **Billing & Licensing / Billable Usage** 中当前周期是否已有 R2 或其他产品费用。
3. 是否绑定了信用卡或 PayPal、是否开启了自动支付。
4. 是否有余额、未结账单或预算限制。

如果用户要求“绝不扣费”，不要直接绑定支付方式，也不要直接关闭或取消已有付款方式。先报告：免费额度不是强制停止阈值，预算告警只是通知；账单页面才是实际计费依据。若账户无法在无支付方式下开通 R2，应明确说明这是 Cloudflare 账户状态的限制，而不是承诺可以绕过。

避免这些会额外产生费用的功能：Workers、Images、Cache Reserve、R2 Data Catalog、Infrequent Access、第三方 CDN 或其他按量付费服务。只上传 Standard R2 对象即可。

## 2. 创建桶和公开链接

如果没有可复用的桶：

1. R2 → **Create bucket**。
2. 使用小写字母、数字和连字符命名，例如 `xiaobao-gzh-images`。
3. 选择 Standard 存储；不需要为图片创建多个区域桶。

公众号或网页需要直接读取图片时，在桶的 **Settings → Public Development URL** 开启 `r2.dev`，输入 `allow` 确认。`r2.dev` 是开发用途、会限速的公开地址；它适合低频公众号素材中转，不适合高流量生产站点。[公共桶说明](https://developers.cloudflare.com/r2/buckets/public-buckets/)

生产网页需要缓存、WAF 或稳定域名时，使用 **Settings → Custom Domains → Add** 绑定自己账户中的域名。自定义域名会使请求经过 Cloudflare Cache；不要把 `r2.dev` 再套一层 CNAME。[R2 缓存说明](https://developers.cloudflare.com/cache/interaction-cloudflare-products/r2/)

记录三项配置，不要写入密钥：

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

如果使用 S3 API，需要 R2 API Token 的 Object Read & Write 权限，并把 token 放在安全的环境变量或本地凭据文件中；绝不要把 token 写进 Skill、仓库或聊天记录。[R2 认证说明](https://developers.cloudflare.com/r2/api/tokens/)

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

`Metrics` 是分析数据，不是最终账单；Cloudflare 的 GraphQL 指标只保留约 31 天，最终费用以 Billable Usage/发票为准。[R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/) [Cloudflare 计费说明](https://developers.cloudflare.com/billing/understand/usage-based-billing/)

### 脚本估算（可选）

用户要求在终端查询时，使用本 Skill 的 `scripts/r2_usage.py`。它读取当前 UTC 月份的 R2 Operations/Storage GraphQL 数据，输出 Class A、Class B、免费操作、存储峰值和相对于免费额度的估算比例。脚本不会修改 Cloudflare 资源，也不会读取账单支付信息。

运行前需要一个只读的 **Account → Account Analytics → Read** API Token，以及环境变量：

```bash
export CF_ACCOUNT_ID="你的_account_id"
export CF_API_TOKEN="只读_analytics_token"
export R2_BUCKET="你的_bucket_name"
python3 .claude/skills/cloudflare-r2/scripts/r2_usage.py
```

也可以指定时间范围：

```bash
python3 .claude/skills/cloudflare-r2/scripts/r2_usage.py \
  --start "2026-08-01T00:00:00Z" \
  --end "2026-08-31T23:59:59Z"
```

创建 Analytics Token 时只选 Account → Account Analytics → Read；不要为了查额度创建写权限 token。[Analytics Token 说明](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

脚本输出必须标注“估算”，并提醒用户回到 **Billable Usage** 复核；不要把 GraphQL 指标当作零费用保证。

## 5. 常见故障处理

- **链接 403/404**：检查对象 key、桶的 public access、`r2.dev` 是否仍为 Allowed，以及 URL 是否正确编码。
- **图片能下载但浏览器不显示**：检查 `Content-Type` 是否为 `image/png`、`image/jpeg` 或 `image/webp`。
- **公众号无法抓取**：先用 `curl -I` 验证公网可达，再检查链接是否带临时签名、是否被防盗链或访问控制拦截。
- **国内访问慢**：`r2.dev` 不是中国大陆 CDN；公众号导入后通常不影响文章内展示。外部网页长期使用时，再评估自定义域名和国内 CDN。
- **额度接近上限**：停止批量上传和不必要的自动读取，先查看 Billable Usage；不要只依赖预算告警。
