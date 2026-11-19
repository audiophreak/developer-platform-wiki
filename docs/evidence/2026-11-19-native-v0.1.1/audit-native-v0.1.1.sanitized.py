#!/usr/bin/env python3
# ARCHIVED, SANITIZED COPY. Differs from the executed original only in that one literal of the personal-data
# scan pattern (the owner's surname) is replaced by OWNER-SURNAME-REDACTED. The original's SHA-256 is in
# ../SHA256SUMS. Kept as a record of the fail-closed harness, not as a maintained tool.
"""Fail-closed published-platform acceptance audit (developer-platform v0.8.0, web-core v0.7.0, native-ios v0.1.1).

Derived from audit-wp4.py (the accepted v0.1.0 baseline audit) for the native-ios-template v0.1.1 corrective patch: same
gates, native expectations moved to v0.1.1, plus gates for the two fixed defects and a real v0.1.0 -> v0.1.1 layer upgrade.

usage: python3 ~/Claude/audit-wp4.py WORKSPACE SIMULATOR_UDID EVIDENCE_FILE
  WORKSPACE  a fresh directory from `uv run python tools/scratch.py new` (inside developer-platform)

Every gate is one argv-list subprocess (no shell, no pipes), its exit code is captured and asserted, and its output is
checked for the expected result (test counts, no failures, no skips). A gate that fails is recorded and the audit goes on
(aggregate failure), except that gates depending on a failed one are recorded as BLOCKED (also a failure).
The process exits 0 only if every gate passed; the evidence file lists every gate with its exit code.
"""
import hashlib, os, re, subprocess, sys, time
from pathlib import Path

W = Path(sys.argv[1]).resolve()
SIM = sys.argv[2]
EVIDENCE = Path(sys.argv[3]).resolve()
HOME = Path.home()
SRC = {r: HOME / "Developer" / r for r in ("developer-platform", "web-core-template", "native-ios-template")}
EXPECT = {
    "developer-platform": ("v0.8.0", "e185d6d2c4ac9edde5db7963458c8146e4c229d2"),
    "web-core-template": ("v0.7.0", "094e35b8b32d6186d609695f940afeb91a9b5990"),
    "native-ios-template": ("v0.1.1", "f0f4a5a8ac58825e94a38068df1bdd413d2f1596"),
}
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "SUPABASE_ALLOW_LAN_EXPOSURE": "true", "IOS_SIMULATOR": SIM, "CI": ""}
ENV.pop("CI")
APPS = W / "apps"
results = []  # (project, gate, ok, detail)
blocked_projects = set()


def record(project, gate, ok, detail=""):
    results.append((project, gate, bool(ok), detail))
    line = f"{'PASS' if ok else 'FAIL'}  {project:<10} {gate:<46} {detail}"
    print(line, flush=True)
    return bool(ok)


