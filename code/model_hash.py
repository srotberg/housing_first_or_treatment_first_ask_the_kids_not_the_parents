#!/usr/bin/env python3
"""The model's SEMANTIC identity: the source with comments and blank lines gone.

WHY THIS EXISTS. The archive is grouped by an md5 of the whole Fortran file, so
a point measured before a comment was added scores against a different "model"
than one measured after. On 1 September a commit that changed ZERO non-comment
lines invalidated forty points, and the loss went from 162.8 per cent to "no
scoreable point in the current economy" because documentation had been written.

Eleven of that day's twelve source changes really were semantic, so this is not
the main reason the search kept restarting -- the main reason was changing the
model twelve times. But a free reset is still a reset, and the fix is cheap.

HOW OLD POINTS ARE RECOVERED. They carry only the full-file MODEL stamp, so the
map from full hash to semantic hash is rebuilt by walking git history for the
Fortran file. That is exact rather than heuristic: every revision that has ever
been committed can be hashed both ways. The map is cached in .model_hash_map and
refreshed when the current source is not in it.
"""
import hashlib, json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
REL = 'code/housing_first_or_treatment_first_SR_v1.f90'
CACHE = os.path.join(HERE, '.model_hash_map')


def semantic(text):
    """md5 of the source with trailing comments and blank lines removed."""
    body = '\n'.join(l.split('!')[0].rstrip() for l in text.splitlines()
                     if l.split('!')[0].strip())
    return hashlib.md5(body.encode()).hexdigest()[:10]


def full(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]


def _git_revs():
    r = subprocess.run(['git', 'log', '--format=%H', '--', REL],
                       cwd=os.path.dirname(HERE), capture_output=True, text=True)
    return r.stdout.split()


def build_map(force=False):
    """{full_hash: semantic_hash} over every committed revision, cached."""
    m = {}
    if os.path.exists(CACHE) and not force:
        try:
            m = json.load(open(CACHE))
        except Exception:
            m = {}
    cur = open(SRC, encoding='utf-8', errors='surrogateescape').read()
    m[full(cur)] = semantic(cur)
    if force or len(m) < 2:
        for sha in _git_revs():
            t = subprocess.run(['git', 'show', f'{sha}:{REL}'],
                               cwd=os.path.dirname(HERE),
                               capture_output=True, text=True).stdout
            if t:
                m[full(t)] = semantic(t)
        try:
            json.dump(m, open(CACHE, 'w'), indent=0)
        except OSError:
            pass
    return m


def current():
    return semantic(open(SRC, encoding='utf-8', errors='surrogateescape').read())


def resolve(stamp, cache=None):
    """Semantic hash for a MODEL stamp read off a point file.

    Unknown stamps come back unchanged, so a point from a revision that was
    never committed still groups with itself and never with anything else.
    """
    m = cache if cache is not None else build_map()
    if stamp not in m:
        m = build_map(force=True)
        if cache is not None:
            cache.update(m)
    return m.get(stamp, stamp)


if __name__ == '__main__':
    m = build_map(force=True)
    print(f'current semantic hash {current()}')
    print(f'{len(m)} revisions mapped, cached in {os.path.basename(CACHE)}')
