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
  s1_bb_frac        the budget-neutral CEV as a fraction of the same-generosity one ("about half of the")
  s2_split          whether stage 2's gain splits evenly between childhood and adult life
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
    # the employment penalty of homelessness in percent, for the introduction (round r147, the author: "how much more
    # likely a parent is to be unemployed because of homelessness")
    if 'c_kappa_h_value' in n:
        out['c_kappa_h_pc'] = f"{100 * _f(n['c_kappa_h_value']):.0f}"
    out['s_vsl_data_musd'] = f"{_f(n['f_vsl_data']) * _f(n['s_mean_hh_usd']) / 1e6:.1f}"
    out['s1_cost_tf_pc'] = f"{100 * _f(n['s1_cost_tf_b']):.2f}"
    out['s1_cost_hf_pc'] = f"{100 * _f(n['s1_cost_hf_b']):.2f}"
    net = _f(n['s1_net_b'])
    out['s1_net_b_abs'] = f'{abs(net):.2f}'
    out['s1_net_dir'] = 'increase' if net > 0 else 'decrease'
    out['s1_hf_vs_none'] = ('above what it was before a programme existed'
                            if _f(n['s1_part_hf_b']) > _f(n['s1_part_none_b'])
                            else 'back towards its level with no programme')
    # the budget-neutral footnote's cost of keeping Housing First as a share of the same-generosity one (round r178, the
    # author: "about half of the ...")
    out['s1_bb_frac'] = min(_CLOSE, key=lambda fw: abs(fw[0] - _f(n['s1_bb_cevpop']) / _f(n['s1_cevpop_b'])))[1]
    x = _f(n['s3_cev_tf']) / _f(n['s4_cev_opt'])
    out['s4_close_frac_a'] = min(_CLOSE, key=lambda fw: abs(fw[0] - x))[1]
    # the share worse off against the share using, both on participation's footing
    # (stage_results.worse_share_exact), for "it is above the ... who use because ..."
    out['s1_worse_vs_part'] = 'above' if _f(n['s1_worse_b']) > _f(n['s1_part_hf_b']) else 'not above'
    # what kappa_x does to the gain from Treatment First, at the precision the text prints
    import fill
    a = fill.text_precision('s3_cev_tf_nokx', n['s3_cev_tf_nokx'])
    b = fill.text_precision('s3_cev_tf', n['s3_cev_tf'])
    out['s3_kx_phrase'] = ('it changes essentially nothing about the welfare gain from Treatment First in the stylized model, which remains at'
                           if a == b else
                           f'it barely changes the welfare gain from Treatment First in the stylized model, which moves from ${a}$ to')
    # how the stage 2 gain splits between childhood and adult life (round r185, the author: "Breaking the gains by
    # periods of life shows a rather even split"), as words that turn if the two parts drift apart
    r = _f(n['s2_cev_tf_kid']) / _f(n['s2_cev_tf_adult'])
    out['s2_split'] = ('a rather even split' if 2.0 / 3.0 <= r <= 1.5 else
                       'that most of the gain comes in adult life' if r < 2.0 / 3.0 else
                       'that most of the gain comes in childhood')
    # the end of the full model's homelessness overshoot (6 October, the T = 60 run's second iterate): the long run
    # can sit either side of Housing First, and "against $-1$ percent" read badly
    if 'x_trf_h_lr_pc' in n:
        v = _f(n['x_trf_h_lr_pc'])
        out['x_trf_h_tail'] = (f'and then declines slowly towards its long-run level, ${abs(v):g}$ percent below that under Housing First'
                               if v < 0 else
                               f'against ${v:g}$ percent in the long run, and then declines slowly towards it')
    # the most the gain from Treatment First could fall if all of the part that comes in childhood shrank with the
    # share of users living with a child, against comparable non-users (7 October, the author: "the gaps are not orders
    # of magnitude... The gains are maybe 15% lower but it won't reverse them")
    # how much less likely users are to live with a child than comparable non-users, for the bound's arithmetic
    # (8 October, the author: "why not 20%? 48 to 40, is 20%, no?")
    if 'nsduh_kh_sud_ratio' in n:
        out['nsduh_kh_sud_gap_pc'] = f"{100 * (1.0 - _f(n['nsduh_kh_sud_ratio'])):.0f}"
    if 'nsduh_kh_sud_ratio' in n and 'x_tf_child_share_pc' in n:
        out['x_kh_gain_bound_pc'] = f"{_f(n['x_tf_child_share_pc']) * (1.0 - _f(n['nsduh_kh_sud_ratio'])):.0f}"
    # the lone-parent comparison in the omega_c item (7 October, the author: "lone parent plus child vs couple no kids"):
    # whether the range against unmarried two-adult households contains the target, and what the married range does
    if 'nsduh_lp_unm_lo_pc' in n and 'c_omega_c_data' in n:
        lo, hi, t = _f(n['nsduh_lp_unm_lo_pc']), _f(n['nsduh_lp_unm_hi_pc']), _f(n['c_omega_c_data'])
        out['nsduh_lp_contains'] = ('a range that contains' if lo <= t <= hi else
                                    'a range wholly above' if t < lo else 'a range wholly below')
        ml, mh = _f(n['nsduh_lp_mar_lo']), _f(n['nsduh_lp_mar_hi'])
        out['nsduh_lp_mar_phrase'] = ('changes sign with the weighting and with the income held equal' if ml < 0 < mh else
                                      f'runs from ${ml:g}$ to ${mh:g}$ percent')
    # the children born at the reform gain less than every cohort after them
    out['s4_tr_more'] = 'even more' if _f(n['s4_tr_c2']) > _f(n['s4_tr_c1']) else 'less'
    return out
