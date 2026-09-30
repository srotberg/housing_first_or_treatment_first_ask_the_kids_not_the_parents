"""Can stage 2 sit at a VSL of 80, the quantitative model's, without a negative value of
life at the drug decision?  (The author, 30 September: "can you hit 80 in this stage 2? or
do you have to hit 84 to prevent negative value of life?")

aleph is bracketed on a VSL of 80 at stage 2's calibration with every other parameter held,
and the value of life at the drug decision, after the employment draw, is checked under
both programmes; the calibrated stage 2 (VSL 84) is checked beside it.  Nothing else is
refitted, so the other moments move a little; they are printed.  Log only.

usage:  STYLIZED_WORKERS=<n> python3 check_vsl80.py
"""
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket
from negative_value_of_life import period1_negative_values, occupied_negative_values

q84, _ = R.load(2)
q84 = ST.solve_child_damage(q84)          # stats() needs the child's damage in place
a80 = bracket(q84, 'aleph', 'vsl', 1.0, q84.aleph, iters=30, tgt=80.0)
for label, q in (('calibrated, VSL 84', q84), ('VSL 80, aleph refit, rest held', with_(q84, aleph=a80))):
    q = ST.solve_child_damage(q)
    m = stats(q)
    print(f'{label}: aleph {q.aleph:.3f}, VSL {m["vsl"]:.2f}, participation {100*m["part"]:.2f}, '
          f'homeless {100*m["homeless"]:.3f}, users income {m["r_use"]:.3f}', flush=True)
    for pol in ('HF', 'TF'):
        v = period1_negative_values(q, pol)
        ov = occupied_negative_values(q, pol)
        print(f'   {pol}: at the drug decision {v["cells"]} negative states '
              f'({100*v["share"]:.3f} per cent of households), lowest {v["lowest"]:.3f} at {v["where"]}; '
              f'period 2 occupied: {ov["cells"]} negative cells', flush=True)
