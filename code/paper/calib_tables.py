"""
Tables 5, 6 and 7, and the numbers Section 5 quotes, read from the benchmark.

usage: python3 code/paper/calib_tables.py

WHY THIS EXISTS. sync_tables.py writes a row's Data cell from a Fortran
declaration, which is right for a target and wrong for a parameter's value: most
calibrated values are set at run time from the handover file, and the
declarations are only starting points (kappa_phi_d_level is declared 8 and runs
at 4; kappa_x is declared 0.002 and runs at 0.9329). The Model column was never
filled at all. This reads the places the numbers live:

  the benchmark's handover   results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt
                             every run-time parameter value
  the benchmark's log        results/reference/hf_omega_c_006_tdm/bench.log.gz
                             every MOMENT and UNTARGETED line, the voucher
                             probability, the kappa_x probe, and the gaps table
                             (code/gaps_table.py) for theta and the HELD verdicts
  the Fortran declarations   code/paper/fortran_consts.py, for the data targets
  the omega_c scan           results/omega_c_scan/SCAN_READINGS.md, drug use at
                             omega_c = 0 with every other parameter the same

and writes the body rows of writing/tables/tab_eleven.tex, tab_standard.tex and
tab_untargeted.tex (captions, column specs and notes are left alone), and
code/paper/calib_numbers.json, one c_<name> per number the prose quotes.

THE BENCHMARK is the Housing First economy at omega_c = 0.06. Its parameters
were calibrated at omega_c = 0 against drug use and SUD targets raised by
UPLIFT = 1.18, the author's rule of 18 September (f90, at
participation_rate_data), and then held while omega_c was raised to 0.06. The
Model column is that benchmark; for b the Data column is the NSDUH figure, the
declared target divided by UPLIFT, and pi_d is on the SUD share of users, which
the uplift leaves where it was.

NO DAGGER (the author, 1 October: "I think we should abandon the idea of this cross
and 'held'. all the parameters we chosen to match something as best as i could").
Every internally calibrated parameter is Int.; HELD is still computed and printed,
for the record, but no longer marks the table.
"""
import gzip
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from fortran_consts import constants

BENCH = os.path.join(ROOT, 'results', 'reference', 'hf_omega_c_006_tdm')
TAB = os.path.join(ROOT, 'writing', 'tables')
OUT = os.path.join(HERE, 'calib_numbers.json')
SCAN = os.path.join(ROOT, 'results', 'omega_c_scan', 'SCAN_READINGS.md')
UPLIFT = 1.18

C = constants()
AGE0 = 25                                     # j = 1 is age 26
J_MAX = int(C['life_span'])
J_RET = int(C['life_span'] - C['retirement_span'] + 1)
H = {}
for l in open(os.path.join(BENCH, 'PARAM_HANDOVER.bench.txt')):
    p = l.split()
    if len(p) >= 2:
        try:
            H[p[0]] = float(p[1].replace('D', 'E'))
        except ValueError:
            pass

LOG = gzip.open(os.path.join(BENCH, 'bench.log.gz'), 'rt', errors='replace').read()
M = {}
for l in LOG.splitlines():
    m = re.match(r'\s*(MOMENT|UNTARGETED)\s+(.*?)\s+model=\s*(\S+)(?:\s+(?:target|observed)=\s*(\S+))?', l)
    if m:
        M[re.sub(r'\s+', ' ', m.group(2).strip())] = (
            float(m.group(3)), float(m.group(4)) if m.group(4) else None)

PI_V = float(re.findall(r'probability_of_voucher=\s*(\S+)', LOG)[-1])
# The probe prints two pairs, at x = 0.2 per cent (Loubiere) and at 0.08; the
# last block's first pair is the one the table quotes.
KX_X = float(re.findall(r'KAPPA_X PROBE: giving up x=\s*(\S+)', LOG)[-2])
KX_IMPLIED = float(re.findall(r'KAPPA_X PROBE: IMPLIED kappa_x=\s*(\S+)', LOG)[-2])
KX_WTP = KX_X * H['kappa_x'] / KX_IMPLIED        # what the coded kappa_x is worth

# the gaps table, for theta on the aggregate and for the HELD verdicts
with tempfile.NamedTemporaryFile('w', suffix='.log', delete=False) as t:
    t.write(LOG)
G = {}
out = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'gaps_table.py'), t.name],
                     capture_output=True, text=True).stdout
os.unlink(t.name)
for l in out.splitlines():
    p = l.split()
    if len(p) >= 4 and re.fullmatch(r'[a-zA-Z_0-9]+', p[0]) and p[0] != 'parameter':
        G[p[0]] = l
HELD = {k for k, l in G.items() if ' HELD' in l and 'rate inside the band' not in l}
HELD.add('kappa_uem')                             # adjuster zeroed; not in the gaps table
# h_2 IS HELD TOO (audit, 29 September): the benchmark's handover zeroes
# smallest_house_size_adjuster, which the gaps table cannot see because it reads
# the Fortran declaration (0.05), so h_2 = 0.0407 did not move in the final round.
if H.get('smallest_house_size_adjuster', 1.0) == 0.0:
    HELD.add('h2')
