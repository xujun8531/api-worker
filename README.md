🛠️ 第一部分：Worker 后端部署 (Cloudflare)
这是你的“云端中心”，负责接收、存储并下发优选后的 IP。

1. 准备工作
创建 KV：在 Cloudflare 控制台 -> 存储与数据库 -> KV，创建一个命名空间。

绑定 KV：在 Worker 的设置 (Settings) -> 变量 (Variables) -> KV 命名空间绑定中，添加绑定：

变量名称：MY_KV

KV 空间：选择你刚才创建的那个。

设置环境变量：在同一页面添加以下变量：

TOKEN：你的专属通信令牌（例如 user1）。

ADMIN_PASSWORD：上传时校验的管理员密码。
🚀 第二部分：Python 上传工具使用指南
这是你本地运行的客户端，负责“测速、挑选、同步”。

1. 环境准备
Python 环境：确保电脑安装了 Python 3，并安装请求库：pip install requests。

必要文件：请确保以下文件放在同一个文件夹内：

sync_tool.py（Python 脚本）

cfst.exe（CloudflareSpeedTest 测速工具）

ip.txt / ipv6.txt（待扫描的 IP 段库）

2. 初始化配置 (首次运行)
双击运行脚本后，程序会进入配置流程：

上传域名：输入你的 Worker 域名（例如 xx.workers.dev）。

Token：输入你在 Worker 环境变量里设置的 TOKEN。

密码：输入对应的 ADMIN_PASSWORD。

提示：配置会自动加密保存在 config.txt。下次运行直接回车即可，无需重复输入。

3. 日常操作流程
启动测速：根据提示选择 IP 类型（IPv4/IPv6），设置线程和延迟上限。

自动同步：测速结束后，脚本会自动提取最优 IP，并通过 API 直接推送到 Worker 里的 MY_KV。

获取订阅：同步成功后，屏幕会显示：

通用订阅地址：适合各种客户端的基础地址。

Clash 专用短链接：推荐使用！ 由 suo.yt 生成，简洁稳定且已集成流媒体分流规则。

Clash 转换长链接：万能备份地址，如果短链服务不可用时使用。

⚠️ 常见问题排查
同步失败 (403/401)：请检查脚本输入的 Token 和密码是否与 Worker 环境变量完全一致。

KV 报错：请确认 Worker 控制台里的 KV 绑定名称 确实是大写的 MY_KV。

短链没出来：如果由于网络波动导致 suo.yt 访问失败，请直接复制屏幕输出的第 3 项（长链接）到 Clash 中。
