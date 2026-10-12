"""The driver of the model's Milby ratio (12 October, the author on the model's 1.19 against Milby's 1.26: "you need to
explain the driver of this gap").

A housed household's SUD recovery hazard depends only on treatment and SMI (eq. frecover), so the gap between voucher
holders and housed households without a voucher, both with a SUD, is a matter of who is in treatment and who has SMI.
The paper's two long-run arms were re-solved with a print of exactly that (code/treat/patch_treat.py, MODE split;
code/treat/remote_treat.sh split -> results/counterfactuals_2c/milby_split/{null,tf}/milby_split.txt): for housed
households with a SUD, by voucher status, the mass, the recovery-hazard sum, the mass in treatment and the mass with SMI.

usage: python3 code/paper/export_milby_split.py   -> x_milby_* split names merged into code/paper/results_numbers.json
(export_results.py rewrites that file whole, so run this after it, as export_revoked.py and the others.)"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
R = os.path.join(ROOT, 'results/counterfactuals_2c/milby_split')
NUM = r'[-+]?\d+\.\d+(?:[EeDd][-+]?\d+)?'


def split(arm):
    """shares in treatment and with SMI, by voucher status, and the voucher holders' recovery hazard over the others'"""
    line = [l for l in open(os.path.join(R, arm, 'milby_split.txt')) if 'MILBY SPLIT' in l][-1]
    mv, rv, tv, sv, mh, rh, th, sh = (float(x.replace('D', 'E')) for x in re.findall(NUM, line))
    return {'treat_v': tv / mv, 'treat_h': th / mh, 'smi_v': sv / mv, 'smi_h': sh / mh,
            'rec_v': rv / mv, 'rec_h': rh / mh, 'ratio': (rv / mv) / (rh / mh), 'mass_v': mv, 'mass_h': mh}


if __name__ == '__main__':
    tf, hf = split('tf'), split('null')
    out = {}
    for tag, s in (('tf', tf), ('hf', hf)):
        out[f'x_milby_{tag}_treat_v_pc'] = f"{100 * s['treat_v']:.0f}"
        out[f'x_milby_{tag}_treat_h_pc'] = f"{100 * s['treat_h']:.0f}"
        out[f'x_milby_{tag}_smi_v_pc'] = f"{100 * s['smi_v']:.0f}"
        out[f'x_milby_{tag}_smi_h_pc'] = f"{100 * s['smi_h']:.0f}"
        out[f'x_milby_{tag}_ratio'] = f"{s['ratio']:.2f}"
    d = json.load(open(OUT_JSON))
    p = json.load(open(os.path.join(HERE, 'fortran_numbers.json')))      # the Fortran declarations
    g, mu_m = float(p['f_treatment_effect_on_recovery']), float(p['f_mu_m'])
    # what each multiplier in eq. frecover alone makes of the ratio: the text says the gap is treatment's, so it must be
    # treatment's ratio that is above one and larger than SMI's effect, and the two must account for the ratio
    r_treat = (1 + (g - 1) * tf['treat_v']) / (1 + (g - 1) * tf['treat_h'])
    r_smi = (1 - (1 - mu_m) * tf['smi_v']) / (1 - (1 - mu_m) * tf['smi_h'])
    assert r_treat > 1 and abs(r_treat - 1) > abs(r_smi - 1), ('the gap is not treatment\'s', r_treat, r_smi)
    assert abs(r_treat * r_smi - tf['ratio']) < 0.01, (r_treat, r_smi, tf['ratio'])
    out['x_milby_tf_smi_clause'] = ('works the other way, since voucher holders have it more often'
                                    if tf['smi_v'] > tf['smi_h'] else
                                    'works the same way, since voucher holders have it less often')
    # the Treatment First arm's ratio is the transition's last period, which export_results.py reads from the path;
    # the two must agree, or the split is not of the economy the paper reports
    if 'x_milby_model_lr' in d:
        assert abs(float(d['x_milby_model_lr']) - tf['ratio']) < 0.011, (d['x_milby_model_lr'], tf['ratio'])
    # THE FIRST YEAR, MILBY'S HORIZON (12 October, the author: "you should use the short run change, not the long run.
    # the short run is the same horizon as milby"). The transition prints only the recovery hazards by voucher status
    # (TRANSITION MILBY t=), not who is in treatment. But in its first year the population is still Housing First's
    # (the masses are the null arm's to 0.1 percent), so its SMI shares are the null arm's, and a housed household's
    # hazard is pi_r * (g if treated) * (mu_m if SMI): the treatment share follows from the hazard. The same inversion,
    # applied to the four groups whose treatment shares ARE printed (both arms, both voucher statuses), must return
    # them to within a point, or the treatment and SMI shares are too correlated for it.
    pi_r = float(p['f_probability_of_stopping_addiction'])

    def treat_from_hazard(rec_rate, smi_share):
        return (rec_rate / (pi_r * (1 - (1 - mu_m) * smi_share)) - 1) / (g - 1)

    for s_, tag in ((tf, 'tf'), (hf, 'hf')):
        for grp in ('v', 'h'):
            inferred = treat_from_hazard(s_['rec_' + grp], s_['smi_' + grp])
            assert abs(inferred - s_['treat_' + grp]) < 0.01, (tag, grp, inferred, s_['treat_' + grp])
    sys.path.insert(0, HERE)
    from transition_source import LOG
    t1 = None
    for l in open(LOG, errors='replace'):
        if 'TRANSITION MILBY t=' in l and int(l.split('t=')[1].split()[0]) == 1:
            t1 = {k: float(v) for k, v in re.findall(r'(\w+)=\s*(\S+)', l) if k != 't'}
    assert t1, 'no first-year TRANSITION MILBY line in ' + LOG
    mv0, mh0 = hf['mass_v'], hf['mass_h']
    assert abs(t1['mass_voucher'] / mv0 - 1) < 1e-3 and abs(t1['mass_housed_nov'] / mh0 - 1) < 1e-3, (t1, mv0, mh0)
    tv1 = treat_from_hazard(t1['rec_voucher'] / t1['mass_voucher'], hf['smi_v'])
    th1 = treat_from_hazard(t1['rec_housed_nov'] / t1['mass_housed_nov'], hf['smi_h'])
    out['x_milby_t1_treat_v_pc'] = f"{100 * tv1:.0f}"
    out['x_milby_t1_treat_h_pc'] = f"{100 * th1:.0f}"
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')
