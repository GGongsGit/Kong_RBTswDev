# -*- coding: utf-8 -*-
"""
로봇SW개발기사 실기 노트 빌드 스크립트

  src/template.html  : 페이지 본문 (예제 코드 자리는 {{파일명.py|설명}} 으로 표시)
  src/snip/*.py      : 페이지에 들어가는 예제 코드 (각각 단독 실행 가능)
  src/snip/sol/*.py  : 실기 예상 문제 모범 답안
  src/problems/      : 예상 문제 입력 파일과 출력 결과(*_expected.txt)

자리표시자
  {{파일.py|설명}}            → 코드 블록 (src/snip 기준 경로, 예: sol/q11_1.py)
  {{file:경로|설명}}          → 텍스트 파일 내용 블록 (src 기준 경로, 예: problems/q22_1_input.txt)
  {{html:경로}}              → HTML 조각을 그대로 넣음 (예: problems/q22_1_explain.html)
  {{img:경로|대체 글}}        → 이미지를 data URI로 넣음 (src 기준 경로, 예: img/sample_joint_chart.png)

예상 문제 답안을 고쳤으면 먼저  python tools/check_solutions.py  로 출력 결과를 다시 만든다.

실행:  python build.py
결과:
  robot_sw_exam.html        : 브라우저로 바로 여는 완성본 (doctype, charset 포함)
  dist/artifact_body.html   : claude.ai 아티팩트 게시용 본문 (doctype 없음)
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src" / "template.html"
SNIP = ROOT / "src" / "snip"
OUT_LOCAL = ROOT / "robot_sw_exam.html"
OUT_BODY = ROOT / "dist" / "artifact_body.html"


def code_block(match):
    name, caption = match.group(1).strip(), match.group(2).strip()
    path = SNIP / name
    if not path.exists():
        sys.exit(f"예제 파일이 없습니다: {path}")
    code = path.read_text(encoding="utf-8-sig").rstrip()
    return (
        '<div class="code"><div class="bar2">'
        f"<span>{html.escape(caption)} · {html.escape(name)}</span>"
        '<button type="button">복사</button></div>'
        f'<pre><code class="language-python">{html.escape(code, quote=False)}</code></pre></div>'
    )


def file_block(match):
    rel, caption = match.group(1).strip(), match.group(2).strip()
    path = ROOT / "src" / rel
    if not path.exists():
        sys.exit(f"파일이 없습니다: {path}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp949")
    lines = text.rstrip().splitlines()
    if len(lines) > 16:                                   # 긴 파일은 앞 10줄 + 끝 2줄만
        lines = lines[:10] + [f"… (중간 {len(lines) - 12}줄 생략, 전체 {len(lines)}줄)"] + lines[-2:]
    return (
        '<div class="iofile"><div class="bar2">'
        f"<span>{html.escape(caption)}</span></div>"
        f"<pre>{html.escape(chr(10).join(lines), quote=False)}</pre></div>"
    )


def img_block(match):
    import base64, mimetypes
    rel, alt = match.group(1).strip(), match.group(2).strip()
    path = ROOT / "src" / rel
    if not path.exists():
        sys.exit(f"이미지가 없습니다: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:{mime};base64,{data}" alt="{html.escape(alt)}" loading="lazy">'


def html_block(match):
    path = ROOT / "src" / match.group(1).strip()
    if not path.exists():
        sys.exit(f"HTML 조각이 없습니다: {path}")
    return path.read_text(encoding="utf-8-sig")


SUB = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜᵢⱼᵣᵤᵥ"
SUB_MAP = str.maketrans(SUB, "0123456789+-=()aeoxhklmnpstijruv")
TALL = set("θJbdfhklt" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_SKIP = re.compile(r'(<script.*?</script>|<style.*?</style>|<div class="code">.*?</pre></div>|<[^>]+>)', re.S)


def fix_dots(body):
    """q̇·q̈처럼 결합 점과 ₁·₂ 같은 아래 첨자 문자를 HTML로 바꿈.
    q̇·q̈처럼 결합 점(U+0307/U+0308)이 붙은 글자를 CSS 점으로 바꿈.
    결합 문자는 글꼴에 따라 점이 옆으로 밀려 보이기 때문.
    스크립트·스타일·태그 속성·복사 버튼이 있는 코드 블록은 그대로 둔다."""
    def conv(text):
        def r(m):
            ch, mark = m.group(1), m.group(2)
            cls = "ov2" if mark == "\u0308" else "ov1"
            if ch in TALL:
                cls += " tall"
            return f'<span class="{cls}">{ch}</span>'
        text = re.sub(r"(\w)([\u0307\u0308])", r, text)
        # 아래 첨자 문자(₀~₉ 등)는 글꼴에 따라 아주 작거나 안 보이므로 <sub>로 바꿈
        return re.sub(f"[{SUB}]+", lambda m: "<sub>" + m.group(0).translate(SUB_MAP) + "</sub>", text)
    parts = _SKIP.split(body)
    return "".join(p if i % 2 else conv(p) for i, p in enumerate(parts))


def main():
    body = SRC.read_text(encoding="utf-8-sig")
    body = re.sub(r"\{\{img:([^|}]+)\|([^}]+)\}\}", img_block, body)
    body = re.sub(r"\{\{file:([^|}]+)\|([^}]+)\}\}", file_block, body)
    body = re.sub(r"\{\{([^|}]+)\|([^}]+)\}\}", code_block, body)
    body = re.sub(r"\{\{html:([^}]+)\}\}", html_block, body)   # 상세 설명 HTML 조각 그대로 삽입
    body = fix_dots(body)
    left = re.findall(r"\{\{[^}]*\}\}", body)
    if left:
        sys.exit(f"치환되지 않은 자리표시자: {left}")
    body = body.replace("\ufffd", "&#xFFFD;")          # 깨진 글자 예시는 HTML 엔티티로

    OUT_BODY.parent.mkdir(exist_ok=True)
    OUT_BODY.write_text(body, encoding="utf-8")

    local = (
        "<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )
    OUT_LOCAL.write_text(local, encoding="utf-8")
    n = len(list(SNIP.glob("*.py")))
    q = len(list((SNIP / "sol").glob("q*.py")))
    print(f"완료: {OUT_LOCAL.name}, dist/{OUT_BODY.name}  (예제 {n}개, 예상 문제 답안 {q}개)")


if __name__ == "__main__":
    main()
