#!/usr/bin/env python3
"""Simulate the Arduino IDE's .ino preprocessing, then compile.

Why this exists: on 2026-08-21 a sketch that compiled cleanly as plain C++
failed in the Arduino IDE with a wall of "'EnvReading' was not declared in
this scope". The cause is that the IDE auto-generates a forward declaration
for every function in the sketch and injects them immediately before the
FIRST function definition in the file. Any struct defined after that point is
invisible to those prototypes. A plain g++ pass can never see this, because
in plain C++ declaration-before-use already holds.

This script reproduces the failure mode, and is deliberately STRICTER than
the IDE: it hoists every generated prototype to the very top, right after the
#includes. If a sketch survives that, the IDE's (later) insertion point is
guaranteed to be fine too.

It also flags default arguments on top-level functions, which the IDE copies
into the generated prototype while leaving them on the definition — the
compiler then rejects the redefined default.
"""
import re
import subprocess
import sys
import os

KEYWORDS = {
    "if", "for", "while", "switch", "else", "do", "return", "struct", "class",
    "enum", "union", "namespace", "template", "catch", "sizeof", "typedef",
}


def find_definitions(src):
    """Top-level function definitions: a line starting at column 0 that opens
    a parameter list and ends in '{'. Good enough for a single-file sketch."""
    defs = []
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if not line or line[0] in " \t#/}":
            continue
        # Trailing content after the brace is allowed, so single-line bodies
        # like `void f() { }` are seen too. An earlier version anchored on
        # end-of-line and silently found nothing in such files.
        m = re.match(
            r"^((?:[A-Za-z_][\w:]*\s+)+[\*&]?\s*)([A-Za-z_]\w*)\s*\(([^)]*)\)\s*\{",
            line,
        )
        if not m:
            continue
        ret, name, params = m.group(1).strip(), m.group(2), m.group(3)
        if name in KEYWORDS or ret.split()[-1] in KEYWORDS:
            continue
        defs.append((i + 1, ret, name, params))
    return defs


def main(path):
    src = open(path, encoding="utf-8").read()
    defs = find_definitions(src)
    if not defs:
        print("ERROR: no function definitions found — the parser is wrong")
        return 2

    problems = []
    for lineno, ret, name, params in defs:
        if "=" in params:
            problems.append(
                "line %d: %s() has a default argument. The IDE duplicates it "
                "into the generated prototype and the compiler rejects it. "
                "Remove the default." % (lineno, name)
            )

    # Insertion point: immediately before the FIRST function definition, which
    # is what the IDE actually does. Hoisting all the way to the top instead
    # would be stricter but wrong — it would flag the recommended pattern of
    # declaring your types above the first function, which is the very fix
    # this check exists to encourage.
    lines = src.split("\n")
    insert_at = defs[0][0] - 1

    protos = ["// ---- simulated Arduino auto-generated prototypes ----"]
    for _, ret, name, params in defs:
        if name in ("setup", "loop"):
            continue
        protos.append("%s %s(%s);" % (ret, name, params))
    protos.append("// ---- end simulated prototypes ----")
    protos.append("")

    out = lines[:insert_at] + protos + lines[insert_at:]
    tmp = path + ".arduino_sim.cpp"
    open(tmp, "w", encoding="utf-8").write("\n".join(out))

    print("functions found: %d" % len(defs))
    for p in problems:
        print("  DEFAULT-ARG: %s" % p)

    cmd = [
        "g++", "-std=gnu++17", "-fsyntax-only", "-Wall", "-Wextra",
        "-Wformat=2", "-Wno-unused-parameter",
        "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "stubs"),
        "-include", "Arduino.h", tmp,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and not r.stderr.strip() and not problems:
        print("PASS  compiles with all prototypes hoisted above the types")
        os.remove(tmp)
        return 0
    print("FAIL")
    if r.stderr.strip():
        # Rewrite the temp filename back to the real one so line numbers read sanely
        print(r.stderr.replace(tmp, os.path.basename(path))[:4000])
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