# AVERAGE LABOUR INCOME, the scale the SSI floor is quoted against: the floor is
# applied to productivity (mean one at entry), and the log prints the food
# allotment over average labour income, so the two give the level.
AVG_LAB = H['max_food_cost'] / float(
    re.findall(r'DIAG max allotment / avg labour income\s*=\s*(\S+)', LOG)[-1])
THETA_AGG = float(G['theta'].split()[2])
SMI_USE = json.load(open(os.path.join(ROOT, 'code', 'paper', 'smi_use_ratio.json')))
# THE DRUG PRICE ELASTICITIES (the author, round ae7a28ed: "where is the extensive and
# intensive drug price elasticities? they should be in the table"): export_elasticity.py's
# averages, the same names Section 2 quotes; the data side is the literature range it types.
RES = json.load(open(os.path.join(ROOT, 'code', 'paper', 'results_numbers.json')))
THETA_NOSUD = float(re.findall(r'drug share, sum spend / sum income\s*=\s*(\S+)\s+(\S+)', LOG)[-1][1])

# omega_c: drug use with the child's weight off and every other parameter the same
scan = open(SCAN).read()
B_OFF = float(re.search(r'reference is therefore b = ([0-9.]+)', scan).group(1))
B_ON = M['b total drug users'][0]
RISE = B_OFF / B_ON - 1


def mom(key, which=0):
    return M[key][which]


def pc(x, nd=1):
    return f'{100 * x:.{nd}f}\\%'


def f(x, nd=2):
    return f'{x:.{nd}f}'


def setcol(gapkey):
    return 'Int.'


NA = 'n.a.'
SIG_UPS = H['kkk_sigma_scale'] * H['sd_employment_surviving']
SD_ENTRY = H['kkk_sigma_scale'] * math.sqrt(
    H['sd_employment_surviving'] ** 2
    + H['sd_fixed_employment_newborn'] ** 2 / (1 - H['persistence_fixed_employment_newborn'] ** 2))

