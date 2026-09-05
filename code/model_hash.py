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
    # drug_spending_share_data, added 5 September when the author moved theta's
    # target from 16.2 to 14.098 per cent. EVERY non-comment use was read before
    # adding it, which is the bar this list demands:
    #
    #   2269   the declaration
    #   6224   write, "MOMENT theta"
    #   39567  write, "drug share, weighted ... target ="
    #   39581  drug_share_gap_1, the theta stepper's clamped gap
    #   39641  distance_relative_share_of_addiction_1, the stepper's distance
    #   39656  a stepper condition, theta pinned at its ceiling
    #   39661  write inside that condition
    #   40580  write, "drug share ... target ="
    #
    # Not one of them is in a household's problem, a price or an equilibrium
    # condition. Writes and the outer stepper's gap only, which is the same
    # footprint as the two names already here.
    'drug_spending_share_data',
)

# Bumped whenever semantic() changes. The cache maps file bytes to a semantic
# hash, so a new rule makes every stored value wrong rather than merely stale --
# the map is rebuilt from git rather than trusted when this moves.
HASH_VERSION = 3

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


# A SOURCE CHANGE THAT IS INERT FOR SOME POINTS, and the machinery to say so.
#
# TARGET_CONSTANTS above handles a change that is inert for EVERY point. This
# handles the other case: a change whose whole effect sits behind a flag, so it
# is inert for exactly those points that ran with the flag off. That is a
# property of the POINT, not of the source, which is why it cannot be a plain
# entry in a source-to-source equivalence table and needs the point's vector.
#
# `when` is given the point file's text and returns True if the change could not
# have touched that run. Keep it conservative: a rule that wrongly pools two
# economies is far worse than one that wrongly splits them, because a split
# costs a re-solve and a pool corrupts a comparison silently.
INERT_CHANGES = [
    {
        'from': '841e04b785',
        'to':   'f9048e2563',
        'what': 'restrict_borrowing_to_impatient bars the patient type from the '
                'negative asset grid',
        'why':  'Every line of it is inside `if (include_unsecured_borrowing==1)` '
                '-- the branch in set_renter_floor and the distribution '
                'projection in the beta-type pass loop alike. The one addition '
                'that runs unconditionally is a second call to set_renter_floor, '
                'which recomputes the same constant array when borrowing is off. '
                'So a point with borrowing off executes identically either side '
                'of the merge.',
        'careful': 'This says NOTHING about a borrowing-ON point. An ON point '
                   'measured before the merge ran with BOTH types on the negative '
                   'grid and is a different economy from one measured after. Those '
                   'must never pool, which is exactly what the flag test below '
                   'prevents.',
        'when': lambda text: re.search(r'include_unsecured_borrowing=0(?![.0-9])',
                                       text) is not None,
    },
    {
        'from': 'f9048e2563',
        'to':   '6d75e61a1d',
        'what': "a renter's negative position is unsecured debt, not a mortgage",
        'why':  'Three sites read min(financial_grid,0) three different ways. The '
                'optimiser scaled the principal by housing_price*housing_size, the '
                'budget check dropped it via max(amortization_used-1,0), and the '
                'fifteen interest sites treated it as absolute. All three now agree '
                'with the absolute reading, which is what the grid is built in. '
                'WITH BORROWING OFF THIS IS PROVABLY A NO-OP: renter_floor_by_age '
                'puts a renter at the zero index, so min(financial_grid,0) is zero '
                'and every branch vanishes.',
        'careful': 'Says nothing about a borrowing-ON point. Every ON point measured '
                   'before this ran an economy whose budget did not clear at 250,039 '
                   'states, and none of them may pool with one measured after.',
        'when': lambda text: re.search(r'include_unsecured_borrowing=0(?![.0-9])',
                                       text) is not None,
    },
    {
        'from': 'd2779837ff',
        'to':   '5bf42a9b2c',
        'what': "the productivity process became switchable, and KKK_process "
                "was made usable for the first time",
        'why':  'Every line of it is inert when fixed_productivity is 1, and it '
                'is 1 in the declaration and in run_one_point.sh. The grid '
                'fix-ups -- the retirement rows, the mean-one normalisation, '
                'log_y_edge, sd_log_y_newborn -- all run before the quantile '
                'construction, which REBUILDS employment_grid from tail_mean_1, '
                'rebuilds unconditional_employment_probability from p_edge_1, and '
                'overwrites log_y_edge from sd_permanent_productivity. The '
                'newborn-parent-share initialiser, the pooled bottom-half share '
                'and the kkk_sigma_scale calibration step are each inside '
                '`if (fixed_productivity==0)`. The width fix in '
                'get_probabilities_KKK_process repairs a routine whose outputs '
                'are discarded on this path -- the masses by the quantile '
                'construction, the transition by the identity loop that starts '
                'at age one. The social security base moved from '
                'employment_grid(1,i) to employment_grid(life_span-'
                'retirement_span,i), and every row of that array is assigned '
                'employment_grid(1,:) a few lines earlier, so the two are the '
                'same number. compute_bottom_half_earnings_share was extracted '
                'to a subroutine that additionally SORTS its nodes, which is a '
                'no-op here because the quantile nodes are already ascending in '
                'index. The state file gained one field at its tail, behind an '
                'iostat guard, and a point starts cold.',
        'careful': 'The one thing that was NOT inert is now gated so that it is: '
                   'the BLS unemployment tilt is divided by its mass-weighted '
                   'mean only when fixed_productivity is 0. On the quantile '
                   'masses that divisor is 1.000017 -- a rounding artefact of '
                   'quoting the vector to four decimals -- and dividing by it '
                   'would have moved every archived point by 1.7 parts in a '
                   'hundred thousand and split 611 of them onto a new hash for '
                   'nothing. On the KKK grid the masses genuinely differ and the '
                   'renormalisation does real work, which is why it is kept '
                   'there. This rule says NOTHING about a fixed_productivity=0 '
                   'point: those are a different economy in every respect and '
                   'none of them existed before this change.',
        'when': lambda text: re.search(r'fixed_productivity=0(?![.0-9])',
                                       text) is None,
    },
    {
        'from': '5bf42a9b2c',
        'to':   '6c3b8a9a23',
        'what': 'bottom_productivity_level applies under KKK too, at every age',
        'why':  'The whole addition sits inside the `if (fixed_productivity==0)` '
                'housekeeping block, which a quantile point never enters. The '
                'quantile grid keeps its own bottom-node override, unchanged and '
                'in its own branch a few hundred lines above. Nothing outside '
                'that block was touched.',
        'careful': 'Says NOTHING about a fixed_productivity=0 point. Under KKK '
                   'this is the difference between a lever that does nothing and '
                   'one that moves the bottom node at every age, so a KKK point '
                   'measured before this change is a different economy from one '
                   'measured after -- and none existed before it.',
        'when': lambda text: re.search(r'fixed_productivity=0(?![.0-9])',
                                       text) is None,
    },
    {
        'from': '6c3b8a9a23',
        'to':   'ae10d02fc7',
        'what': "sigma_y is scored on the bottom half's share of LABOUR INCOME, "
                "emp_homeless is emitted as a MOMENT rather than as UNTARGETED",
        'why':  'Neither touches the economy. The first adds a second histogram '
                'beside the income one, filled in the same distribution sweep from '
                'labor_supply x employment_grid x labour_deterministic_efficiency '
                'for working-age households in work, and walks it to the median; '
                'nothing reads it back into a policy, a price or an adjuster. The '
                'second changes the wording of one write statement. Every state, '
                'every policy function and every equilibrium object is bit for bit '
                'what it was, so a point measured either side of this is the same '
                'economy and the archive pools across it.',
        'careful': 'INERT DOES NOT MEAN COMPARABLE, and here the distinction bites. '
                   'sigma_y named the bottom half share of PRODUCTIVITY before this '
                   "and the bottom half share of EARNINGS after it -- same target, "
                   '0.172, different statistic. Pooling the model economy is right; '
                   'pooling that MOMENT is not. STALE_LABEL in next_batch.py drops '
                   "the old label and gaps.py does the same, so an archived point "
                   'keeps all its other moments and loses only sigma_y, which is '
                   'the correct outcome and is why this entry is safe.',
        'when': lambda text: True,
    },
    {
        'from': 'ae10d02fc7',
        'to':   '092d9e6232',
        'what': "ssi_floor_level is handed in, so the floor's LEVEL can be set "
                "and not only its take-up",
        'why':  'One new case in the handover select, reachable only when a '
                'point names ssi_floor_level in its vector. Nothing else in the '
                'source changed: the benefit arithmetic, the floor comparison '
                'and every other declaration are byte for byte what they were, '
                'and the variable keeps its declared 0.1774. A point that does '
                'not hand the name in runs the identical economy, which is '
                'every point in the archive.',
        'careful': 'It is inert only AT THE LEGACY VALUE. 0.1774 is the 2024 '
                   'federal benefit rate over the average wage index -- it is '
                   'the DATA -- so a point handing in anything else is running a '
                   'different policy environment and must not pool with one that '
                   'is not. The condition below is what enforces that: any '
                   'vector naming a non-legacy ssi_floor_level fails it. '
                   'LEGACY_DEFAULT in run_one_point.sh separately keeps the name '
                   'out of the tag at 0.1774, so no existing point changes '
                   'identity.',
        'when': lambda text: re.search(
            r'ssi_floor_level=(?!0\.1774(?![0-9]))', text) is None,
    },
    {
        'from': '092d9e6232',
        'to':   '5f2fa9f347',
        'what': "a retired renter's DIAG income is their own pension, not the "
                "economy's average wage",
        'why':  'income_by_age_renter is written to the DIAG age line and read '
                'nowhere else -- not by a policy, a price, an adjuster or an '
                'invariant -- so correcting it cannot change any equilibrium '
                'object. The retirement branch now calls calculate_income, the '
                'same routine the model uses, instead of adding an aggregate to '
                'a per-household accumulator.',
        'careful': 'Inert for the ECONOMY, not for anyone reading the column. '
                   'Every archived point reports each retired renter at the same '
                   'number -- 12.2973 flat from age 66 to 85 on point_5c436e0799 '
                   '-- which is the aggregate average labour income and not a '
                   'pension. Do not compare that column across the change, and '
                   'do not use it on an archived point to reason about '
                   'retirement income at all.',
        'when': lambda text: True,
    },
]


def resolve_for_point(stamp, text, cache=None):
    """Semantic hash for a point, allowing for changes inert at ITS vector.

    Falls back to resolve() when no inert rule applies, so a point that does not
    meet a rule's condition groups exactly as it did before.
    """
    h = resolve(stamp, cache)
    seen = set()
    while h in seen or True:
        seen.add(h)
        for ch in INERT_CHANGES:
            if h == ch['from'] and ch['when'](text):
                h = ch['to']
                break
        else:
            return h
        if h in seen:
            return h


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