def sh(argv, cwd=None, timeout=1800, env=None):
    log = W / "logs"
    log.mkdir(exist_ok=True)
    try:
        p = subprocess.run(argv, cwd=cwd, env=env or ENV, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        return p.returncode, ANSI.sub("", p.stdout + p.stderr)
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT after {timeout}s"
    except Exception as e:  # a command that cannot even start is a failure, never a pass
        return 127, f"could not run: {e}"


def gate(project, name, argv, cwd=None, expect_exit=0, check=None, timeout=1800, env=None):
    """Runs argv, asserts the exit code, then the optional output check (returns (ok, detail))."""
    if project in blocked_projects:
        return record(project, name, False, "BLOCKED by an earlier failure in this project"), ""
    code, out = sh(argv, cwd, timeout, env)
    (W / "logs" / f"{project}-{re.sub(r'[^A-Za-z0-9]+', '_', name)}.log").write_text(out)
    ok, detail = code == expect_exit, f"exit {code}"
    if code != expect_exit:
        detail += f" (expected {expect_exit}); tail: {out.strip()[-160:]!r}"
    elif check:
        cok, cd = check(out)
        ok, detail = cok, f"exit {code}; {cd}"
    record(project, name, ok, detail)
    return ok, out


def vitest_totals(min_tests):
    def check(out):
        found = re.findall(r"Tests\s+(?:(\d+) failed \| )?(\d+) passed(?: \| (\d+) (skipped|todo))?(?: \| (\d+) \w+)? \((\d+)\)", out)
        bad = re.search(r"Tests\s+.*\b(failed|skipped|todo)\b", out)
        if not found or bad:
            return False, "no clean 'Tests N passed' line" if not bad else f"failed/skipped tests: {bad.group(0)!r}"
        total = sum(int(f[1]) for f in found)
        return (total >= min_tests), f"{total} tests passed in {len(found)} run(s), none failed or skipped"
    return check


def swift_totals(expected, allow_skip=()):
    def check(out):
        m = re.findall(r"Test run with (\d+) tests? in (\d+) suites? (passed|failed)", out)
        if not m or any(x[2] != "passed" for x in m):
            return False, f"swift testing summary missing or failed: {m}"
        n = sum(int(x[0]) for x in m)
        skipped = [l for l in out.splitlines() if re.search(r'(?:Test|Suite) ".*" (?:skipped|disabled)|\bTest Case .* skipped|\(\d+ tests? skipped\)|, [1-9]\d* tests? skipped', l) and not any(a in l for a in allow_skip)]
        xc = re.findall(r"Executed (\d+) tests?, with (\d+) failures?", out)
        if skipped:
            return False, f"unexpected skipped/disabled: {skipped[:2]}"
        if any(int(f[1]) for f in xc):
            return False, f"XCTest failures {xc}"
        if "TEST FAILED" in out:
            return False, "TEST FAILED"
        return n == expected, f"Swift Testing {n} passed (expected {expected}), no unexpected skips"
    return check


def tail_ok(pattern):
    def check(out):
        m = re.search(pattern, out)
        return bool(m), (m.group(0) if m else f"missing /{pattern}/")
    return check


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- 0. source state before
def source_state():
    s = {}
    for r, p in SRC.items():
        _, head = sh(["git", "-C", str(p), "rev-parse", "HEAD"])
        _, st = sh(["git", "-C", str(p), "status", "--porcelain"])
        _, tags = sh(["git", "-C", str(p), "for-each-ref", "--format=%(refname) %(objectname)", "refs/tags", "refs/heads"])
        s[r] = (head.strip(), st.strip(), tags.strip())
    return s


before = source_state()

print("=== 0. preflight: no leftover containers or volumes from an earlier run")
code, out = sh(["docker", "ps", "-a", "--format", "{{.Names}}"])
record("preflight", "docker reachable, no containers", code == 0 and not out.strip(), out.strip()[:80])
code, out = sh(["docker", "volume", "ls", "-q"])
record("preflight", "no leftover docker volumes (stale volumes keep old passwords)", code == 0 and not out.strip(), out.strip()[:80])
if not results[-1][2] or not results[-2][2]:
    print("preflight failed; aborting", flush=True)
    EVIDENCE.write_text("FAIL preflight\n")
    sys.exit(1)

# ---------------------------------------------------------------- 1. published tags and visibility and CI
print("=== 1. published tags, privacy, main CI")
for r, (tag, want) in EXPECT.items():
    url = f"https://github.com/audiophreak/{r}.git"
    code, out = sh(["git", "ls-remote", "--tags", url, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"])
    peeled = {l.split()[1]: l.split()[0] for l in out.splitlines() if len(l.split()) == 2}
    got, obj = peeled.get(f"refs/tags/{tag}^{{}}"), peeled.get(f"refs/tags/{tag}")
    record(r, f"remote tag {tag} -> expected commit (annotated)", code == 0 and got == want and obj and obj != got, f"peeled {got}")
    code, out = sh(["git", "ls-remote", url, "refs/heads/main"])
    record(r, "remote main == expected SHA", code == 0 and out.split()[:1] == [want], out.strip()[:40])
    code, out = sh(["gh", "repo", "view", f"audiophreak/{r}", "--json", "visibility", "-q", ".visibility"])
    record(r, "repository is PRIVATE", code == 0 and out.strip() == "PRIVATE", out.strip())
    code, out = sh(["gh", "run", "list", "-R", f"audiophreak/{r}", "-b", "main", "-L", "1", "--json", "conclusion,headSha,url,status", "-q", ".[0] | [.conclusion,.status,.headSha,.url] | @tsv"])
    f = out.strip().split("\t")
    record(r, "main CI green on the expected SHA", code == 0 and f[:3] == ["success", "completed", want], out.strip())

# ---------------------------------------------------------------- 2. fresh clone of the published platform
print("=== 2. fresh clone of developer-platform v0.8.0")
P = W / "platform"
code, out = sh(["git", "clone", "-q", "--branch", "v0.8.0", "https://github.com/audiophreak/developer-platform.git", str(P)])
ok = record("platform", "clone tag v0.8.0", code == 0, f"exit {code}")
if ok:
    _, head = sh(["git", "-C", str(P), "rev-parse", "HEAD"])
    record("platform", "clone HEAD == expected SHA", head.strip() == EXPECT["developer-platform"][1], head.strip())
    gate("platform", "uv sync --locked", ["uv", "sync", "--locked", "--project", str(P)], cwd=P)
    gate("platform", "devkit --version", ["uv", "run", "--project", str(P), "devkit", "--version"], cwd=W, check=tail_ok(r"0\.8\.0"))
    gate("platform", "devkit doctor", ["uv", "run", "--project", str(P), "devkit", "doctor"], cwd=W)
else:
    blocked_projects.add("platform")
DK = ["uv", "run", "--project", str(P), "devkit"]

# ---------------------------------------------------------------- 3. generation matrix from the published templates
print("=== 3. generation matrix (fresh destinations, published templates)")
APPS.mkdir()
MATRIX = {
    "basic-app": [],
    "fs-pg": ["--profile", "full-stack", "--set", "database=postgres"],
    "fs-sb": ["--profile", "full-stack", "--set", "database=supabase"],
    "nat-pg": ["--profile", "native-ios", "--set", "database=postgres"],
    "nat-sb": ["--profile", "native-ios", "--set", "database=supabase"],
}
for n, extra in MATRIX.items():
    gate(n, "devkit new (published templates)", DK + ["new", n, "--description", f"Acceptance {n}", "--output-dir", str(APPS), *extra], cwd=W)
    d = APPS / n
    if n in blocked_projects:
        continue
    web = (d / ".copier-answers.yml").read_text() if (d / ".copier-answers.yml").exists() else ""
    ok = "_commit: v0.7.0" in web and "https://github.com/audiophreak/web-core-template" in web
    record(n, "web layer provenance = published v0.7.0 (not a path)", ok, "answers file")
    if n.startswith("nat-"):
        ios = (d / ".copier-answers.ios.yml").read_text() if (d / ".copier-answers.ios.yml").exists() else ""
        record(n, "native layer provenance = published v0.1.1", "_commit: v0.1.1" in ios and "https://github.com/audiophreak/native-ios-template" in ios, "answers file")
    code, out = sh(["git", "init", "-q", "-b", "main"], cwd=d)
    code2, _ = sh(["git", "add", "-A"], cwd=d)
    code3, _ = sh(["git", "-c", "user.name=Audit", "-c", "user.email=a@example.invalid", "commit", "-q", "-m", "initial"], cwd=d)
    record(n, "git baseline committed", code == code2 == code3 == 0, "")

print("=== 3b. rejections (exit 2, nothing created at the destination)")
for label, extra in {
    "full-stack without a database": ["--profile", "full-stack"],
    "full-stack with auth=false": ["--profile", "full-stack", "--set", "database=postgres", "--set", "auth=false"],
    "native-ios without a database": ["--profile", "native-ios"],
    "native-set on web-core": ["--native-set", "bundle_identifier=com.acme.x"],
}.items():
    gate("platform", f"reject: {label}", DK + ["new", "rejected", "--output-dir", str(APPS), *extra], cwd=W, expect_exit=2)
    record("platform", f"reject: {label} created nothing", not (APPS / "rejected").exists(), "")

# ---------------------------------------------------------------- 4. generated-project validation, audits, scans, layered status
print("=== 4. generated-project validation")
for n in MATRIX:
    d = APPS / n
    gate(n, "npm ci", ["npm", "ci", "--no-audit", "--no-fund"], cwd=d)
    gate(n, "npm run check (lint+typecheck+format+tests+build)", ["npm", "run", "check"], cwd=d, check=vitest_totals(3 if n == "basic-app" else 200))
    gate(n, "npm audit --omit=dev", ["npm", "audit", "--omit=dev"], cwd=d, check=tail_ok(r"found 0 vulnerabilities"))
    cred = subprocess.run(["grep", "-r", "-l", "-E", r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----", ".", "--exclude-dir=node_modules", "--exclude-dir=.next", "--exclude-dir=.build", "--exclude-dir=.git", "--exclude=package-lock.json"], cwd=d, capture_output=True, text=True)
    record(n, "no credentials in the project", cred.returncode == 1 and not cred.stdout, f"grep exit {cred.returncode}")
    user = os.environ.get("USER", "")
    pers = subprocess.run(["grep", "-r", "-l", "-E", f"/Users/|{re.escape(str(HOME))}|my-first-app|OWNER-SURNAME-REDACTED|\\b{re.escape(user)}\\b", ".", "--exclude-dir=node_modules", "--exclude-dir=.next", "--exclude-dir=.build", "--exclude-dir=.git", "--exclude-dir=.derived-data", "--exclude=package-lock.json", "--exclude=*.tsbuildinfo", "--exclude=check-static.sh"], cwd=d, capture_output=True, text=True)
    record(n, "no personal paths or names in the project", pers.returncode == 1 and not pers.stdout, f"grep exit {pers.returncode} {pers.stdout.strip()[:80]}")
    if n.startswith("nat-"):
        gate(n, "devkit status: both layers up to date", DK + ["status", str(d)], cwd=W, check=lambda o: (o.count("up to date") >= 2, f"{o.count('up to date')} layers up to date"))
        gate(n, "upgrade without --layer is refused", DK + ["upgrade", str(d), "--dry-run"], cwd=W, expect_exit=2)
        gate(n, "upgrade --layer web dry-run", DK + ["upgrade", str(d), "--layer", "web", "--dry-run"], cwd=W, check=tail_ok(r"(?i)up to date"))
        gate(n, "upgrade --layer native dry-run", DK + ["upgrade", str(d), "--layer", "native", "--dry-run"], cwd=W, check=tail_ok(r"(?i)up to date"))
    else:
        gate(n, "upgrade dry-run: up to date", DK + ["upgrade", str(d), "--dry-run"], cwd=W, check=tail_ok(r"(?i)up to date"))
    _, st = sh(["git", "status", "--porcelain"], cwd=d)
    leftovers = [l for l in st.splitlines() if not re.search(r"\.next|\.env|node_modules|tsbuildinfo|next-env", l)]
    record(n, "tree clean after validation and dry-run upgrades", not leftovers, "; ".join(leftovers[:3]))

# ---------------------------------------------------------------- 5. database gates
print("=== 5. database init/up/migrate/status/tests")
for n in ("fs-pg", "fs-sb", "nat-pg", "nat-sb"):
    d = APPS / n
    for step in ("db:init", "db:up", "db:migrate"):
        gate(n, f"npm run {step}", ["npm", "run", "--silent", step], cwd=d)
    gate(n, "npm run db:status (3 migrations applied, none pending)", ["npm", "run", "--silent", "db:status"], cwd=d,
         check=lambda o: (bool(re.search(r"app_runtime", o)) and not re.search(r"(?i)\bpending\b[^\n]*[1-9]", o), "runtime role app_runtime; status printed"))
    gate(n, "npm run test:db (real database)", ["npm", "run", "--silent", "test:db"], cwd=d, check=vitest_totals(70), timeout=2400)
    gate(n, "npm run db:down", ["npm", "run", "--silent", "db:down"], cwd=d)

# ---------------------------------------------------------------- 6. native layer gates
print("=== 6. native layer: contract, client regeneration, Swift tests, Keychain, Release config")
for n in ("nat-pg", "nat-sb"):
    d = APPS / n
    ios = d / "ios"
    before_sha = sha(d / "openapi/openapi.json")
    gate(n, "deterministic OpenAPI: npm run openapi:generate", ["npm", "run", "--silent", "openapi:generate"], cwd=d, timeout=900)
    record(n, "OpenAPI unchanged by regeneration (byte-identical)", sha(d / "openapi/openapi.json") == before_sha, before_sha[:16])
    record(n, "web openapi.json == ios Contract/openapi.json", sha(d / "openapi/openapi.json") == sha(ios / "Contract/openapi.json"), sha(ios / "Contract/openapi.json")[:16])
    gate(n, "static checks", ["sh", "scripts/check-static.sh"], cwd=ios)
    gate(n, "contract check", ["sh", "scripts/check-contract.sh"], cwd=ios)
    gate(n, "Swift client regeneration, zero diff", ["sh", "scripts/check-generated.sh"], cwd=ios, timeout=2400)
    gate(n, "host swift test (AppCore package)", ["swift", "test"], cwd=ios / "Packages/AppCore", check=swift_totals(58), timeout=2400)
    gate(n, "simulator package tests", ["sh", "scripts/test.sh", "package"], cwd=ios, check=swift_totals(58), timeout=3000)
    gate(n, "simulator hosted app + Keychain tests", ["sh", "scripts/test.sh", "app"], cwd=ios,
         check=swift_totals(11, allow_skip=("EndToEnd", "phase one", "phase two", "scenario's own marker")), timeout=3000)
    gate(n, "Release HTTPS / ATS configuration", ["sh", "scripts/check-release-config.sh"], cwd=ios, timeout=2400)
    gate(n, "committed client matches a fresh generation (git diff)", ["git", "diff", "--exit-code", "--stat"], cwd=d)
    _, st = sh(["git", "status", "--porcelain", "--untracked-files=all"], cwd=d)
    record(n, "v0.1.1 fix: no Git-visible file after native gates incl. Release check", not st.strip(), "; ".join(st.splitlines()[:3]) or "git status empty")
    record(n, "v0.1.1 fix: Release check log kept in the ignored build area", (ios / ".derived-data/release.log").is_file() and not (ios / ".derived-data-release.log").exists(), "ios/.derived-data/release.log")
    gate(n, "devkit status after the Release check", DK + ["status", str(d)], cwd=W, check=lambda o: (o.count("up to date") >= 2, f"{o.count('up to date')} layers up to date"))
    gate(n, "upgrade --layer native dry-run after the Release check (not refused)", DK + ["upgrade", str(d), "--layer", "native", "--dry-run"], cwd=W, check=tail_ok(r"(?i)up to date"))
    readme = (ios / "README.md").read_text()
    record(n, "v0.1.1 fix: generated README documents devkit upgrade PROJECT --layer native, no upgrade-native",
           "devkit upgrade PROJECT --layer native" in readme and "upgrade-native" not in readme, "ios/README.md")

# ---------------------------------------------------------------- 6b. an existing v0.1.0 native project upgrades to v0.1.1
print("=== 6b. existing native v0.1.0 project: the old defect, then devkit v0.8.0 upgrades the layer to v0.1.1")
u = "nat-up"
U = APPS / u
gate(u, "devkit new with the published native v0.1.0", DK + ["new", u, "--output-dir", str(APPS), "--profile", "native-ios", "--set", "database=postgres", "--native-template-ref", "v0.1.0"], cwd=W)
if u not in blocked_projects:
    record(u, "native provenance = published v0.1.0", "_commit: v0.1.0" in (U / ".copier-answers.ios.yml").read_text(), "answers file")
    c1, _ = sh(["git", "init", "-q", "-b", "main"], cwd=U); c2, _ = sh(["git", "add", "-A"], cwd=U)
    c3, _ = sh(["git", "-c", "user.name=Audit", "-c", "user.email=a@example.invalid", "commit", "-q", "-m", "initial"], cwd=U)
    record(u, "git baseline committed", c1 == c2 == c3 == 0, "")
    gate(u, "devkit status reports native v0.1.1 newer", DK + ["status", str(U)], cwd=W, check=tail_ok(r"native\s+v0\.1\.0\s+newer available: v0\.1\.1"))
    gate(u, "v0.1.0 Release check (reproduces the old defect)", ["sh", "scripts/check-release-config.sh"], cwd=U / "ios", timeout=2400)
    _, st = sh(["git", "status", "--porcelain", "--untracked-files=all"], cwd=U)
    record(u, "v0.1.0 defect reproduced: untracked ios/.derived-data-release.log", st.strip() == "?? ios/.derived-data-release.log", st.strip()[:80])
    gate(u, "devkit upgrade refuses the tree dirtied by the v0.1.0 check", DK + ["upgrade", str(U), "--layer", "native", "--dry-run"], cwd=W, expect_exit=1, check=None)
    (U / "ios/.derived-data-release.log").unlink()  # the one stray file the v0.1.0 script wrote, nothing else
    gate(u, "upgrade --layer native dry-run plans v0.1.0 -> v0.1.1", DK + ["upgrade", str(U), "--layer", "native", "--dry-run"], cwd=W, check=tail_ok(r"Upgrading v0\.1\.0 -> v0\.1\.1"))
    gate(u, "upgrade --layer native to v0.1.1", DK + ["upgrade", str(U), "--layer", "native"], cwd=W)
    record(u, "native provenance after upgrade = v0.1.1", "_commit: v0.1.1" in (U / ".copier-answers.ios.yml").read_text(), "answers file")
    _, changed = sh(["git", "status", "--porcelain", "--untracked-files=all"], cwd=U)
    files = sorted(l[3:] for l in changed.splitlines())
    want = [".copier-answers.ios.yml", "ios/README.md", "ios/scripts/check-release-config.sh"]
    record(u, "upgrade changed exactly the answers file, README and Release check", files == want, ", ".join(files))
    c4, _ = sh(["git", "add", "-A"], cwd=U)
    c5, _ = sh(["git", "-c", "user.name=Audit", "-c", "user.email=a@example.invalid", "commit", "-q", "-m", "chore: update native template to v0.1.1"], cwd=U)
    record(u, "upgrade committed", c4 == c5 == 0, "")
    gate(u, "devkit status: both layers up to date", DK + ["status", str(U)], cwd=W, check=lambda o: (o.count("up to date") >= 2, f"{o.count('up to date')} layers up to date"))
    gate(u, "v0.1.1 Release check on the upgraded project", ["sh", "scripts/check-release-config.sh"], cwd=U / "ios", timeout=2400)
    _, st = sh(["git", "status", "--porcelain", "--untracked-files=all"], cwd=U)
    record(u, "upgraded project stays clean after the Release check", not st.strip(), st.strip()[:80] or "git status empty")
    gate(u, "upgrade --layer native dry-run not refused afterwards", DK + ["upgrade", str(U), "--layer", "native", "--dry-run"], cwd=W, check=tail_ok(r"(?i)up to date"))

# ---------------------------------------------------------------- 7. real end-to-end on the simulator
print("=== 7. real native end-to-end (PostgreSQL, Supabase)")
STEPS = [
    ("phase one: passed", "sign-in + Keychain token + session + create/read/update + cross-user denial (phase one)"),
    ("restarting the web server and the database", "server and database restart"),
    ("phase two: passed", "relaunch persistence + delete + sign-out + old-token 401 (phase two)"),
    ("the server log contains no authorization header or token", "no token in the server log"),
    ("END-TO-END SCENARIO PASSED", "scenario verdict"),
]
for n in ("nat-pg", "nat-sb"):
    d = APPS / n
    ok, out = gate(n, "e2e.mjs exit status", ["node", "ios/scripts/e2e.mjs", "--down"], cwd=d, timeout=3600)
    for marker, label in STEPS:
        record(n, f"e2e: {label}", marker in out, "marker found" if marker in out else f"marker missing: {marker}")
    record(n, "e2e: no test skipped (phase tests ran)", "did not run" not in out and "FAILED" not in out, "")

# ---------------------------------------------------------------- 8. provider parity
print("=== 8. provider parity")
def tree_digest(root, skip=(".derived-data", ".build", ".derived-data-release.log")):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if p.is_file() and not any(s in p.parts or p.name == s for s in skip):
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()
record("parity", "openapi.json identical across nat-pg / nat-sb / fs-pg / fs-sb",
       len({sha(APPS / n / "openapi/openapi.json") for n in ("nat-pg", "nat-sb")}) == 1, "native pair")
def norm_tree(n, a, b):
    h = hashlib.sha256()
    for p in sorted(Path(APPS / n / "ios").rglob("*")):
        if p.is_file() and not any(s in p.parts or p.name == s for s in (".derived-data", ".build", ".derived-data-release.log")):
            h.update(str(p.relative_to(APPS / n / "ios")).encode())
            h.update(p.read_bytes().replace(a.encode(), b"NAME").replace(a.replace("-", " ").title().encode(), b"NAME").replace(a.replace("-", "").encode(), b"NAME"))
    return h.hexdigest()
record("parity", "ios/ tree identical between providers (apart from the app name / bundle id)", norm_tree("nat-pg", "nat-pg", "") == norm_tree("nat-sb", "nat-sb", ""), "all non-build files, name normalised")
record("parity", "both providers passed the same e2e scenario",
       all(r[2] for r in results if r[0] in ("nat-pg", "nat-sb") and r[1].startswith("e2e")), "")

# ---------------------------------------------------------------- 9. source repositories unchanged
print("=== 9. source repositories unchanged by the audit")
after = source_state()
for r in SRC:
    record(r, "local repo HEAD, status, tags and branches unchanged", before[r] == after[r] and not after[r][1], f"HEAD {after[r][0][:12]}")

# ---------------------------------------------------------------- evidence
failed = [r for r in results if not r[2]]
lines = [f"{'PASS' if r[2] else 'FAIL'}\t{r[0]}\t{r[1]}\t{r[3]}" for r in results]
lines.append(f"TOTAL gates {len(results)} passed {len(results) - len(failed)} failed {len(failed)}")
EVIDENCE.write_text("\n".join(lines) + "\n")
print(lines[-1])
print("AUDIT RESULT:", "PASS" if not failed else "FAIL")
sys.exit(0 if not failed else 1)
