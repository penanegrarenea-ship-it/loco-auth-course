# Loco 认证课

这是一份给已经会用 Loco 的人看的中文课，外加它讲解的 `saas_app` 源码。生成器是已发布的 `loco` 1.3.1，旗标为 sqlite、async、serverside。认证流程保持脚手架原样。

课程入口是仓库里的 [`docs/index.html`](https://github.com/penanegrarenea-ship-it/loco-auth-course/blob/main/docs/index.html)。GitHub Pages 还没有打开，这个链接只打开 GitHub 上的文件，不是已经上线的网站。

离线看课：进入 `docs/`，用浏览器打开 `index.html`。样式、脚本和 12 课、4 个参考页都用相对路径，不需要后端。小测验只在浏览器里立刻对答案，不上传、不记录。

公开源码提交是 [`9d99c8f53a63dc9b4c7582ec9dc061f141ee1f86`](https://github.com/penanegrarenea-ship-it/loco-auth-course/commit/9d99c8f53a63dc9b4c7582ec9dc061f141ee1f86)。课里的行号链接指向这一次提交。课程文件提交是 [`f22cb224baeb9a5bd895d5c632d4912bf0be83e2`](https://github.com/penanegrarenea-ship-it/loco-auth-course/commit/f22cb224baeb9a5bd895d5c632d4912bf0be83e2)。所有者以后打开 Pages 的步骤在 [`docs/handoff.html`](https://github.com/penanegrarenea-ship-it/loco-auth-course/blob/main/docs/handoff.html)。保存之后要用设置页显示的地址做检查。

开发配置里的 JWT 默认值是教学占位，解码后的 ASCII 是 `dev-only-placeholder`。不要用它部署后端，也不要把这个值打到终端上。

`saas_app/assets/static/image.png` 不在公开源码提交里。首页图片因此还缺着。需要时在仓库根目录手动运行 `repro/restore-image.ps1`。它从 Loco `v1.3.1` 的固定提交下载同一字节，核对 SHA256 `fe474f23e270bf582fd8f60a87daf77e08767e5d5b60d9b618005d5d5effe279` 之后才放入该路径。应用启动不会自己下载。跑完脚本也不表示远程仓库已经有这张图。

## 许可

生成出的应用来自 [Loco](https://github.com/loco-rs/loco) tag `v1.3.1`，提交 [`3ddc279740ebf0516403ca8f7028ce481d616a02`](https://github.com/loco-rs/loco/commit/3ddc279740ebf0516403ca8f7028ce481d616a02)，Apache License 2.0。见 `LICENSE` 和 `NOTICE`。

## 本机运行 API

应用在仓库的 `saas_app/` 子目录，不在仓库根目录。需要 rustc 1.94 或更新。下面的迁移、测试和 HTTP 行为在 Linux 上核对过。Windows 11 上没有跑过这些命令。

```sh
git clone https://github.com/penanegrarenea-ship-it/loco-auth-course.git
cd loco-auth-course/saas_app
# 可选。不设置时用配置里的教学占位。不要 echo 这个值。
# export JWT_SECRET='<standard-base64>'
export PORT=43123
export BINDING=127.0.0.1
cargo run --locked -- db migrate
cargo run --locked -- routes
cargo test --locked
cargo run --locked -- start
```

`cargo install loco --version 1.3.1 --locked` 只在要重新生成一棵树时需要。

`config/development.yaml` 里 `mailer.stub` 为 true，进程不连接 SMTP。迁移写入 `saas_app` 目录下的 SQLite 文件，并应用 `m20220101_000001_users`。不要启动生产配置，不要填写真实邮箱账号。

Windows PowerShell 的同一组步骤在 `docs/reference/powershell.html`。
