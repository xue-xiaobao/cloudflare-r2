<h1 align="center">Cloudflare R2 图床</h1>

<p align="center"><strong>Agent Skills · 低频图片图床 · Cloudflare R2</strong></p>
<p align="center"><em>上传一次，稳定复用。</em></p>

<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a>
</p>
<p align="center">
  <a href="https://github.com/xue-xiaobao/cloudflare-r2/stargazers"><img src="https://img.shields.io/github/stars/xue-xiaobao/cloudflare-r2?style=flat&amp;logo=github" alt="GitHub stars"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/xue-xiaobao/cloudflare-r2" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Agent%20Skills-compatible-4F46E5" alt="Agent Skills compatible">
  <img src="https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-E11D48" alt="中文文档">
</p>
<p align="center">
  <a href="#about">关于</a> ·
  <a href="#install">安装</a> ·
  <a href="#usage">使用</a> ·
  <a href="#boundary">费用与安全</a> ·
  <a href="#metrics">额度查询</a> ·
  <a href="#license">许可证</a> ·
  <a href="#feedback">反馈</a>
</p>

---

<a id="about"></a>
## 关于

`cloudflare-r2` 是一个遵循 Agent Skills 规范的开源 Skill，用于把 Cloudflare R2 作为低频图片图床使用，可通过 Skills CLI 安装到兼容的 Agent。

它负责：

- 申请和配置 R2，并检查免费额度、账单与自动扣款风险；
- 通过网页或 Wrangler 上传图片并生成公开链接；
- 在 Cloudflare 控制台查看指标，或用只读 GraphQL 脚本估算当前月免费额度消耗。

<a id="install"></a>
## 安装

使用 Skills CLI 安装到当前用户的兼容 Agent：

```bash
npx skills add xue-xiaobao/cloudflare-r2 -g -a '*' -y
```

项目级安装时，去掉 `-g`：

```bash
npx skills add xue-xiaobao/cloudflare-r2 -a '*' -y
```

安装目录由 CLI 自动选择，调用方式按 Agent 的说明执行。检查安装结果：

```bash
npx skills list
```

<a id="usage"></a>
## 使用

调用示例（具体前缀由 Agent 决定）：

```text
使用 cloudflare-r2：帮我上传这张图片，并检查当前 R2 免费额度。
```

上传图片时，Skill 会引导你确认桶、公开访问地址和对象路径；查询额度时，优先以 Cloudflare 控制台的 Billable Usage 为准。

<a id="boundary"></a>
## 费用与安全边界

1. R2 免费额度按月计算；超出免费额度、使用非 Standard 存储或启用其他收费产品，都可能进入计费范围。
2. 信用卡、PayPal、API Token 和 Secret Key 应保存在安全的账户或环境变量中，不写入仓库、命令行历史或聊天记录。
3. `r2.dev` 公开地址定位为低频、开发用途；高流量网站应使用自定义域名，并单独评估 CDN 成本。
4. 公共桶中的对象任何人都可以读取，请仅上传适合公开访问的文件。

<a id="metrics"></a>
## 免费额度查询

脚本读取 Cloudflare GraphQL Analytics，用于估算当前月的 R2 操作量和存储消耗：

```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="account-analytics-read-token"
export R2_BUCKET="your-bucket-name"
python3 scripts/r2_usage.py
```

API Token 需要 `Account → Account Analytics → Read` 权限。脚本结果是估算值，实际费用以 Cloudflare **Billable Usage** 为准。

## 官方资料

- [R2 定价与免费额度](https://developers.cloudflare.com/r2/pricing/)
- [R2 公共存储桶](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [R2 上传对象](https://developers.cloudflare.com/r2/objects/upload-objects/)
- [R2 Metrics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)
- [Cloudflare GraphQL Analytics Token](https://developers.cloudflare.com/analytics/graphql-api/getting-started/authentication/api-token-auth/)

<a id="license"></a>
## 许可证

[MIT](./LICENSE)

<a id="feedback"></a>
## 反馈

欢迎通过 [GitHub Issues](https://github.com/xue-xiaobao/cloudflare-r2/issues) 报告问题或提出改进建议。提交前请移除凭据、个人信息和内部项目名。