# (symbol, description, set, moment and source, data, model, value)
ELEVEN = [
    ('Who uses drugs', [
        (r'$\theta$', 'Weight on drugs in utility', setcol('theta'),
         r'Drug spending over income, Midgette et al.\ (2019)',
         pc(C['drug_spending_share_data']), pc(THETA_AGG), f(H['relative_share_of_addiction_1'], 3)),
        (r'$b$', 'Whether a household uses at all', setcol('b'), 'Drug participation, NSDUH 2024',
         pc(C['participation_rate_data'] / UPLIFT, 2), pc(mom('b total drug users'), 2),
         f(H['addiction_scalar_1'], 4)),
        (r'$\pi_d$', 'Chance that a year of use leads to a SUD', setcol('addiction_onset_base'),
         'Share of users carrying a SUD, NSDUH 2024',
         pc(C['sud_rate_data'] / C['participation_rate_data']),
         pc(mom('lambda_d disorder rate') / mom('b total drug users')),
         f(H['addiction_onset_base'], 4)),
        (r'$\kappa_{\phi d}$', 'Increased mortality with a SUD', setcol('kappa_phi_d_level'),
         'Income of drug users over average, NSDUH 2024',
         pc(C['drug_user_income_data'], 0), pc(mom('y_u income of drug users'), 0),
         f(H['kappa_phi_d_level'])),
        (r'$\aleph$', 'Flow value of being alive', setcol('aleph'),
         r'VSL, Viscusi and Aldy (2003)',
         f(C['vsl_data'], 0), f(mom('aleph value of life / income'), 0), f(H['value_of_life'], 1)),
    ]),
    ('Costs of homelessness and vouchers', [
        (r'$\kappa^{ue}_{d}$', 'How much harder it is to regain employment with a SUD', setcol('find_if_addicted'),
         r'SUD share of the homeless, Gutwinski et al.\ (2021)',
         pc(C['sud_share_of_homeless']), pc(mom('sud_homeless SUD share of the homeless')),
         f(H['multiple_find_if_addicted'])),
        # kappa^eu_d HAS NO ROW: it is one in the benchmark (clamped at its floor),
        # so the SUD does not raise separations and the parameter is inert (audit,
        # 29 September); Section 4 no longer carries it.
        (r'$h_1$', 'Service flow of homelessness', 'Int.',
         'Homelessness rate, HUD PiT 2023, within a band',
         f'{100 * C["h1_band_lo"]:.2f}--{100 * C["h1_band_hi"]:.2f}\\%',
         pc(mom('h_1 homelessness rate'), 2), f(H['size_homelessness'], 4)),
        (r'$\kappa_{\phi H}$', 'Mortality when homeless', 'Ext.',
         r'Meyer et al.\ (2023)',
         f(1 + C['increased_risk_of_death_homeless']), NA, f(1 + C['increased_risk_of_death_homeless'])),
        (r'$\kappa_{H}$', 'Employment penalty of homelessness', 'Ext.', r'Desmond and Gershenson (2016)',
         f(H['increased_prob_if_homeless']), NA, f(H['increased_prob_if_homeless'])),
        (r'$\underline c$', 'Food stamp maximum allotment', setcol('c_bar'),
         'Food stamps over output (GDP), USDA',
         pc(C['food_stamps_share_data'], 2), pc(mom('cbar food stamps / income'), 2),
         f(H['max_food_cost'], 4)),
        (r'$\pi_V$', 'Chance of drawing a voucher', setcol('pi_v'),
         'Recipients over eligible, HUD 2023',
         pc(C['voucher_coverage_data']), pc(mom('pi_V eligibles with a voucher')), f(PI_V, 4)),
        (r'$T_0$', 'Endowment at entry to adulthood ($j=1$)', setcol('newborn_endowment'),
         'Share of homeless aged 25 to 34, HUD PiT 2024',
         pc(mom('share of the homeless, band 1', 1)), pc(mom('share of the homeless, band 1')),
         f(H['newborn_endowment_scale'], 3)),
    ]),
    ('SMI chain', [
        (r'$\iota$', 'SUD multiplier on SMI onset', 'Ext.', r'Danish registers, Nielsen et al.\ (2017)',
         f(C['iota_smi']), NA, f(C['iota_smi'])),
        (r'$\lambda_m$', 'Annual chance of recovering from SMI', 'Ext.',
         r'SMI ten-year recovery rate, {\AA}sb{\o} et al.\ (2022)',
         pc(C['smi_ten_year_recovery_data'], 0), NA, f(H['lambda_m'], 3)),
        (r'$\omega_m$', 'Level of the SMI onset profile', setcol('p_m'),
         'SMI share of the population, NSDUH 2024',
         pc(mom('p_m SMI population share', 1), 2), pc(mom('p_m SMI population share'), 2),
         f(H['smi_onset_level'], 4)),
        (r'$\kappa^{ue}_{m}$', 'How much harder it is to regain employment with SMI', setcol('kappa_find_smi'),
         r'SMI share of the homeless, Gutwinski et al.\ (2021)',
         pc(C['smi_share_of_homeless_data'], 0), pc(mom('lambda_m SMI share of the homeless')),
         f(H['kappa_find_smi'])),
        # kappa^eu_m IS GONE (the author, 1 October: "I think this was fixed at 1, no?
        # we only calibrated the ue case"): kappa_uem is 1, so SMI, like the SUD, acts
        # only on job finding, and the row and the term in the paper's equation went.
        (r'$\mu_m$', 'SUD recovery multiplier for SMI', 'Ext.',
         r'Dual diagnosis relapse, Bradizza et al.\ (2006)', f(C['mu_m']), NA, f(C['mu_m'])),
        (r'$\kappa_{\phi m}$', 'Mortality multiplier for SMI', 'Ext.', r'Olfson et al.\ (2015)',
         f(C['kappa_phi_m']), NA, f(C['kappa_phi_m'])),
    ]),
    ('Recovery and treatment', [
        (r'$\bar\pi_r$', 'Baseline SUD recovery rate', 'Ext.', r'SUD ten-year remission rate, Vaillant (1995)',
         f(H['probability_of_stopping_addiction'], 3), NA, f(H['probability_of_stopping_addiction'], 3)),
        (r'$\mu_H$', 'SUD recovery when homeless', setcol('mu_H'),
         r'Abstinence, housed/homeless, Milby et al.\ (2005)',
         f(C['milby_recovery_ratio_data']), f(mom('mu_H recovery housed / homeless')),
         f(H['mu_homeless'], 3)),
        (r'$g$', 'Treatment effect on recovery', 'Ext.',
         'Remission with medication for opioid use disorder',
         f(C['treatment_effect_on_recovery']), NA, f(C['treatment_effect_on_recovery'])),
        (r'$\bar\tau^{u}$', 'Utility cost of treatment', setcol('tau_u'), 'Treatment take-up, NSDUH 2024',
         pc(C['treatment_take_up_data']), pc(mom('tau_u treatment take up')),
         f(H['utility_cost_of_treatment'])),
    ]),
    ('Externalities', [
        (r'$\omega_c$', "Parent's weight on its child", 'Int.',
         "Non-parents' use over parents', NSDUH 2024",
         pc(C['child_use_gap_data']), pc(RISE), f(H['weight_on_child'])),
        (r'$\delta_d$', "Earnings the child loses to a parent's SUD", 'Ext.', r'Earnings lost in utero, Nilsson (2017)',
         f(C['penalty_child_addicted']), NA, f(H['penalty_child_addicted'])),
        (r'$\kappa_x$', 'Disamenity of homelessness', 'Ext.',
         r'Willingness to pay, Loubi\`ere et al.\ (2020)',
         # THE MODEL CELL IS ON THE INCOME BASIS, like the data's (the author, 1 October:
         # "you should still use 0.2% since it is income terms too"): kappa_x = 0.93 was
         # set on 24 September so that the willingness to pay is Loubiere's 0.2 per cent
         # of income (CALIBRATION_STATE.md), so the cell is that share by construction.
         # KX_WTP, the same amount against consumption, is c_kappa_x_cons for the prose.
         pc(KX_X, 2), pc(KX_X, 2), f(H['kappa_x'])),
    ]),
    ('Drug market', [
        (r'$\varepsilon_s$', 'Price elasticity of drug supply', 'Ext.', r'Mace et al.\ (2020)',
         f(C['drug_supply_elasticity']), NA, f(C['drug_supply_elasticity'])),
    ]),
]

