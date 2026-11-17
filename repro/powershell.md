# Windows 11 上的复现命令

下面是给 Windows 11 PowerShell 的命令。本仓库的编译、迁移、`cargo test` 和 HTTP 探针都在 Linux 上跑过，没有在 Windows 上跑过。Windows 只做了生成器文件差异对比（Linux 上用 `--os windows` 再生成一棵树，没有编译）。

需要 rustc 1.94 或更新。`loco` 1.3.1 的 MSRV 是 1.94。本机镜像自带的 1.83.0 不能编译这个生成器。

```powershell
rustc --version
cargo install loco --version 1.3.1 --locked
loco --version
loco new --help
```

`loco --version` 应打印 `loco 1.3.1`。

在一个还不是 git 仓库的空目录里，用户给出的命令可以直接用。要得到和本仓库相同的 Linux 生成树（没有 `src/bin/tool.rs`），在 Windows 上必须写明 `--os linux`。省略 `--os` 时 Windows 默认是 `windows`。

```powershell
loco new --name saas_app --db sqlite --bg async --assets serverside --os linux
Set-Location saas_app
```

如果当前目录已经在 git 仓库里，生成器会提问并默认中止。那时再加 `--allow-in-git-repo`。这个旗标不改变生成出的业务代码。

生成器会在 `config/development.yaml` 和 `config/test.yaml` 写入随机 `auth.jwt.secret`。不要把那两行提交，也不要贴出来。改成读取环境变量，或在启动前设置 `JWT_SECRET`。值必须是标准 Base64（框架会先 Base64 解码再做 HMAC）。生产配置没有默认值。

```powershell
# 换成你自己的标准 Base64。不要使用仓库里的教学占位值做任何共享环境。
$env:JWT_SECRET = "<standard-base64>"
$env:PORT = "43123"
$env:BINDING = "127.0.0.1"
```

开发配置若仍是生成器原样，`smtp.enable` 为 true 且没有 `stub: true`，注册会去连 `localhost:1025`。把 `mailer.stub: true` 写上，或只跑测试配置。不要去填真实 SMTP 账号。

```powershell
cargo loco db migrate
cargo loco routes
cargo test
cargo loco start
```

预期：

- `db migrate` 日志里出现 `Applying migration 'm20220101_000001_users'`，再次执行则是 `No pending migrations`。
- `routes` 列出 `GET /`、`GET /_health`、`GET /_ping`、`GET /_readiness`，以及文末那 9 个 `/api/auth` 路由。没有 refresh 路由。
- `cargo test` 在 Linux 上是 28 passed。Windows 上数字应相同，但这次没有 Windows 实测。
- `start` 打印 `listening on http://127.0.0.1:43123`。`cargo loco version` 在未设置 `BUILD_SHA` 时是 `0.1.0 (dev)`。

另开一个 PowerShell，只看状态码。下面用占位邮件，密码放在变量里，不要 `Write-Host` 密码或 token。

```powershell
$base = "http://127.0.0.1:43123"
$pw = "<synthetic-password>"
Invoke-WebRequest "$base/_health" | Select-Object StatusCode, Content
# 预期: 200, {"ok":true}
$body = @{ name = "Main Student"; email = "student-main@example.com"; password = $pw } | ConvertTo-Json
Invoke-WebRequest "$base/api/auth/register" -Method POST -ContentType "application/json" -Body $body | Select-Object StatusCode, Content
# 预期: 200, 正文 null
Invoke-WebRequest "$base/api/auth/current" | Select-Object StatusCode, Content
# 预期: 失败，HTTP 401，JSON error=unauthorized，description 为固定的无权限英文句子
```

登录成功时响应里有 `token`。不要把响应原文记进日志。用完即丢。验证、重置、magic link 的材料在 SQLite 列里，不在 HTTP 响应里；读取后只保留状态码。

SQLite 架构（没有行数据）：

```powershell
sqlite3 saas_app_development.sqlite "PRAGMA table_info(users);"
sqlite3 saas_app_development.sqlite "PRAGMA index_list(users);"
sqlite3 saas_app_development.sqlite "PRAGMA index_info('sqlite_autoindex_users_1');"
sqlite3 saas_app_development.sqlite "PRAGMA index_info('sqlite_autoindex_users_2');"
```

Linux 上这两条唯一索引分别是 `email` 和 `api_key`。
