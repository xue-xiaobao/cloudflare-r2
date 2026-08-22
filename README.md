# cloudflare-r2

一个面向 Codex 的开源 Skill，用于把 Cloudflare R2 作为低频图片图床使用：

- 申请和配置 R2，并检查免费额度、账单与自动扣款风险；
- 通过网页或 Wrangler 上传图片并生成公开链接；
- 在 Cloudflare 控制台查看指标，或用只读 GraphQL 脚本估算当前月免费额度消耗。

## 安装

使用开源 Skills CLI 从 GitHub 安装。`npx` 随 Node.js 一起提供：

全局安装到当前用户的 Codex Skills 目录：

```bash
npx skills add xue-xiaobao/cloudflare-r2 -g -a codex -y
```

`npx skills` 会根据目标 Agent 使用全局 `~/.agents/skills/` 或项目内的 `./.agents/skills/`；以安装器最后输出的目标路径为准。

只安装到当前项目：

```bash
npx skills add xue-xiaobao/cloudflare-r2 -a codex -y
```

安装后可以检查：

```bash
npx skills list
```

如果只想查看仓库中可安装的 Skill，不执行安装：

```bash
npx skills add xue-xiaobao/cloudflare-r2 --list
```

在 Codex 中显式调用：

```text
$cloudflare-r2 帮我上传这张图片，并检查当前 R2 免费额度
```

也可以让 Codex 根据 Skill 描述自动选择它。

## 使用前的重要事项

1. R2 的免费额度不是硬封顶。超出免费额度、使用非 Standard 存储或启用其他收费产品，都可能产生账单。
2. 不要把信用卡、PayPal、API Token 或 Secret Key 写入仓库、命令行历史或聊天记录。
3. `r2.dev` 公开地址适合低频、非生产使用；高流量网站应使用自定义域名，并单独评估 CDN 成本。
4. 公共桶中的对象任何人都可以读取。请勿上传私人或敏感文件。

## 免费额度查询脚本

脚本只读 Cloudflare GraphQL Analytics，不修改账户：

```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="account-analytics-read-token"
export R2_BUCKET="your-bucket-name"
python3 scripts/r2_usage.py
```

API Token 只需要 `Account → Account Analytics → Read` 权限。脚本结果是估算值，实际费用以 Cloudflare **Billable Usage** 为准。

## 官方资料

- [R2 定价与免费额度](https://developers.cloudflare.com/r2/pricing/)
- [R2 公共存储桶](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [R2 上传对象](https://developers.cloudflare.com/r2/objects/upload-objects/)
- [R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)
- [Cloudflare GraphQL Analytics Token](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

## 许可证

[MIT](./LICENSE)
