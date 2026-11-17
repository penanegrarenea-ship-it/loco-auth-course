#!/usr/bin/env python3
"""Write the static course into docs/. Pass SOURCE_SHA for pinned links."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SHA = os.environ.get("SOURCE_SHA", "").strip()
if len(SHA) != 40 or any(c not in "0123456789abcdef" for c in SHA):
    sys.stderr.write("SOURCE_SHA must be the 40-character public source commit\n")
    sys.exit(2)

APP = f"https://github.com/penanegrarenea-ship-it/loco-auth-course/blob/{SHA}"
UP = "https://github.com/loco-rs/loco/blob/3ddc279740ebf0516403ca8f7028ce481d616a02"

LESSONS = [
    ("01-map", "这棵树谁负责什么"),
    ("02-columns", "users 列以 SQLite 为准"),
    ("03-register", "注册写入哪些列"),
    ("04-verify", "验证令牌没有过期"),
    ("05-login", "登录不要求已验证"),
    ("06-jwt", "JWT 与 current"),
    ("07-reset", "过期重置仍返回 200"),
    ("08-resend", "重发验证信的三种结果"),
    ("09-magic", "magic link 只收两个域名"),
    ("10-tokens", "三种令牌不要混用"),
    ("11-authz", "认证通过不等于授权"),
    ("12-old-jwt", "改密不使旧 JWT 失效"),
]
REFS = [
    ("http", "实测 HTTP 结果"),
    ("powershell", "PowerShell 命令"),
    ("untested", "没测过的边界"),
    ("extension", "还没做的 notes 设计"),
]


def app_link(path: str, start: int, end: int, label: str | None = None) -> str:
    text = label or f"{path}:{start}-{end}"
    return f'<a href="{APP}/{path}#L{start}-L{end}">{html.escape(text)}</a>'


def up_link(path: str, start: int, end: int, label: str | None = None) -> str:
    text = label or f"{path}:{start}-{end}"
    return f'<a href="{UP}/{path}#L{start}-L{end}">{html.escape(text)}</a>'


def code(text: str) -> str:
    return f"<pre><code>{html.escape(text.rstrip())}</code></pre>"


def equalize(options: list[tuple[str, str]]) -> list[tuple[str, str]]:
    width = max(len(text) for _, text in options)
    # Same character length, including at least one ideographic space,
    # so the right answer is not the longest line.
    target = width + 1
    return [(value, text + ("\u3000" * (target - len(text)))) for value, text in options]


CSS = r"""
:root {
  color-scheme: light;
  --ink: #1c1917;
  --muted: #57534e;
  --line: #d6d3d1;
  --paper: #faf7f2;
  --card: #fffdf8;
  --accent: #1e3a5f;
  --ok: #14532d;
  --no: #7f1d1d;
  --code: #f3eee6;
}
* { box-sizing: border-box; }
html { font-size: 100%; }
body {
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: "Segoe UI", "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  line-height: 1.65;
}
a { color: var(--accent); }
a:focus-visible, button:focus-visible, summary:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}
.skip {
  position: absolute;
  left: 0.5rem;
  top: -3rem;
  background: var(--card);
  padding: 0.4rem 0.7rem;
}
.skip:focus { top: 0.5rem; }
.wrap {
  width: min(1080px, calc(100% - 2rem));
  margin: 0 auto;
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  gap: 1.5rem;
  padding: 1.25rem 0 3rem;
}
header.site {
  grid-column: 1 / -1;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.8rem;
}
header.site p { margin: 0.2rem 0 0; color: var(--muted); }
nav ol { list-style: none; padding: 0; margin: 0; }
nav li { margin: 0.15rem 0; }
nav a { text-decoration: none; }
nav a[aria-current="page"] { font-weight: 700; text-decoration: underline; }
h1 { font-size: 1.7rem; line-height: 1.25; margin: 0 0 0.6rem; }
h2 { font-size: 1.15rem; margin: 1.4rem 0 0.4rem; }
.kicker { color: var(--muted); margin-top: 0; }
pre {
  background: var(--code);
  border: 1px solid var(--line);
  padding: 0.8rem 1rem;
  overflow: auto;
  font-size: 0.92rem;
  line-height: 1.45;
}
code, pre { font-family: "Cascadia Code", "Sarasa Mono SC", Consolas, "Source Han Mono", monospace; }
table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
th, td { border: 1px solid var(--line); padding: 0.35rem 0.5rem; text-align: left; vertical-align: top; }
th { background: var(--code); }
.quiz { border: 1px solid var(--line); background: var(--card); padding: 0.8rem 1rem 1rem; margin-top: 1.2rem; }
.quiz label { display: block; margin: 0.35rem 0; }
.choice { white-space: pre-wrap; }
button {
  font: inherit;
  background: var(--accent);
  color: white;
  border: 0;
  padding: 0.4rem 0.9rem;
  margin-top: 0.4rem;
}
.feedback { min-height: 1.4em; font-weight: 650; }
.feedback.ok { color: var(--ok); }
.feedback.no { color: var(--no); }
.pager { display: flex; justify-content: space-between; gap: 1rem; margin-top: 1.5rem; }
.ask { color: var(--muted); }
footer { color: var(--muted); font-size: 0.9rem; margin-top: 2rem; }
@media (max-width: 800px) {
  .wrap { grid-template-columns: 1fr; width: min(100% - 1.25rem, 42rem); }
  nav { border: 1px solid var(--line); padding: 0.4rem 0.7rem; background: var(--card); }
}
@media print {
  body { background: white; }
  .skip, button, nav { display: none; }
  .wrap { display: block; width: auto; }
  a { color: black; text-decoration: underline; }
  pre, .quiz { break-inside: avoid; }
}
"""

JS = r"""
document.querySelectorAll("form.quiz").forEach((form) => {
  const out = form.querySelector(".feedback");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const picked = form.querySelector("input[name='choice']:checked");
    if (!picked) {
      out.className = "feedback no";
      out.textContent = "还没有选择。四个选项点一个，再按核对。";
      return;
    }
    const ok = picked.value === form.dataset.answer;
    out.className = ok ? "feedback ok" : "feedback no";
    out.textContent = ok
      ? "对。这是这次实测或源码里的结果。"
      : "不对。再看本页上面的代码和 HTTP 结果。";
  });
});
"""


def quiz(question: str, options: list[tuple[str, str]], answer: str, why: str) -> str:
    options = equalize(options)
    widths = {len(text) for _, text in options}
    if len(widths) != 1:
        raise SystemExit(f"choice lengths differ: {widths}")
    labels = []
    for value, text in options:
        labels.append(
            "<label>"
            f'<input type="radio" name="choice" value="{html.escape(value)}"> '
            f'<span class="choice">{html.escape(text)}</span></label>'
        )
    return f"""
