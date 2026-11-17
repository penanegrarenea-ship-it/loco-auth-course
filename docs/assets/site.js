
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