STANDARD = [
    ('Preferences', [
        (r'$\sigma$', 'Risk aversion', 'Ext.', r'Attanasio and Weber (2010)',
         f(C['risk_aversion_consumption']), NA, f(C['risk_aversion_consumption'])),
        (r'$\gamma$', 'Weight on housing services', setcol('gamma'),
         'Housing over expenditure net of drugs, CEX 2024',
         pc(C['housing_share_of_expenditure_data']), pc(mom('gamma housing over expenditure')),
         f(H['relative_share_of_housing'], 3)),
        (r'$\beta$', 'Discount factor', setcol('beta'), 'Wealth over output, BEA fixed assets',
         f(C['wealth_to_output_data']), f(mom('beta wealth over output')), f(H['discount_factor'], 3)),
        (r'$\xi_j$', 'Equivalence scale', 'Ext.', 'Square-root scale, OECD',
         f(math.sqrt(2)), NA, f(math.sqrt(2))),
    ]),
    ('Rental ladder', [
        # THE TWO BURDEN CUTS SWAPPED (the author, 1 October: "maybe it's better to use that
        # for the h2 calibration point ... and use the 30% in the validation ... just swap
        # them"): h_2's row reads the over-half share, the 30 per cent one is untargeted. The
        # Fortran's h_2 rule still brackets on the 30 per cent cut; h_2 is held in every run
        # until the next full calibration, which must switch the rule first.
        (r'$h_2$', 'Smallest rental size', setcol('h2'), r'Renters paying over half of income, SCF 2022',
         pc(C['renter_burden_50_data']), pc(mom('over half of income, all renters')),
         f(H['smallest_rental_relative_to_lowest_income'], 4)),
        (r'$h_3/h_2$', 'Middle rung over the smallest', 'Ext.', 'Set', f(H['rung_ratio_h3']), NA,
         f(H['rung_ratio_h3'])),
        (r'$h_4/h_2$', 'Largest rung over the smallest', 'Ext.', 'Set', f(H['rung_ratio_h4']), NA,
         f(H['rung_ratio_h4'])),
    ]),
    ('Earnings and employment', [
        # THE HORIZON (the author, round b8142d12: "You never set J=60 and J_R=41 anywhere"):
        # life_span and retirement_span from the declarations; j = 1 is age 26
        (r'$J$', 'Maximum age', 'Ext.', f"Age {AGE0 + J_MAX}, end of the SSA life table",
         f'{J_MAX}', NA, f'{J_MAX}'),
        (r'$J_R$', 'Retirement age', 'Ext.', f"Age {AGE0 + J_RET}, SSA full retirement age",
         f'{J_RET}', NA, f'{J_RET}'),
        (r'$\varepsilon(j)$', 'Age profile of efficiency', 'Ext.',
         r'Hump peaking at age 56, Greenwood et al.\ (2025)', 'profile', NA, 'profile'),
        (r'$\rho_z$', 'Persistence of productivity', 'Ext.', r'Guvenen et al.\ (2023b)',
         f(H['persistence_employment_surviving']), NA, f(H['persistence_employment_surviving'])),
        (r'$\sigma_\zeta$', 'Standard deviation of its shocks', setcol('sigma_y'),
         "Bottom half's share of earnings, SCF 2022",
         pc(C['bottom_half_earnings_share_data']), pc(mom('sigma_y bottom half labour income share')),
         f(SIG_UPS, 3)),
        (r'$\rho$', 'Persistence of productivity across generations', 'Ext.',
         r'Solon (1992), Mazumder (2005)', f(C['rho_intergenerational']), NA,
         f(C['rho_intergenerational'])),
        (r'$\bar\pi^{eu}$', 'Job separation rate', setcol('pi_eu'), 'Unemployment rate, BLS CPS 2014--24',
         pc(C['unemployment_rate_data']), pc(mom('pi_eu unemployment rate')),
         f(H['probability_becoming_unemployed'], 4)),
        # how the separation tilt is set (the author, round b8142d12: "shouldn't you explain
        # how this parameter is set?!"): data/UNEMPLOYMENT_BY_PRODUCTIVITY.md
        (r'$\varpi(y)$', 'Separations by productivity', 'Ext.', 'Unemployment by education, BLS 2019',
         'profile', NA, 'profile'),
        (r'$\bar\pi^{ue}$', 'Annual job finding rate', 'Ext.', r'Krueger et al.\ (2014)',
         f(C['probability_becoming_employed']), NA, f(C['probability_becoming_employed'])),
        # BLS USDL-23-0586 (the author, round b8142d12): about 7 in 10 of the unemployed who
        # worked in the past year had not applied for UI; related_lit/ holds the release
        (r'$p_{ui}$', 'Share of separations that are insured', 'Ext.', 'UI applicants among the unemployed, BLS 2022',
         f(C['probability_of_ui']), NA, f(C['probability_of_ui'])),
    ]),
    ('Baseline survival and SMI onset', [
        (r'$\bar\phi_j$', 'Baseline survival by age', 'Ext.', 'SSA period life table, ages 26 to 85',
         'profile', NA, 'profile'),
        (r'$\varsigma_m(j)$', 'Age profile of SMI onset', 'Ext.', 'SMI prevalence by age, NSDUH 2024',
         'profile', NA, 'profile'),
    ]),
    ('Interest and taxes', [
        (r'$r$', 'Risk-free rate', 'Ext.', r'Kaplan et al.\ (2020)',
         f(C['risk_free_rate_data']), NA, f(C['risk_free_rate_data'])),
        (r'$\varphi$', 'Tax progressivity', 'Ext.', r'Heathcote et al.\ (2017)',
         f(C['curvature_of_labor_income_taxes']), NA, f(C['curvature_of_labor_income_taxes'])),
        # tau_l before tau_k (the author, round 375493a0)
        (r'$\tau_{\ell}$', 'Level of the labour income tax', setcol('tau_ell'), r'Average labour income tax, McDaniel (2007)',
         pc(C['average_labor_income_tax_data']), pc(mom('tau_l average labour income tax')),
         f(H['labor_income_tax_rate'], 3)),
        (r'$\tau_k$', 'Capital income tax', 'Ext.', 'US long-run rate on gains and dividends',
         f(C['investment_income_tax']), NA, f(C['investment_income_tax'])),
    ]),
    ("Social security benefits and programmes' rules", [
        (r'$S(y)$', 'Social security', 'Ext.', 'SSA primary insurance amount',
         'statute', NA,
         f'{C["ss_pia_rate_1"]:.2f}, {C["ss_pia_rate_2"]:.2f}, {C["ss_pia_rate_3"]:.2f}'),
        (r'$\underline S$', 'SSI floor over entry productivity', 'Ext.', 'SSA federal benefit rate',
         f(H['ssi_floor_level'], 3), NA, f(H['ssi_floor_level'], 3)),
        (r'$\psi_{ui}$', 'UI replacement rate', 'Ext.', 'DOL statutory replacement rates',
         f(H['replacement_rate_ui']), NA, f(H['replacement_rate_ui'])),
        (r'$\bar y$', 'Cap on the UI earnings base', 'Ext.', 'DOL state benefit maxima',
         f(H['max_ui_as_perc_of_avg_inc']), NA, f(H['max_ui_as_perc_of_avg_inc'])),
        (r'$\kappa_V$', 'Voucher means test', 'Ext.', 'HUD rule',
         f(C['threshold_income_vouchers']), NA, f(C['threshold_income_vouchers'])),
        (r'$\kappa_r$', "Tenant's rent, share of income", 'Ext.', 'HUD rule',
         f(C['rent_to_income_ratio_vouchers']), NA, f(C['rent_to_income_ratio_vouchers'])),
        (r'$\varrho$', 'Food stamp clawback rate', 'Ext.', r'SNAP statute, 7 CFR 273.10',
         f(C['food_stamp_taper']), NA, f(C['food_stamp_taper'])),
    ]),
    ('Drug market', [
        (r'$J_E$', 'Maximum age at which use can begin', 'Ext.', 'Model age 55, that is age 80',
         f'{C["max_age_to_choose_addiction"]:.0f}', NA, f'{C["max_age_to_choose_addiction"]:.0f}'),
        (r'$\nu_1$', 'Supply shifter', 'Ext.', r'Normalisation, so $p_v=1$', 'norm.', NA, 'norm.'),
    ]),
]


