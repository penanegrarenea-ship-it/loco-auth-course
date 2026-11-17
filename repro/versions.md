# 版本

| 项 | 值 |
| --- | --- |
| 生成器 | `loco` 1.3.1，2026-11-06 发布 |
| 生成器 crates.io checksum | `dd67834a4e55b94bb3c285747ffd7906eac791020e4599bfc48068206f04f6ba` |
| 框架 | `loco-rs` 1.3.1 |
| 框架 checksum（Cargo.lock） | `8aa30671d3a487b08a61cec5e9d9b9764cdf73e7df074fd1618811935214e076` |
| 上游提交 | [`3ddc279740ebf0516403ca8f7028ce481d616a02`](https://github.com/loco-rs/loco/commit/3ddc279740ebf0516403ca8f7028ce481d616a02) |
| 注释 tag 对象 | `ff90c4258957b64378c7170fa465043a0c0e520b` |
| 生成清单里的要求 | `loco-rs = { version = "1.3" }` |
| 应用版本 | `0.1.0`；未设置 `BUILD_SHA` 时 `cargo loco version` 打印 `0.1.0 (dev)` |
| 核对用的 rustc | 1.100.0（`0ef1bc386`，2026-11-09） |
| sea-orm | 2.0.4 |
| argon2 | 0.5.3 |

公开源码提交是 `9d99c8f53a63dc9b4c7582ec9dc061f141ee1f86`。课里的行号链接指向这一次提交。

框架行号核对过 crates.io 上的 `loco-rs` 1.3.1，并确认这些路径在上游提交上返回 200：`src/auth/jwt.rs`、`src/hash.rs`、`src/boot.rs`、`src/schema.rs`、`src/controller/monitoring.rs`、`src/controller/extractor/auth.rs`、`src/controller/mod.rs`。
