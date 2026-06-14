# CLAUDE.md

## 包管理策略（必需遵循）

本机是 **MacBook Air 2015，macOS Monterey 12.7.6**（系统已到顶）。Homebrew 不为此旧系统提供预编译 bottle。

**安装任何软件包时，严格按以下优先级**：

1. **MacPorts（最高优先级）**：`port search <pkg>` → `sudo port install <pkg>`
   - 走清华 ports 树 + USTC 二进制包，秒装不编译
   - ports 树路径：`/opt/local/var/macports/sources/mirrors.tuna.tsinghua.edu.cn/macports/release/tarballs/ports/`
   - 不要运行 `port selfupdate`（rsync被封，会卡住）
   
2. **Go 工具**：`GOPROXY=https:https://goproxy.cn,direct go install <path>@latest`
   - 示例：`go install github.com/cli/cli/v2/cmd/gh@latest`
   
3. **Python 包**：`pip3 install -i https:https://mirrors.ustc.edu.cn/pypi/web/simple <pkg>`

4. **Homebrew（仅备选）**：仅当 MacPorts 没有时使用，接受源码编译
   - 已配 USTC 镜像但 Monterey 无 bottle

**检查已安装**：先 `which <cmd>` 或 `port installed | grep <pkg>`，避免重复装。

## Python 版本

始终使用 Python 3.11：`/usr/local/bin/python3.11`

## 系统信息

- macOS Monterey 12.7.6 (Darwin 21.6.0)
- MacBookAir7,2 (Intel x86_64)
- 系统无法再升级（硬件限制）
