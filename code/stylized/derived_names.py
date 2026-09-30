"""
Names the prose quotes that are arithmetic on other generated names, computed at fill
time so they are never typed.  Round 9775f014 (the author, 30 September).

  s_vsl_data_musd   the full model's VSL target (f_vsl_data, 80) times mean household
                    income, in millions: "just say 80" -- aleph is fitted to 84 and the
                    text and Table 2's target column quote 80
  s1_cost_*_pc      the programme costs in PERCENT of mean income, so two decimals show
                    the difference ("these are identical!" at 0.021 and 0.021)
  s1_net_b_abs, s1_net_dir     "a 1.30 percentage point increase"
  s1_hf_vs_none     whether Housing First takes use above its level with no programme
  s4_close_frac_a   the share of the distance Treatment First closes, with its article
                    ("closes about eighth" read ungrammatically, and 0.157 is a sixth)
"""


def _f(x):
    return float(str(x).replace(',', ''))


_CLOSE = ((1.0, 'all'), (0.75, 'three quarters'), (2.0 / 3.0, 'two thirds'), (0.5, 'half'),
          (1.0 / 3.0, 'a third'), (0.25, 'a quarter'), (0.2, 'a fifth'), (1.0 / 6.0, 'a sixth'),
          (0.125, 'an eighth'), (0.1, 'a tenth'))


def derived(n):
    out = {}
    out['s_vsl_data_musd'] = f"{_f(n['f_vsl_data']) * _f(n['s_mean_hh_usd']) / 1e6:.1f}"
    out['s1_cost_tf_pc'] = f"{100 * _f(n['s1_cost_tf_b']):.2f}"
    out['s1_cost_hf_pc'] = f"{100 * _f(n['s1_cost_hf_b']):.2f}"
    net = _f(n['s1_net_b'])
    out['s1_net_b_abs'] = f'{abs(net):.2f}'
    out['s1_net_dir'] = 'increase' if net > 0 else 'decrease'
    out['s1_hf_vs_none'] = ('even higher than before a programme existed'
                            if _f(n['s1_part_hf_b']) > _f(n['s1_part_none_b'])
                            else 'back towards its level with no programme')
    x = _f(n['s3_cev_tf']) / _f(n['s4_cev_opt'])
    out['s4_close_frac_a'] = min(_CLOSE, key=lambda fw: abs(fw[0] - x))[1]
    # the share worse off against the share using, both on participation's footing
    # (stage_results.worse_share_exact), for "it is above the ... who use because ..."
    out['s1_worse_vs_part'] = 'above' if _f(n['s1_worse_b']) > _f(n['s1_part_hf_b']) else 'not above'
    # what kappa_x does to the gain from Treatment First, at the precision the text prints
    import fill
    a = fill.text_precision('s3_cev_tf_nokx', n['s3_cev_tf_nokx'])
    b = fill.text_precision('s3_cev_tf', n['s3_cev_tf'])
    out['s3_kx_phrase'] = ('it changes essentially nothing about the welfare gain from Treatment First, which remains at'
                           if a == b else
                           f'it barely changes the welfare gain from Treatment First, which moves from ${a}$ to')
    # the children born at the reform gain less than every cohort after them
    out['s4_tr_more'] = 'even more' if _f(n['s4_tr_c2']) > _f(n['s4_tr_c1']) else 'less'
    return out
