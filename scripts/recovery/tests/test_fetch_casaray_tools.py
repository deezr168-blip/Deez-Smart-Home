"""Tests for scripts/recovery/fetch_casaray_tools.sh.

    python3 -I scripts/recovery/tests/test_fetch_casaray_tools.py

Each scenario builds a throwaway git "remote" (file:// URL) whose branch
recovery/phase0-diagnostics holds the two recovery scripts, runs the fetch
script with BusyBox sh under strace, and asserts the exit code, what was
written to the output folder, that the temporary repository is gone, that no
write happened outside the output folder, and that no credential source was
consulted: a planted token variable, a global git config naming a credential
helper, a credentials file and an askpass hook must all go unused.

Needs git and strace; BusyBox (env BUSYBOX or 'busybox' on PATH) is used as the
shell when present, else /bin/sh. Prints SKIP and exits 0 without git/strace.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(REPO, "scripts/recovery/fetch_casaray_tools.sh")
FILES = ("casaray_evidence.sh", "register_casaray.sh")
BRANCH = "recovery/phase0-diagnostics"
TOKEN = "CANARY_TOKEN_" + "f00dfeed"   # assembled so the validator's token scan never sees a literal
OPEN_RE = re.compile(r'open(?:at)?\((?:AT_FDCWD, )?"([^"]*)", ([A-Z_|0-9]+)')
EXEC_RE = re.compile(r'execve\("([^"]*)"')
CHANGE_RE = re.compile(r'\b(mkdir|mkdirat|unlink|unlinkat|rename|renameat2?|rmdir|creat|link|linkat|symlink|symlinkat)\((.*)\)\s+=')


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def git(*args, cwd=None):
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True)


def make_remote(base, mutate=None, drop=None):
    work = os.path.join(base, "work")
    os.makedirs(os.path.join(work, "scripts/recovery"))
    for f in FILES:
        if f == drop:
            continue
        shutil.copy2(os.path.join(REPO, "scripts/recovery", f), os.path.join(work, "scripts/recovery", f))
        if f == mutate:
            with open(os.path.join(work, "scripts/recovery", f), "a") as fh:
                fh.write("# tampered\n")
    git("init", "-q", "-b", BRANCH, cwd=work)
    git("add", ".", cwd=work)
    git("commit", "-q", "-m", "fixture", cwd=work)
    bare = os.path.join(base, "remote.git")
    git("clone", "-q", "--bare", work, bare)
    return "file://" + bare


def plant_credentials(home):
    """Every credential source a careless git call could pick up."""
    os.makedirs(home)
    marker = os.path.join(home, "ASKPASS_WAS_CALLED")
    askpass = os.path.join(home, "askpass.sh")
    with open(askpass, "w") as f:
        f.write(f"#!/bin/sh\ntouch {marker}\necho {TOKEN}\n")
    os.chmod(askpass, 0o755)
    with open(os.path.join(home, ".gitconfig"), "w") as f:
        f.write(f"[credential]\n\thelper = store --file={home}/.git-credentials\n[core]\n\taskPass = {askpass}\n")
    with open(os.path.join(home, ".git-credentials"), "w") as f:
        f.write("https://u" + ":" + TOKEN + "@" + "github.com\n")
    return askpass, marker


def run(base, url, busybox, strace):
    out = os.path.join(base, "out")
    os.makedirs(out, exist_ok=True)
    home = os.path.join(base, "home")
    askpass, marker = plant_credentials(home)
    bindir = os.path.join(base, "bin")
    os.makedirs(bindir)
    if busybox:
        for a in subprocess.run([busybox, "--list"], capture_output=True, text=True).stdout.split():
            os.symlink(busybox, os.path.join(bindir, a))
    else:
        for a in ("sh", "env", "sha256sum", "cut", "sed", "tail", "mktemp", "mv", "rm", "cat"):
            p = shutil.which(a)
            if p:
                os.symlink(p, os.path.join(bindir, a))
    gitbin = shutil.which("git")
    if os.path.lexists(os.path.join(bindir, "git")):
        os.unlink(os.path.join(bindir, "git"))
    os.symlink(gitbin, os.path.join(bindir, "git"))
    trace = os.path.join(base, "strace.log")
    cwd = os.path.join(base, "cwd")
    os.makedirs(cwd)
    env = {"PATH": bindir, "HOME": home, "DEEZ_GH_TOKEN": TOKEN, "GITHUB_TOKEN": TOKEN,
           "GIT_ASKPASS": askpass, "CASARAY_REPO_URL": url, "CASARAY_OUT": out}
    p = subprocess.run([strace, "-f", "-qq", "-v", "-s", "256", "-e",
                        "trace=open,openat,creat,mkdir,mkdirat,unlink,unlinkat,rename,renameat,renameat2,rmdir,"
                        "link,linkat,symlink,symlinkat,execve", "-o", trace,
                        os.path.join(bindir, "sh"), SCRIPT], capture_output=True, text=True, env=env, timeout=300,
                       cwd=cwd)
    with open(trace) as f:
        lines = f.read().splitlines()
    return p, out, home, marker, lines


def common_checks(p, out, home, marker, lines, base):
    fails = []
    text = p.stdout + p.stderr
    if TOKEN in text:
        fails.append("token canary reached the output")
    if os.path.exists(marker):
        fails.append("the planted askpass hook was called")
    left = [n for n in os.listdir(out) if n.startswith("casaray_fetch.")]
    if left:
        fails.append(f"temporary repository left behind: {left}")
    git_execs = 0
    for l in lines:
        m = EXEC_RE.search(l)
        if m and (m.group(1).endswith("/git") or "/git-" in m.group(1)):
            git_execs += 1
            if TOKEN in l:
                fails.append(f"git started with the token in its environment: {m.group(1)}")
        if l.rstrip().endswith("ENOENT (No such file or directory)"):
            continue
        m = OPEN_RE.search(l)
        if m:
            path, flags = m.groups()
            if path.startswith(home) and (".gitconfig" in path or ".git-credentials" in path):
                fails.append(f"credential source opened: {path}")
            if re.search(r"O_WRONLY|O_RDWR|O_CREAT|O_TRUNC|O_APPEND", flags) and path != "/dev/null" \
                    and not path.startswith(out + "/"):
                fails.append(f"write outside the output folder: {path} {flags}")
        m = CHANGE_RE.search(l)
        if m and l.rstrip().endswith("= 0"):
            call, args = m.group(1), re.findall(r'"([^"]*)"', m.group(2))
            # symlink(target, linkpath) / symlinkat(target, dirfd, linkpath): the target is only
            # the link's text; the path created is the last string. Every other call: all paths.
            paths = args[-1:] if call.startswith("symlink") else args
            for path in paths:
                if path.startswith("/") and not path.startswith(out + "/"):
                    fails.append(f"filesystem change outside the output folder: {l.strip()[:140]}")
    # Relative paths are resolved against the cwd, which must stay empty (see run()).
    if os.listdir(os.path.join(base, "cwd")):
        fails.append(f"files created in the working directory: {os.listdir(os.path.join(base, 'cwd'))}")
    planted = {".gitconfig", ".git-credentials", "askpass.sh"}
    if set(os.listdir(home)) != planted:
        fails.append(f"home folder changed: {sorted(set(os.listdir(home)) ^ planted)}")
    if not git_execs:
        fails.append("no git process seen: the token/environment assertion would be vacuous")
    return fails


def scenario(name, busybox, strace, mutate=None, drop=None, bad_url=False, stale=False):
    base = tempfile.mkdtemp(prefix="fetch_casaray_")
    try:
        url = make_remote(base, mutate=mutate, drop=drop)
        if bad_url:
            url = "file://" + os.path.join(base, "no-such-repo.git")
        if stale:
            os.makedirs(os.path.join(base, "out"))
            for f in FILES:
                with open(os.path.join(base, "out", f), "w") as fh:
                    fh.write("stale copy\n")
        p, out, home, marker, lines = run(base, url, busybox, strace)
        fails = common_checks(p, out, home, marker, lines, base)
        verified = mutate is None and drop is None and not bad_url
        if verified:
            if p.returncode != 0:
                fails.append(f"exit {p.returncode} != 0: {(p.stdout + p.stderr).strip()[-200:]!r}")
            for f in FILES:
                q = os.path.join(out, f)
                if not os.path.exists(q) or sha(q) != sha(os.path.join(REPO, "scripts/recovery", f)):
                    fails.append(f"{f} not written byte-exact")
            if sorted(os.listdir(out)) != sorted(FILES):
                fails.append(f"unexpected files in the output folder: {sorted(os.listdir(out))}")
        else:
            if p.returncode != 1:
                fails.append(f"exit {p.returncode} != 1")
            for f in FILES:
                q = os.path.join(out, f)
                if stale:
                    with open(q) as fh:
                        if fh.read() != "stale copy\n":
                            fails.append(f"{f}: a pre-existing copy was replaced although verification failed")
                elif os.path.exists(q):
                    fails.append(f"{f} written although verification failed")
            if "STOP" not in p.stdout:
                fails.append("no STOP line")
        print(f"[{'PASS' if not fails else 'FAIL'}] {name}: exit {p.returncode}, "
              f"last line {p.stdout.strip().splitlines()[-1][:90]!r}" if p.stdout.strip() else f"[FAIL] {name}: no output")
        for f in fails:
            print("        !!", f)
        return len(fails) if p.stdout.strip() else len(fails) + 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    if not shutil.which("git") or not shutil.which("strace"):
        print("SKIP: needs git and strace")
        return 0
    busybox = os.environ.get("BUSYBOX") or shutil.which("busybox")
    print(f"shell: {'BusyBox ' + busybox if busybox else '/bin/sh (no BusyBox found)'}")
    total = 0
    total += scenario("verified-both", busybox, strace=shutil.which("strace"))
    total += scenario("verified-replaces-stale-copies", busybox, shutil.which("strace"), stale=True)
    total += scenario("tampered-register-writes-nothing", busybox, shutil.which("strace"), mutate="register_casaray.sh")
    total += scenario("tampered-evidence-keeps-stale-copies", busybox, shutil.which("strace"),
                      mutate="casaray_evidence.sh", stale=True)
    total += scenario("missing-file-writes-nothing", busybox, shutil.which("strace"), drop="register_casaray.sh")
    total += scenario("fetch-fails-writes-nothing", busybox, shutil.which("strace"), bad_url=True)
    print(f"TOTAL FAILURES: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
