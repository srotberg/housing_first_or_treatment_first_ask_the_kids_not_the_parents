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
import hashlib, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
REL = 'code/housing_first_or_treatment_first_SR_v1.f90'
CACHE = os.path.join(HERE, '.model_hash_map')


# A TARGET IS NOT A MODEL. Changing the number a moment is SCORED against does
# not change a single household's problem, a single price, or a single
# allocation -- but it is a line of the Fortran, so it used to move the hash and
# empty the archive.
#
# It cost fifteen solves on 2 September. Four source changes landed between 12:53
# and 13:59; two of them were target edits the author asked for (the wealth-to-GDP
# ratio to 2.5 and back to 3.0, ninety minutes apart). The three points measured
# between 13:18 and 13:59 differ from the source that followed them by EXACTLY ONE
# non-comment line -- `wealth_to_output_data=2.5d0` against `=3.0d0` -- and were
# discarded for it.
#
# THE BAR FOR ADDING A NAME HERE IS EVIDENCE, NOT THE SUFFIX. Thirty-six constants
# end in `_data` and most of them are NOT safe: personal_exemption_data and
# standard_deduction_data build the tax function at 27870, avg_labor_supply_data
# is inside a labour supply expression at 29351, fraction_of_average_house_price_
# data is in the household problem at 19279. A name goes in this list only after
# every one of its non-comment uses has been read and found to be a write
# statement or a gap in the outer calibration stepper -- never an equilibrium
# object. Both entries below were checked that way, line by line.
#
# It is also only sound because a POINT PINS EVERY PARAMETER. run_one_point hands
# over all 43 and the point file records "HANDOVER OK: 43 of 43", so the stepper
# these targets drive has nothing left to move and the solved allocation cannot
# depend on them. If a point is ever run with a live adjuster, this stops being
# true for that point.
TARGET_CONSTANTS = (
    'wealth_to_output_data',      # decl, 6 writes, and the discount_factor gap
    'unemployment_rate_data',     # decl, 1 write, and the separation_rate gap
)

# Bumped whenever semantic() changes. The cache maps file bytes to a semantic
# hash, so a new rule makes every stored value wrong rather than merely stale --
# the map is rebuilt from git rather than trusted when this moves.
HASH_VERSION = 2

_TARGET_RE = re.compile(
    r'^(\s*.*::\s*(?:%s)\s*=)\s*\S+\s*$' % '|'.join(TARGET_CONSTANTS))


def semantic(text):
    """md5 of the source with comments, blank lines and TARGET VALUES removed.

    The target's declaration is kept and only its value is blanked, so renaming
    or deleting a target still moves the hash -- it is the number that is
    ignored, not the line.
    """
    out = []
    for l in text.splitlines():
        l = l.split('!')[0].rstrip()
        if not l.strip():
            continue
        m = _TARGET_RE.match(l)
        if m:
            l = m.group(1) + ' <target>'
        out.append(l)
    return hashlib.md5('\n'.join(out).encode()).hexdigest()[:10]


def full(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]


def _git_revs():
    r = subprocess.run(['git', 'log', '--format=%H', '--', REL],
                       cwd=os.path.dirname(HERE), capture_output=True, text=True)
    return r.stdout.split()


def build_map(force=False):
    """{full_hash: semantic_hash} over every committed revision, cached.

    THE CACHE IS ONLY EVER ADDED TO. `force` means "walk git again", not
    "throw away what we already know", and the difference is not cosmetic: it
    used to start from an empty dict on force, walk whatever revisions the
    checkout happened to have, and write THAT over the cache. In a full clone
    the two are the same. In a SHALLOW clone -- which is what every worker
    session gets -- git log sees seven revisions, so one gaps.py run rewrote
    the tracked 329-entry map down to seven and a worker then pushed the
    truncated file. Every point whose stamp lived in the discarded entries
    stops resolving, which reads downstream as "no scoreable point in the
    current economy": the archive looks empty when it is merely unmappable.

    Merging is always safe. A mapping is from the md5 of a file's bytes to the
    semantic hash of those same bytes, so an entry can never become wrong, and
    two sources that disagree about one key cannot exist.
    """
    m = {}
    if os.path.exists(CACHE):
        try:
            m = json.load(open(CACHE))
        except Exception:
            m = {}
    # A NEW HASH RULE MAKES EVERY STORED VALUE WRONG, not merely stale, so the
    # merge-only discipline above does not apply across a version bump: an old
    # entry would keep resolving a stamp to a hash the current semantic() would
    # never produce. Drop the map and rebuild it from git instead.
    if m.pop('__hash_version__', 1) != HASH_VERSION:
        m = {}
        force = True
    m['__hash_version__'] = HASH_VERSION
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


_rebuilt = False


def resolve(stamp, cache=None):
    """Semantic hash for a MODEL stamp read off a point file.

    Unknown stamps come back unchanged, so a point from a revision that was
    never committed still groups with itself and never with anything else.

    THE REBUILD HAPPENS AT MOST ONCE PER PROCESS. Rebuilding walks every
    revision of a 39,000 line file through `git show`, which takes seconds; the
    first version of this called it for EVERY unknown stamp and turned a gate run
    into a two-minute timeout. Most unknown stamps are genuinely unknown --
    points from revisions that were never committed -- so re-walking cannot help
    them and only costs.
    """
    global _rebuilt
    m = cache if cache is not None else build_map()
    if stamp not in m and not _rebuilt:
        _rebuilt = True
        fresh = build_map(force=True)
        m.update(fresh)
        if cache is not None:
            cache.update(fresh)
    return m.get(stamp, stamp)


if __name__ == '__main__':
    m = build_map(force=True)
    print(f'current semantic hash {current()}')
    print(f'{len(m)} revisions mapped, cached in {os.path.basename(CACHE)}')
