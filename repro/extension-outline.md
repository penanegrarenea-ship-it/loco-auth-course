# 一个还没做的最小扩展

不改认证。给已登录用户加一张自己的 `notes` 表，只包含 id、所属用户、正文和时间戳。

## 模型与迁移

- 新迁移，例如 `migration/src/m20220101_000002_notes.rs`，并在 `migration/src/lib.rs` 的 `migrations()` 里挂上。保留 `inject-above` 注释。
- 列：`create_table` 会再补 `created_at` / `updated_at`。显式列用 `id`（`PkAuto`）、`user_id`（指向 `users.id` 的 64 位整数，非空）、`body`（text，非空）。
- 不要把 `user_id` 做成 JWT claim。现有 token 只有 `pid` 和 `exp`。接口用 `auth::JWT` 取出 `pid`，再 `users::Model::find_by_pid`，用查到的 `users.id` 写入 `notes.user_id`。
- `users` 表不加列。已有账号、验证令牌、重置令牌、magic link、JWT 都不用迁移数据。

## 接口

- `POST /api/notes`，JSON `{ "body": "..." }`，需要 `Authorization: Bearer`。
- `GET /api/notes`，只返回当前 `user_id` 的行。
- 路由加在新控制器里，由 `App::routes` 再 `add_route`。不要改 `controllers/auth.rs` 的 `routes()`。

## 兼容

- 现有 `/api/auth/*`、`/_health`、`/_ping`、`/_readiness`、`GET /` 的路径和响应字段不变。
- 旧 JWT 继续可用：claims 没有新字段，签名算法仍是 HS512。
- 未登录访问新接口应得到与 `/api/auth/current` 缺 token 时相同的 401 外壳。这是框架 `Error::Unauthorized` 的固定文案，不是新协议。
- SQLite 上先加表，不改 `users` 的 UNIQUE(email) 和 UNIQUE(api_key)。

这次没有生成该迁移，也没有新路由。