def band5(key, nd=1):
    d = ', '.join(f'{100 * mom(f"{key}, band {i}", 1):.{nd}f}' for i in range(1, 6))
    m = ', '.join(f'{100 * mom(f"{key}, band {i}"):.{nd}f}' for i in range(1, 6))
    return d, m


def one(key, nd=1, scale=100):
    return f'{scale * mom(key, 1):.{nd}f}', f'{scale * mom(key):.{nd}f}'


def many(keys, nd=1, neg=False):
    wrap = (lambda s: f'${s}$') if neg else (lambda s: s)
    return (', '.join(wrap(f'{100 * mom(k, 1):.{nd}f}') for k in keys),
            ', '.join(wrap(f'{100 * mom(k):.{nd}f}') for k in keys))


USER_BANDS = ['users aged 34 or less, share', 'users aged 35-44, share', 'users aged 45-54, share',
              'users aged 55-64, share', 'users aged 65 plus, share']

# (moment, (data, model), source); per cent unless the label says otherwise.
UNTARGETED = [
    ('Homelessness', None, None),
    # SHARES IN THE BAND, NOT RATES WITHIN IT (the author, 1 October: "what i need for
    # SUD and homelessness by age is share of in the band, not share within the age
    # bracket"). The within-band rate row went: its data are PERSON rates at the PiT
    # one-night level and the model's are HOUSEHOLD rates at the level h_1 targets, so
    # the two were in different units by construction (DATA_APPENDIX section 9).
    (r'Share of homeless by age, 25--34 to 65+$^{a}$', band5('share of the homeless'), 'HUD PiT 2024'),
    ('Employed share of the homeless',
     (f'{100 * C["employed_share_of_homeless_data"]:.0f}', f'{100 * mom("emp_homeless employed share of homeless"):.1f}'),
     'HUD PiT 2023, TEDS-A 2022'),
    ('Income of the homeless, over average', one('income of the homeless'), r'Meyer et al.\ (2024)'),
    ('Who uses and who carries a SUD', None, None),
    ('Share of users by age, 26--34 to 65+', many(USER_BANDS, 0), 'NSDUH 2024'),
    ('Mean age of users, years', one('mean age of drug users', 1, 1), 'NSDUH 2024'),
    ('Unemployment given a SUD', one('kappa_ued unemployment given SUD'), 'NSDUH 2024'),
    # DRUG USE, NOT THE SUD RATE, with SMI over without (the author, 1 October: "we need to
    # show the drug use ratio with SMI over without (not show the SUD rate)"); the same
    # numbers as the Block 3 sentence, from smi_use_ratio.json (model measured 23 Sept).
    ('Drug use with SMI over without, ratio', (SMI_USE['c_smi_use_ratio_data'],
     f"{float(SMI_USE['c_smi_use_ratio_model']):.2f}"), 'NSDUH 2024'),
    ('Drug deaths as a share of deaths, 25--44', one('drug deaths, share of deaths'), 'CDC WONDER'),
    ('Treatment', None, None),
    ('Homeless at treatment admission', one('homeless at treatment admission'), 'TEDS-A 2022'),
    ('Psychiatric problem at SUD admission', one('SMI alongside SUD at admission'), 'TEDS-A 2022'),
    ('Working at all, homeless in treatment', one('working, homeless in treatment'), 'TEDS-A 2022'),
    ('Housing and vouchers', None, None),
    # the data side from the declaration (0.192, renters with positive income and rent,
    # 1 October), not from the benchmark log's observed=, which is the old 0.175
    (r'Renters paying over 30\% of income', (f'{100 * C["renter_burden_30_data"]:.1f}',
     f'{100 * mom("renters above 30 pct of income"):.1f}'), 'SCF 2022'),
    ('Rent over income, voucher holders', one('tenant contribution rate'), 'HUD PSH 2023'),
    ('Voucher holders living on wages', one('voucher holders, wages main'), 'HUD PSH 2023'),
    ('Distribution, shares of the total', None, None),
    (r'Income, bottom 1, 5, 10, 20\%',
     many([f'income share bottom {p} pct' for p in (1, 5, 10, 20)], 2), 'SCF 2022'),
    # THE BOTTOM HALF JOINS THE ROW (the author, 1 October: "add the 50% here instead of
    # its own row"); its data side is the FRB DFA's, the other four the SCF's
    (r'Net worth, bottom 1, 5, 10, 20, 50\%',
     tuple(a + ', ' + b for a, b in zip(
         many([f'wealth share bottom {p} pct' for p in (1, 5, 10, 20)], 2, neg=True),
         (f'{100 * mom("w_bot net worth share, bottom half", 1):.1f}',
          f'{100 * mom("w_bot net worth share, bottom half"):.1f}'))), 'SCF 2022, FRB DFA'),
    ('Drug price elasticities', None, None),
    ('Participation (extensive margin)', (f"${RES['x_el_part_lo']}$ to ${RES['x_el_part_hi']}$", f"${RES['x_el_part']}$"),
     r'Saffer and Chaloupka (1999), Grossman and Chaloupka (1998)'),
    ('Per user, all users (intensive margin)', (f"${RES['x_el_int_lo']}$ to ${RES['x_el_int_hi']}$", f"${RES['x_el_int']}$"),
     r'Grossman and Chaloupka (1998), Olmstead et al.\ (2015)'),
    ('Transmission, odds ratios', None, None),
    # BOTH STUDIES ON ONE LINE (the author, 1 October: "just add it to the above, combine
    # them in one line"): 1.44 is Mellentin's and 2.51 Yoon's
    ('Child of a SUD parent acquires a SUD',
     ('1.44, 2.51', f'{mom("delta_d child SUD odds ratio"):.2f}'),
     r'Mellentin et al.\ (2016), Yoon et al.\ (2013)'),
    ('Homeless adult had a homeless caretaker',
     ('1.8 to 2.4', f'{mom("delta_h child homeless odds ratio"):.2f}'), r'Bassuk et al.\ (1997)'),
]


