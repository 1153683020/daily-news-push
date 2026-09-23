# Daily News Push

每日北京时间 07:00 推送国内/国际热点到企业微信群。

## 配置

在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

- `TAVILY_API_KEY`
- `WECHAT_WEBHOOK`

## 触发

- 定时：UTC 23:00，对应北京时间次日 07:00
- 手动：Actions → Daily News Push → Run workflow

## 配额

每天约 2~4 次 Tavily 调用，每月约 60~120 次，远低于 1000 次上限。

## 保活

公共仓库连续 60 天无提交会禁用定时任务，`keepalive.yml` 会定期保活。