<form class="quiz" data-answer="{html.escape(answer)}">
  <fieldset>
    <legend>{html.escape(question)}</legend>
    {''.join(labels)}
  </fieldset>
  <button type="submit">核对</button>
  <p class="feedback" role="status" aria-live="polite"></p>
  <noscript><p>不运行脚本时的答案：{html.escape(why)}</p></noscript>
</form>
"""


def nav(current: str) -> str:
    items = []
    items.append(f'<li><a href="{ "../" if current else "" }index.html">首页</a></li>')
    for slug, title in LESSONS:
        href = f"{'' if current else 'lessons/'}{slug}.html" if current else f"lessons/{slug}.html"
        if current and not current.startswith("ref-"):
            href = f"{slug}.html"
        elif current and current.startswith("ref-"):
            href = f"../lessons/{slug}.html"
        mark = ' aria-current="page"' if current == slug else ""
        items.append(f'<li><a href="{href}"{mark}>{html.escape(title)}</a></li>')
    for slug, title in REFS:
        if not current:
            href = f"reference/{slug}.html"
        elif current.startswith("ref-"):
            href = f"{slug}.html"
        else:
            href = f"../reference/{slug}.html"
        mark = ' aria-current="page"' if current == f"ref-{slug}" else ""
        items.append(f'<li><a href="{href}"{mark}>{html.escape(title)}</a></li>')
    return f'<nav aria-label="课程"><ol>{"".join(items)}</ol></nav>'


def layout(title: str, current: str, body: str, depth: int) -> str:
    prefix = "../" * depth
    home = f"{prefix}index.html"
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Loco 认证课</title>
  <link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
  <a class="skip" href="#main">跳到正文</a>
  <div class="wrap">
    <header class="site">
      <p><a href="{home}">Loco 认证课</a></p>
      <p>静态页，不运行 Rust，不收集回答。</p>
    </header>
    {nav(current)}
    <main id="main">
      {body}
      <p class="ask">还有疑问就在对话里问。这个页面没有聊天窗口，也不保存你的选择。</p>
      <footer>
        <p>源码提交 <a href="https://github.com/penanegrarenea-ship-it/loco-auth-course/commit/{SHA}">{SHA[:12]}</a>。
        框架 <a href="https://github.com/loco-rs/loco/commit/3ddc279740ebf0516403ca8f7028ce481d616a02">3ddc279740eb</a>。
        本站不能代替本机的 <code>cargo loco start</code>。</p>
      </footer>
    </main>
  </div>
  <script src="{prefix}assets/site.js"></script>
</body>
</html>
"""