# RED MARKS WHAT MOVED. calib_tables_prev.json holds every row of the three
# tables as the author last read them, keyed on the first cell; a cell that
# differs from it, a row it does not have and a block heading it does not have
# are wrapped in \textcolor{red}, never \new (see the note at the top of
# tab_eleven.tex). The baseline moves only with --freeze, once the author has
# read the tables, so red accumulates between rounds as the rest of Section 4
# onward does.
PREV_JSON = os.path.join(HERE, 'calib_tables_prev.json')
PREV = json.load(open(PREV_JSON)) if os.path.exists(PREV_JSON) else None


def norm(x):
    """A cell's content without its unit, so '31.2 percent' and '31.2' match."""
    x = re.sub(r'\s*(percent|\\%)', '', x).replace('$', '').strip()
    try:
        return f'{float(x):g}'
    except ValueError:
        return x


def red(x):
    return r'\textcolor{red}{%s}' % x


def marked(table, cells, cols=None):
    """cells, with each one that moved since the baseline in red. cols maps a
    new column to the baseline's (None for a column the baseline lacks)."""
    if PREV is None:
        return list(cells)
    old = PREV[table]['rows'].get(cells[0])
    cols = cols or list(range(len(cells)))
    out = []
    for i, c in enumerate(cells):
        j = cols[i]
        same = old is not None and j is not None and j < len(old) and norm(old[j]) == norm(c)
        out.append(c if same else red(c))
    return out


