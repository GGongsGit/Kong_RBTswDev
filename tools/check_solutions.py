# -*- coding: utf-8 -*-
"""
예상 문제 모범 답안을 모두 실행해서 결과를 src/problems/<문제>_expected.txt 로 저장한다.
답안 코드 안의 C:\KONG_2027Prg\RBTSW_Results\ 경로는 임시 폴더로 바꿔서 실행하므로
실제 결과 폴더는 건드리지 않는다.

실행:  python tools/check_solutions.py          (전체)
       python tools/check_solutions.py q22_1    (하나만)
"""
import os, pathlib, shutil, subprocess, sys, tempfile
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOL = ROOT / "src" / "snip" / "sol"
PROB = ROOT / "src" / "problems"
PREFIX = "C:\\KONG_2027Prg\\RBTSW_Results\\"

def run(sol):
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for f in PROB.iterdir():
            if not f.name.endswith("_expected.txt"):
                shutil.copy(f, td / f.name)
        code = sol.read_text(encoding="utf-8").replace(PREFIX, str(td) + "/")
        (td / "_run.py").write_text(code, encoding="utf-8")
        r = subprocess.run([sys.executable, "_run.py"], cwd=td, capture_output=True,
                           text=True, encoding="utf-8")
        if r.returncode != 0:
            raise SystemExit(f"[실패] {sol.name}\n{r.stderr}")
        parts = []
        outs = sorted(p for p in td.iterdir() if p.name.startswith(sol.stem + "_output"))
        for o in outs:
            if o.suffix.lower() in (".xlsx", ".png", ".pdf"):
                parts.append(f"[{o.name} 생성됨]")
                continue
            raw = o.read_bytes()
            bom = raw.startswith(b"\xef\xbb\xbf")
            txt = raw.decode("utf-8-sig")
            parts.append(f"[{o.name}{' (utf-8-sig)' if bom else ''}]\n{txt.rstrip()}")
        if r.stdout.strip():
            parts.append(("[화면 출력]\n" if outs else "") + r.stdout.rstrip())
        (PROB / f"{sol.stem}_expected.txt").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        print(f"[완료] {sol.stem}")

only = sys.argv[1:]
for s in sorted(SOL.glob("q*.py")):
    if not only or s.stem in only:
        run(s)