def lesson(slug: str, title: str, body: str, prev: tuple[str, str] | None, nxt: tuple[str, str] | None) -> str:
    pager = ['<p class="pager">']
    if prev:
        pager.append(f'<a href="{prev[0]}.html">上一课：{html.escape(prev[1])}</a>')
    else:
        pager.append("<span></span>")
    if nxt:
        pager.append(f'<a href="{nxt[0]}.html">下一课：{html.escape(nxt[1])}</a>')
    pager.append("</p>")
    inner = f"<h1>{html.escape(title)}</h1>{body}{''.join(pager)}"
    return layout(title, slug, inner, 1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    pages: dict[str, str] = {}

    pages["01-map"] = f"""
<p class="kicker">一课只看职责，不看安装步骤。</p>
<h2>结果</h2>
{code('''App::routes
  with_default_routes()     框架：/_health /_ping /_readiness
  auth::routes()            脚手架：/api/auth/*
  page::routes()            脚手架：GET /''')}
<p>源码 {app_link("saas_app/src/app.rs", 51, 55)}。认证路由表 {app_link("saas_app/src/controllers/auth.rs", 261, 273)}。健康检查在框架 {up_link("src/controller/monitoring.rs", 104, 108)}。</p>
<h2>说明</h2>
<p>控制器决定 HTTP 状态和 JSON 形状。用户列和令牌读写在 <code>saas_app/src/models/users.rs</code>。签名、Argon2、401 外壳在 <code>loco-rs</code> 1.3.1，不在这个应用里重写。</p>
<p>迁移文件只点名业务列。真正建表时框架会再加时间戳。下一课对的是 SQLite 的 PRAGMA，不是迁移数组的字面列表。</p>
{quiz("密码比对发生在哪一层？", [
    ("a", "脚手架控制器先哈希，再把明文交给模型保存"),
    ("b", "模型调用框架 hash::verify_password 做比对"),
    ("c", "SQLite 用 UNIQUE 约束直接判断密码对错"),
    ("d", "JWT 提取器在读 Authorization 时完成比对"),
], "b", "B。比对在模型的 verify_password，它调用框架 hash::verify_password。")}
"""

    pages["02-columns"] = f"""
<p class="kicker">迁移数组和实际表不是同一张清单。</p>
<h2>结果</h2>
{code('''PRAGMA table_info(users) 的列序
created_at  timestamp_with_timezone_text  NOT NULL  DEFAULT CURRENT_TIMESTAMP
updated_at  timestamp_with_timezone_text  NOT NULL  DEFAULT CURRENT_TIMESTAMP
id          INTEGER                       NOT NULL  PRIMARY KEY AUTOINCREMENT
pid         uuid_text                     NOT NULL
email       varchar                       NOT NULL  UNIQUE
password    varchar                       NOT NULL
api_key     varchar                       NOT NULL  UNIQUE
name        varchar                       NOT NULL
其余令牌和时间列均可 NULL，且没有 UNIQUE''')}
<p>迁移手写列从 <code>id</code> 到 <code>magic_link_expiration</code>：{app_link("saas_app/migration/src/m20220101_000001_users.rs", 10, 34)}。时间戳来自框架 <code>create_table</code>：{up_link("src/schema.rs", 490, 496)} 和 {up_link("src/schema.rs", 24, 38)}。</p>
<h2>说明</h2>
<p>唯一索引只有两条自动索引：<code>email</code> 和 <code>api_key</code>。<code>pid</code> 在插入时写成 UUID，表上没有 UNIQUE。没有 <code>disabled</code>、<code>role</code>、<code>refresh_token</code> 列。完整 pragma 在 <code>repro/text/schema.txt</code>。</p>
<p>Rust 实体把 <code>id</code> 写成 <code>i64</code>：{app_link("saas_app/src/models/_entities/users.rs", 11, 12)}。文件头仍写着 sea-orm-codegen 1.0.0，lock 里的 sea-orm 是 2.0.4。以 PRAGMA 和实体字段为准。</p>
{quiz("created_at 从哪里来？", [
    ("a", "迁移数组里写了 created_at，类型是 INTEGER"),
    ("b", "框架 create_table 自动加上，带 CURRENT_TIMESTAMP"),
    ("c", "注册控制器在插入用户之前手动写入该列"),
    ("d", "SQLite 对每张表都隐式提供 created_at 列"),
], "b", "B。迁移数组没有这列。框架 create_table 会加时间戳。")}
"""

    pages["03-register"] = f"""
<p class="kicker">先看写入，再看 200 代表什么。</p>
<h2>结果</h2>
{code('''POST /api/auth/register
HTTP 200
null

同一邮箱再 POST 一次
HTTP 200
null
该邮箱的行数仍是 1''')}
<p>控制器 {app_link("saas_app/src/controllers/auth.rs", 46, 72)}。插入 {app_link("saas_app/src/models/users.rs", 233, 266)}。插入前补 <code>pid</code> 和 <code>lo-</code> 前缀的 <code>api_key</code>：{app_link("saas_app/src/models/users.rs", 45, 59)}。</p>
<h2>说明</h2>
<p>写入的业务列是邮箱、密码哈希、姓名。哈希在框架 {up_link("src/hash.rs", 24, 36)}：Argon2id，版本 0x13，默认参数 m=19456、t=2、p=1。随后 <code>set_email_verification_sent</code> 写入发送时间和一枚 UUID 验证令牌。{app_link("saas_app/src/models/users.rs", 290, 297)}。<code>email_verified_at</code> 仍是 NULL。</p>
<p>重复邮箱在模型里是 <code>EntityAlreadyExists</code>，控制器吞掉错误并返回 JSON <code>null</code>。这不是 409。注册不看邮箱域名。</p>
{quiz("重复邮箱再次注册时，实测响应是？", [
    ("a", "HTTP 409，JSON 说明这个邮箱已经注册过"),
    ("b", "HTTP 200，正文 null，表里仍然只有一行"),
    ("c", "HTTP 200，正文 null，表里变成两行同邮箱"),
    ("d", "HTTP 422，因为第二次请求缺少验证令牌"),
], "b", "B。两次都是 200 和 null，COUNT 仍为 1。")}
"""

    pages["04-verify"] = f"""
<p class="kicker">验证令牌会作废，但不会过期。</p>
<h2>结果</h2>
{code('''把 email_verification_sent_at 改成 2000-01-01 后
GET /api/auth/verify/{{token}}
HTTP 200
null

同一 token 再 GET
HTTP 401
{{"error":"unauthorized","description":"You do not have permission to access this resource"}}

POST /api/auth/verify
HTTP 404，HTML，不是 JSON''')}
<p>查找只按令牌列等值匹配：{app_link("saas_app/src/models/users.rs", 96, 109)}。成功后清空令牌：{app_link("saas_app/src/models/users.rs", 326, 331)}。路由只有 GET：{app_link("saas_app/src/controllers/auth.rs", 77, 91)}。</p>
<h2>说明</h2>
<p><code>email_verification_sent_at</code> 被写下来，但查找函数不读它。所以把发送时间拨到 2000 年，原令牌仍然 200。用过之后列变成 NULL，再请求就是 401。</p>
<p>脚手架测试辅助函数向 <code>POST /api/auth/verify</code> 发 JSON。这条路由不存在，实测 404。真正生效的测试走 GET 路径参数。</p>
{quiz("验证令牌的时间政策是哪一种？", [
    ("a", "发送超过一天就失效，接口返回 401"),
    ("b", "查找不看发送时间，用过才把令牌清空"),
    ("c", "过期后仍返回 200，同时把邮箱标成已验证"),
    ("d", "令牌留在行里，已验证用户可以反复使用"),
], "b", "B。没有过期判断。成功验证后令牌列为 NULL。")}
"""

    pages["05-login"] = f"""
<p class="kicker">注释和实测相反的地方就在这里。</p>
<h2>结果</h2>
{code('''尚未验证，密码正确
POST /api/auth/login
HTTP 200
字段：is_verified=false，另外有 token、pid、name

验证之后，密码正确
HTTP 200
is_verified=true

密码错误，或邮箱不存在
HTTP 401
同一句 unauthorized 描述，没有原文 "Invalid credentials!"''')}
<p>登录函数 {app_link("saas_app/src/controllers/auth.rs", 137, 159)}。它上面的注释 {app_link("saas_app/src/controllers/auth.rs", 74, 75)} 写未验证不能登录。响应字段 {app_link("saas_app/src/views/auth.rs", 5, 22)}。</p>
<h2>说明</h2>
<p><code>login</code> 只查邮箱和 <code>verify_password</code>。不读 <code>email_verified_at</code>。<code>is_verified</code> 只是把该列是否有值放进 JSON。脚手架测试 <code>can_login_without_verify</code> 也期望 200。</p>
<p>401 外壳来自框架，不回显控制器里的字符串：{up_link("src/controller/mod.rs", 227, 235)}。</p>
{quiz("未验证用户用正确密码登录，实测是？", [
    ("a", "HTTP 401，描述里写明邮箱还没有完成验证"),
    ("b", "HTTP 200，JSON 里 is_verified 的值是 false"),
    ("c", "HTTP 404，验证完成之前数据库里没有该用户"),
    ("d", "HTTP 403，因为验证令牌还留在用户那一行里"),
], "b", "B。未验证登录是 200，is_verified 为 false。")}
"""

    pages["06-jwt"] = f"""
<p class="kicker">先看令牌里有什么，再看 current 查了什么。</p>
<h2>结果</h2>
{code('''登录成功后解开的 JWT
header: typ=JWT, alg=HS512
claims: pid, exp
exp 与当时 unix 时间的差：604800 秒
没有额外 claim

GET /api/auth/current
缺 Authorization                         401
Bearer not-a-jwt                          401
签名段被改坏                              401
合法 Bearer                               200，字段 pid、name、email
删掉该用户后再用原 JWT                     404 not_found''')}
<p>签发 {app_link("saas_app/src/models/users.rs", 273, 277)}。框架生成与校验 {up_link("src/auth/jwt.rs", 20, 20, "HS512")}、{up_link("src/auth/jwt.rs", 161, 164, "Base64 密钥")}、{up_link("src/auth/jwt.rs", 181, 201, "generate_token")}、{up_link("src/auth/jwt.rs", 217, 248, "validate")}。过期秒数 {app_link("saas_app/config/development.yaml", 115, 115)}。</p>
<h2>说明</h2>
<p><code>current</code> 的提取器是 <code>auth::JWT</code>，只校验签名和过期，不加载用户：{up_link("src/controller/extractor/auth.rs", 106, 121)}。默认读 <code>Authorization: Bearer</code>。然后控制器自己 <code>find_by_pid</code>：{app_link("saas_app/src/controllers/auth.rs", 162, 165)}。</p>
<p>secret 必须是标准 Base64。配置里的默认值是教学占位，不要拿去部署后端。用户已删除时，提取器仍然接受签名，控制器的查询变成 404，不是 401。</p>
{quiz("合法 JWT 的 claims 里实测有哪些键？", [
    ("a", "只有 pid 和 exp，算法头是 HS512"),
    ("b", "pid、exp、role，另外还有 refresh"),
    ("c", "pid、email、password，算法头是 RS256"),
    ("d", "sub、iat、jti，另外有一个吊销编号"),
], "a", "A。claims 只有 pid 和 exp，header 的 alg 是 HS512。")}
"""

    pages["07-reset"] = f"""
<p class="kicker">200 在这里不表示密码已经换掉。</p>
<h2>结果</h2>
{code('''POST /api/auth/forgot  未知邮箱或已知邮箱都是 HTTP 200，正文 null
已知邮箱：reset_token 和 reset_sent_at 被写上

POST /api/auth/reset  错误 token：HTTP 200，旧密码仍能登录
把 reset_sent_at 改成 2000-01-01 再重置：HTTP 200
新密码登录 401，旧密码登录 200

未过期的重置：HTTP 200，两列清空，旧密码 401，新密码 200''')}
<p>忘记密码 {app_link("saas_app/src/controllers/auth.rs", 98, 116)}。重置 {app_link("saas_app/src/controllers/auth.rs", 120, 133)}。30 分钟判断 {app_link("saas_app/src/models/users.rs", 12, 12, "RESET_TOKEN_EXPIRATION_MIN")} 和 {app_link("saas_app/src/models/users.rs", 152, 180)}。成功后清空 {app_link("saas_app/src/models/users.rs", 342, 352)}。</p>
<h2>说明</h2>
<p>找不到或已过期都走进同一个分支，返回 JSON <code>null</code>，不改密码。调用方不能用状态码区分“换好了”和“令牌无效”。没有测刚好 30 分钟的边界，只测了明显过期。</p>
{quiz("重置令牌已经过期时，接口和密码分别怎样？", [
    ("a", "HTTP 401，密码保持不变，旧密码不能登录"),
    ("b", "HTTP 200，密码保持不变，旧密码仍然能登录"),
    ("c", "HTTP 200，密码改成新值，旧密码不能再登录"),
    ("d", "HTTP 404，因为过期令牌会从用户行里删除"),
], "b", "B。过期重置仍是 200，旧密码还能登录。")}
"""

    pages["08-resend"] = f"""
<p class="kicker">三种邮箱，三种数据库结果，HTTP 都是 200。</p>
<h2>结果</h2>
{code('''POST /api/auth/resend-verification-mail
未知邮箱                         200 null
已验证用户                       200 null，验证令牌仍是 NULL
未验证用户                       200 null，令牌换成新值''')}
<p>控制器 {app_link("saas_app/src/controllers/auth.rs", 230, 259)}。</p>
<h2>说明</h2>
<p>未知邮箱直接返回，避免暴露邮箱是否存在。已验证用户不再发信，也不重写令牌。未验证用户再次调用 <code>set_email_verification_sent</code>，所以令牌列会变。这次只比较了前后是否不同，没有记录令牌值。</p>
<p>进程外读不到 stub 邮箱里的正文。封数由 <code>cargo test</code> 断言：未验证重发后是 2 封，已验证后再重发仍是 1 封。</p>
{quiz("已经验证过的用户再请求重发，数据库怎样？", [
    ("a", "HTTP 409，并新写一枚验证令牌到该行"),
    ("b", "HTTP 200，验证令牌列保持 NULL 不变"),
    ("c", "HTTP 200，把 email_verified_at 重新清空"),
    ("d", "HTTP 401，因为已验证用户不能再收验证信"),
], "b", "B。已验证重发是 200，验证令牌仍为 NULL。")}
"""

    pages["09-magic"] = f"""
<p class="kicker">域名、长度、五分钟、用过即删。</p>
<h2>结果</h2>
{code('''POST /api/auth/magic-link
邮箱不以 @example.com 或 @gmail.com 结尾    400 invalid request
域名合法但没有这个用户                      200 {{}}
有这个用户                                  200 {{}}
令牌长度 32，magic_link_expiration 非空

GET /api/auth/magic-link/{{token}}
不存在                         401
未过期                         200，字段与登录相同，随后两列被清空
同一令牌再 GET                 401
过期列写成 2000-01-01          401，令牌列还在''')}
<p>域名正则 {app_link("saas_app/src/controllers/auth.rs", 16, 19)}。请求 {app_link("saas_app/src/controllers/auth.rs", 181, 205)}。兑换 {app_link("saas_app/src/controllers/auth.rs", 208, 227)}。常量 {app_link("saas_app/src/models/users.rs", 10, 11)}。</p>
<h2>说明</h2>
<p>成功请求返回的是空对象 <code>{{}}</code>，注册返回的是 <code>null</code>。这是 <code>empty_json</code> 和 <code>json(())</code> 的差别。过期失败不会清掉令牌；兑换成功会先清掉再签发 JWT。没有测刚好 5 分钟。</p>
{quiz("magic link 请求一个不存在、但域名合法的邮箱，实测是？", [
    ("a", "HTTP 404，正文说明这个邮箱还没有注册"),
    ("b", "HTTP 200，正文是空对象，且不新建用户"),
    ("c", "HTTP 400，因为只有已验证邮箱才能收链接"),
    ("d", "HTTP 200，正文 null，并插入一行空密码用户"),
], "b", "B。未知但域名合法的邮箱返回 200 和空对象。")}
"""

    pages["10-tokens"] = f"""
<p class="kicker">用途、存放、过期、消费，四列分开看。</p>
<h2>结果</h2>
<table>
  <thead><tr><th>令牌</th><th>存放</th><th>过期</th><th>消费</th></tr></thead>
  <tbody>
    <tr><td>邮箱验证</td><td>email_verification_token</td><td>不判断</td><td>验证成功后置 NULL</td></tr>
    <tr><td>重置密码</td><td>reset_token，另有 reset_sent_at</td><td>发送后 30 分钟</td><td>重置成功后两列都空</td></tr>
    <tr><td>magic link</td><td>magic_link_token，另有过期列</td><td>5 分钟</td><td>兑换成功后两列都空</td></tr>
    <tr><td>JWT</td><td>不入库，只在响应里</td><td>exp，配置 604800 秒</td><td>无服务端消费记录</td></tr>
  </tbody>
</table>
<h2>说明</h2>
<p>验证和重置的材料是 UUID 字符串。magic link 是 32 位随机字母数字。JWT 是 HS512 三段 compact。四者不能互相拿去调用对方的路由。HTTP 成功响应不回带前三种令牌，只回带 JWT。</p>
{quiz("哪一种材料写在用户表里，但查找时不看时间？", [
    ("a", "邮箱验证令牌写在表里，查找不看发送时间"),
    ("b", "重置令牌写在表里，查找时完全不看时间"),
    ("c", "magic link 写在表里，查找时不看过期列"),
    ("d", "JWT 写在用户表里，查找时不看 exp 声明"),
], "a", "A。验证令牌有发送时间列，查找函数不用它。")}
"""

    pages["11-authz"] = f"""
<p class="kicker">登录成功只证明你是这一个 pid。</p>
<h2>结果</h2>
{code('''users 表没有 disabled、role、refresh_token
登录和 current 不读这些不存在的列
LoginResponse 没有 refresh 字段
改密、退出、按角色拒绝：这些路由不存在

框架源码里有 session store，可以按用户撤销会话。
生成出的 App::routes 没有接上那些路由。''')}
<p>列清单见 {app_link("saas_app/migration/src/m20220101_000001_users.rs", 10, 34)} 和 <code>repro/text/schema.txt</code>。路由表 {app_link("saas_app/src/controllers/auth.rs", 261, 273)}。</p>
<h2>说明</h2>
<p>认证回答“这个签名是不是这个 pid”。授权回答“这个 pid 能不能做这件事”。当前路由没有第二问。持有有效 JWT 就能读 <code>/api/auth/current</code>，没有角色可以挡。</p>
<p><code>api_key</code> 会在插入时生成，但这些 HTTP 路由不用它登录。框架的 <code>ApiToken</code> 提取器没有接到生成的路由上。</p>
{quiz("这棵生成代码里，授权能力实际是？", [
    ("a", "JWT 里带 role，current 会按角色返回不同字段"),
    ("b", "没有角色或禁用检查，有效 JWT 就能读 current"),
    ("c", "refresh 路由负责授权，过期前必须先刷新"),
    ("d", "session store 已接上，改密会撤销全部会话"),
], "b", "B。没有角色或禁用检查。有效 JWT 可以读 current。")}
"""

    pages["12-old-jwt"] = f"""
<p class="kicker">密码换了，签过名的 JWT 还在有效期内。</p>
<h2>结果</h2>
{code('''1. 登录，留下 JWT，不把它写进任何公开记录
2. 完成一次未过期的密码重置
3. 旧密码登录变为 401，新密码登录为 200
4. 用第 1 步的 JWT 调用 GET /api/auth/current
   HTTP 200''')}
<p>JWT 校验只看签名、算法、过期和意外的 <code>aud</code>：{up_link("src/auth/jwt.rs", 217, 248)}。没有 <code>jti</code>，用户表也没有吊销列表。</p>
<h2>说明</h2>
<p><code>reset_password</code> 只换哈希并清空重置列。它不修改已经发出的 JWT，<code>current</code> 也不比较“令牌签发时的密码版本”。所以改密不能当作注销。</p>
<p>用户行被删掉是另一条路径：签名仍有效，但 <code>find_by_pid</code> 得到 404。那是行不在了，不是令牌被吊销。</p>
{quiz("密码重置成功后，重置前签发的 JWT 调用 current，实测是？", [
    ("a", "HTTP 401，因为密码版本已经变了，签名失效"),
    ("b", "HTTP 200，因为校验不看密码是否后来换过"),
    ("c", "HTTP 404，重置会删掉用户行并要求重新注册"),
    ("d", "HTTP 409，旧 JWT 必须先调用不存在的吊销口"),
], "b", "B。改密后旧 JWT 调 current 仍是 200。")}
"""

    order = LESSONS
    html_by_slug = {}
    for index, (slug, title) in enumerate(order):
        prev = (order[index - 1][0], order[index - 1][1]) if index else None
        nxt = (order[index + 1][0], order[index + 1][1]) if index + 1 < len(order) else None
        html_by_slug[slug] = lesson(slug, title, pages[slug], prev, nxt)

    home_items = "".join(
        f'<li><a href="lessons/{slug}.html">{html.escape(title)}</a></li>' for slug, title in LESSONS
    )
    ref_items = "".join(
        f'<li><a href="reference/{slug}.html">{html.escape(title)}</a></li>' for slug, title in REFS
    )
    home = f"""
<h1>看这棵 saas_app 实际做了什么</h1>
<p class="kicker">给已经会生成 Loco 应用的人。每课先放代码或 HTTP 结果，再解释。不教安装，也不教一套新的 CRUD。</p>
<p>页面由 GitHub Pages 托管。它不能注册、不能登录、不能签发 JWT。Rust API 在本机用 <code>cargo loco start</code> 跑。开发配置里的 JWT 默认值是教学占位，不要用它部署后端。</p>
<h2>课</h2>
<ol>{home_items}</ol>
<h2>参考</h2>
<ul>{ref_items}</ul>
<p>公开源码提交是 <a href="https://github.com/penanegrarenea-ship-it/loco-auth-course/commit/{SHA}">{SHA}</a>。私有草稿基线是 <code>44039154416aed32ce4a96a901d26ec6f2e9c9c8</code>，那条历史不在这个仓库里。</p>
"""
    index = layout("首页", "", home, 0)

    http_ref = layout("实测 HTTP 结果", "ref-http", f"""
<h1>实测 HTTP 结果</h1>
<p>Linux 上对 <code>127.0.0.1:43123</code> 的探针。账号使用 example.com。口令、令牌、哈希、api key 和 JWT 没有留在结果里。</p>
<pre><code>{html.escape((ROOT / "repro/text/http-results.txt").read_text())}</code></pre>
<p><code>cargo test</code> 28 项通过，名单在仓库 <code>repro/text/test-results.txt</code>。那是测试进程，不是这个网站。</p>
""", 1)

    ps_ref = layout("PowerShell 命令", "ref-powershell", f"""
<h1>PowerShell 命令</h1>
<p>这些命令没有在 Windows 上执行。Linux 上用对应的环境变量和 curl 核对过行为。</p>
{code('''rustc --version
cargo install loco --version 1.3.1 --locked
loco new --name saas_app --db sqlite --bg async --assets serverside --os linux
Set-Location saas_app
$env:JWT_SECRET = "<standard-base64>"
$env:PORT = "43123"
$env:BINDING = "127.0.0.1"
cargo loco db migrate
cargo loco routes
cargo test
cargo loco start''')}
<p>要得到与公开树相同的文件，Windows 上必须写 <code>--os linux</code>。省略时默认是 <code>windows</code>，会多出 <code>src/bin/tool.rs</code>。本次没有编译那棵树。</p>
<p>预期：迁移日志出现 <code>m20220101_000001_users</code>；<code>routes</code> 含 9 个 <code>/api/auth</code> 路径以及 <code>/_health</code>、<code>/_ping</code>、<code>/_readiness</code> 和 <code>GET /</code>；<code>start</code> 监听所设端口。登录响应里的 token 不要记下来。</p>
""", 1)

    untested = layout("没测过的边界", "ref-untested", """
<h1>没测过的边界</h1>
<ul>
  <li>Windows 编译、<code>cargo test</code> 和 PowerShell 实际执行。</li>
  <li><code>--os windows</code> 那棵树的编译。只比较过文件差。</li>
  <li>生产配置启动，以及任何真实 SMTP。</li>
  <li>重置令牌刚好 30 分钟、magic link 刚好 5 分钟。</li>
  <li>stub 邮件的正文和链接格式。进程外读不到那封信，测试只断言封数，正文快照是注释掉的。</li>
  <li><code>DownloadWorker</code> 的任务执行。它被注册了，<code>tests/workers/mod.rs</code> 是空模块。</li>
  <li>框架里的 session 和 OAuth。生成的路由没有接上。</li>
  <li>把用户标成禁用后再登录。没有这个列，做不了这个实验。</li>
</ul>
<p>已经测过的相反事实：未验证可以登录；过期重置返回 200 且不改密码；验证令牌没有过期；magic link 有域名限制；改密后旧 JWT 仍能读 current。</p>
""", 1)

    extension = layout("还没做的 notes 设计", "ref-extension", f"""
<h1>还没做的 notes 设计</h1>
<p>下面不是已实现的接口。仓库里没有 <code>notes</code> 表，也没有 <code>/api/notes</code>。</p>
{code('''新迁移，不改 users 的列
notes
  id          框架的 PkAuto
  user_id     非空，指向 users.id，不是 pid
  body        非空文本
  created_at / updated_at    create_table 会再加

POST /api/notes    要 Bearer
GET  /api/notes    只返回这个 user_id 的行''')}
<p>现有 JWT 只有 <code>pid</code>。处理请求时用 {app_link("saas_app/src/models/users.rs", 187, 198, "find_by_pid")} 找到 <code>users.id</code>，再写 <code>notes.user_id</code>。不要把 <code>user_id</code> 放进 claims，这样旧 JWT 仍然可用。</p>
<h2>授权例子</h2>
<p>正向：A 的 JWT 创建的笔记，A 再去列表里看得到，因为查询条件是 A 的 <code>users.id</code>。</p>
<p>反向：B 拿自己的有效 JWT 去要 A 的笔记，签名是对的，但 <code>user_id</code> 对不上，结果应是空列表或 404。这是授权，不是再做一次登录。当前应用没有这个判断，因为笔记还不存在。</p>
<p>已有的 <code>/api/auth/*</code>、<code>/_health</code>、<code>/_ping</code>、<code>/_readiness</code>、<code>GET /</code> 都不必改。</p>
""", 1)

    if DOCS.exists():
        for old in DOCS.rglob("*"):
            if old.is_file() and old.suffix == ".md":
                old.unlink()
    write(DOCS / "assets" / "site.css", CSS)
    write(DOCS / "assets" / "site.js", JS)
    write(DOCS / ".nojekyll", "")
    write(DOCS / "index.html", index)
    for slug, _title in LESSONS:
        write(DOCS / "lessons" / f"{slug}.html", html_by_slug[slug])
    write(DOCS / "reference" / "http.html", http_ref)
    write(DOCS / "reference" / "powershell.html", ps_ref)
    write(DOCS / "reference" / "untested.html", untested)
    write(DOCS / "reference" / "extension.html", extension)

    missing = []
    for page in DOCS.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        root = page.parent
        for raw in text.split('href="'):
            if raw.startswith("http") or raw[:1] not in (".", "a", "l", "r", "i"):
                continue
            href = raw.split('"', 1)[0]
            if href.startswith("http"):
                continue
            target = (root / href).resolve()
            if not target.exists():
                missing.append(f"{page.relative_to(DOCS)} -> {href}")
    if missing:
        raise SystemExit("missing links:\n" + "\n".join(missing))
    print(f"wrote {DOCS} pinned to {SHA}")


if __name__ == "__main__":
    main()
