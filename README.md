# Loco 认证课

这是一份给已经会用 Loco 的人看的中文课，外加它讲解的 `saas_app` 源码。生成器是已发布的 `loco` 1.3.1，旗标为 sqlite、async、serverside。认证流程保持脚手架原样。

已公开的源码提交是 [`9d99c8f53a63dc9b4c7582ec9dc061f141ee1f86`](https://github.com/penanegrarenea-ship-it/loco-auth-course/commit/9d99c8f53a63dc9b4c7582ec9dc061f141ee1f86)。这是应用源码，不是课程站点。

课程静态页在 `docs/`，准备用 GitHub Pages 的 `/docs` 目录。本页不声称站点已经构建成功或可以打开。Pages 只托管这些页面，不能执行 Rust API。接口要在本机跑。静态图 `saas_app/assets/static/image.png` 不在该源码提交里。

开发配置里的 JWT 默认值是教学占位，解码后的 ASCII 是 `dev-only-placeholder`。不要用它部署后端。

## 许可

生成出的应用来自 [Loco](https://github.com/loco-rs/loco) tag `v1.3.1`，提交 [`3ddc279740ebf0516403ca8f7028ce481d616a02`](https://github.com/loco-rs/loco/commit/3ddc279740ebf0516403ca8f7028ce481d616a02)，Apache License 2.0。见 `LICENSE` 和 `NOTICE`。

## 本机运行 API

需要 rustc 1.94 或更新。下面的命令在 Linux 上跑过，没有在 Windows 上跑过。Windows 命令见课程里的参考页。

```sh
cd saas_app
cargo loco db migrate
cargo loco routes
cargo test
PORT=43123 BINDING=127.0.0.1 cargo loco start
```

`config/development.yaml` 里 `mailer.stub` 为 true，进程不连接 SMTP。说明在 `repro/scaffold-adjustments.md`。

不要启动生产配置，不要填写真实邮箱账号。