def head(table, text, ncol, label=''):
    h = text if PREV is None or text in PREV[table]['heads'] else red(text)
    return r'\multicolumn{%d}{@{}l}{\emph{%s%s}} \\' % (ncol, label, h)


# THE BLOCKS ARE NUMBERED, in the tables as in the text, one sequence across Tables 4 and 5
# (the author, 1 October: "block 1: (and do this for every block)"). The number is a label
# on the heading and not part of it, so the frozen baseline still matches the heading itself.
def rows(blocks, table, first=1):
    out = []
    for i, (hd, rs) in enumerate(blocks):
        if i:
            out.append(r'\addlinespace')
        out.append(head(table, hd, 7, 'Block %d: ' % (first + i)))
        for r in rs:
            out.append(' & '.join(marked(table, r)) + r' \\')
    return '\n'.join(out) + '\n'


def rows_untargeted():
    out = []
    for mo, dm, s in UNTARGETED:
        if dm is None:
            if out:
                out.append(r'\addlinespace')
            out.append(head('tab_untargeted', mo, 4))
            continue
        # the baseline table had no Model column: Moment, Data, Source
        out.append(' & '.join(marked('tab_untargeted', [mo, dm[0], dm[1], s])) + r' \\')
    return '\n'.join(out) + '\n'


def write_body(fname, body):
    p = os.path.join(TAB, fname)
    s = open(p).read()
    a = s.index(r'\midrule') + len(r'\midrule') + 1
    b = s.index(r'\bottomrule')
    open(p, 'w').write(s[:a] + body + s[b:])


def key(sym):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]', '_', sym.replace('\\', ' ').lower())).strip('_')


