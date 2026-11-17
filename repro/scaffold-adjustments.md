# 相对生成器的改动

Rust 控制器、模型和迁移没有重写。改动只有这些：

1. `saas_app/config/development.yaml` 增加 `mailer.stub: true`。`smtp.enable` 仍是生成器的 `true`。`stub` 为真时框架直接使用内存 mailer，不连接 SMTP。上游：`src/boot.rs` 的 `create_mailer`。
2. 开发和测试配置的 `auth.jwt.secret` 改为 `JWT_SECRET`。未设置时使用教学占位 `ZGV2LW9ubHktcGxhY2Vob2xkZXI=`（标准 Base64，解码后是 `dev-only-placeholder`）。生成器原来的随机值没有进入公开仓库。不要用这个占位部署后端。生产配置本来就没有默认值。
3. `saas_app/src/fixtures/users.yaml` 的 `password` 和 `api_key` 改成带 `dev-only-placeholder` 的占位，不再保存密码哈希或生成的 api key。`tests/models/users.rs` 的 `can_reset_password` 改为先确认占位不能通过 `verify_password`，再调用 `reset_password` 检查新哈希。`cargo test` 仍是 28 项通过。
4. 生成命令在已有 git 目录里多了 `--allow-in-git-repo`。在 Linux 上显式写了 `--os linux`，这与该平台默认值相同。Windows 11 省略 `--os` 会多出 `src/bin/tool.rs`。这次没有编译 Windows 产物。
5. `loco` 1.3.1 没有 `--template`。`--db`、`--bg`、`--assets` 都给齐时不弹模板菜单，结果与 “Saas App with server side rendering” 加 sqlite 和 async 相同。

`cargo test` 使用的明文口令只存在于测试代码里，用来注册临时用户。它们不是 fixture 里的哈希。