def numbers():
    """The prose's names: c_<symbol>_value, _data and _model for every row of
    Tables 5 and 6, per cent signs dropped, and the derived numbers the prose
    argues from."""
    nums = {}
    for blocks in (ELEVEN, STANDARD):
        for head, rs in blocks:
            for sym, desc, st, src, data, model, value in rs:
                for tag, v in (('value', value), ('data', data), ('model', model)):
                    if v != NA:
                        # a band is an en dash in the table and 'to' in the prose
                        nums[f'c_{key(sym)}_{tag}'] = v.replace('\\%', '').replace('--', ' to ')
    nums.update({
        'c_uplift_pc': f'{100 * (UPLIFT - 1):.0f}',
        'c_b_target_pc': f'{100 * C["participation_rate_data"]:.2f}',
        'c_sud_data_pc': f'{100 * C["sud_rate_data"] / UPLIFT:.2f}',
        'c_sud_target_pc': f'{100 * C["sud_rate_data"]:.2f}',
        'c_sud_model_pc': f'{100 * mom("lambda_d disorder rate"):.2f}',
        'c_b_off_pc': f'{100 * B_OFF:.2f}',
        'c_b_fall_pc': f'{100 * (1 - B_ON / B_OFF):.1f}',
        'c_kx_implied': f'{KX_IMPLIED:.2f}',
        'c_theta_mor_pc': f'{100 * mom("theta drug spending share"):.0f}',
        # theta's aggregate among users WITHOUT a SUD, the second figure of the same DIAG
        # line whose first (users with a SUD) is the gaps table's and the Model cell's
        'c_theta_model_nosud': f'{100 * THETA_NOSUD:.1f}',
        'c_kappa_x_cons': f'{100 * KX_WTP:.2f}',
        'c_sd_entry': f'{SD_ENTRY:.2f}',
        'c_shelter_last_age': f'{25 + H["max_age_to_choose_homelessness"]:.0f}',
        'c_nodes': f'{C["employment_base_size"]:.0f}',
        'c_ssi_takeup': f'{H["ssi_floor_takeup"]:.0f}',
        # the SSI floor over the benchmark's average labour income (audit, 29 September)
        'c_j_value': f'{J_MAX}', 'c_j_age': f'{AGE0 + J_MAX}',
        'c_j_r_value': f'{J_RET}', 'c_j_r_age': f'{AGE0 + J_RET}',
        'c_ssi_floor_earn': f'{H["ssi_floor_level"] / AVG_LAB:.3f}',
        'c_avg_lab': f'{AVG_LAB:.2f}',
        # the productivity grid's settings that no row carried (audit, 29 September)
        'c_sd_fixed': f'{H["sd_fixed_employment_newborn"]:.2f}',
        'c_sd_fixed_scaled': f'{H["kkk_sigma_scale"] * H["sd_fixed_employment_newborn"]:.2f}',
        'c_rho_fixed': f'{H["persistence_fixed_employment_newborn"]:.2f}',
        'c_kkk_lo': f'{H["kkk_s_deviation_bottom"]:.2f}',
        'c_kkk_hi': f'{H["kkk_s_deviation_top"]:.2f}',
        'c_bottom_prod': f'{H["bottom_productivity_level"]:.3f}',
        # the share of SUDs over within ten years at the baseline hazard (Section 2 quotes it)
        'c_bar_pi_r_ten_pc': f'{100 * (1 - (1 - H["probability_of_stopping_addiction"]) ** 10):.0f}',
    })
    # TABLE 6 IN THE PROSE (the author, 1 October: the validation text "should walk the
    # reader through it well"). Every figure the walk-through quotes, and every word in
    # it that says which way the model misses, comes from here, so it turns when the
    # numbers do.
    def p1(x):
        return f'{100 * x:.1f}'

    def where(m, lo, hi):
        return 'within' if lo <= m <= hi else ('below' if m < lo else 'above')
    band = lambda k, d=0: mom(f'share of the homeless, band {k}', d) if d else mom(f'share of the homeless, band {k}')
    age_m, age_d = mom('mean age of drug users'), mom('mean age of drug users', 1)
    odds_d, odds_h = mom('delta_d child SUD odds ratio'), mom('delta_h child homeless odds ratio')
    nums.update({
        'u_hl_3544_d': p1(band(2, 1)), 'u_hl_3544_m': p1(band(2)),
        'u_hl_55p_d': p1(band(4, 1) + band(5, 1)), 'u_hl_55p_m': p1(band(4) + band(5)),
        'u_emp_hl_d': f'{100 * C["employed_share_of_homeless_data"]:.0f}',
        'u_emp_hl_m': p1(mom('emp_homeless employed share of homeless')),
        'u_inc_hl_d': p1(mom('income of the homeless', 1)), 'u_inc_hl_m': p1(mom('income of the homeless')),
        'u_users_young_d': f'{100 * mom(USER_BANDS[0], 1):.0f}', 'u_users_young_m': f'{100 * mom(USER_BANDS[0]):.0f}',
        'u_age_d': f'{age_d:.1f}', 'u_age_m': f'{age_m:.1f}',
        'u_age_dir': 'older' if age_m > age_d else 'younger',
        'u_unemp_d': p1(mom('kappa_ued unemployment given SUD', 1)), 'u_unemp_m': p1(mom('kappa_ued unemployment given SUD')),
        'u_deaths_d': p1(mom('drug deaths, share of deaths', 1)), 'u_deaths_m': p1(mom('drug deaths, share of deaths')),
        'u_treat_hl_d': p1(mom('homeless at treatment admission', 1)), 'u_treat_hl_m': p1(mom('homeless at treatment admission')),
        'u_b30_d': f'{100 * C["renter_burden_30_data"]:.1f}', 'u_b30_m': p1(mom('renters above 30 pct of income')),
        'u_vrent_d': p1(mom('tenant contribution rate', 1)), 'u_vrent_m': p1(mom('tenant contribution rate')),
        'u_vwage_d': p1(mom('voucher holders, wages main', 1)), 'u_vwage_m': p1(mom('voucher holders, wages main')),
        'u_inc20_d': f'{100 * mom("income share bottom 20 pct", 1):.2f}', 'u_inc20_m': f'{100 * mom("income share bottom 20 pct"):.2f}',
        'u_nw20_d': f'{100 * mom("wealth share bottom 20 pct", 1):.2f}', 'u_nw20_m': f'{100 * mom("wealth share bottom 20 pct"):.2f}',
        'u_nw50_d': p1(mom('w_bot net worth share, bottom half', 1)), 'u_nw50_m': p1(mom('w_bot net worth share, bottom half')),
        'u_odds_sud_lo': '1.44', 'u_odds_sud_hi': '2.51', 'u_odds_sud_m': f'{odds_d:.2f}',
        'u_odds_sud_where': where(odds_d, 1.44, 2.51),
        'u_odds_hl_lo': '1.8', 'u_odds_hl_hi': '2.4', 'u_odds_hl_m': f'{odds_h:.2f}',
        'u_odds_hl_where': where(odds_h, 1.8, 2.4),
    })
    return nums


if __name__ == '__main__':
    if '--freeze' in sys.argv:
        # the author has read the tables: what they show now is the new baseline
        fr = {}
        for t, blocks in (('tab_eleven', ELEVEN), ('tab_standard', STANDARD)):
            fr[t] = {'rows': {r[0]: list(r) for hd, rs in blocks for r in rs},
                     'heads': [hd for hd, rs in blocks]}
        # the MODEL column is frozen too: without it every model cell stayed red after a
        # freeze (30 September, the author: "remove all red from the tables too")
        fr['tab_untargeted'] = {'rows': {mo: [mo, dm[0], dm[1], s] for mo, dm, s in UNTARGETED if dm},
                                'heads': [mo for mo, dm, s in UNTARGETED if dm is None]}
        json.dump(fr, open(PREV_JSON, 'w'), indent=1, sort_keys=True)
        PREV = fr
        print('froze the three tables into calib_tables_prev.json')
    write_body('tab_eleven.tex', rows(ELEVEN, 'tab_eleven'))
    write_body('tab_standard.tex', rows(STANDARD, 'tab_standard', 1 + len(ELEVEN)))
    write_body('tab_untargeted.tex', rows_untargeted())
    nums = numbers()
    json.dump(nums, open(OUT, 'w'), indent=1, sort_keys=True)
    print(f'wrote three table bodies and {OUT} ({len(nums)} numbers)')
    print('HELD:', sorted(HELD))
