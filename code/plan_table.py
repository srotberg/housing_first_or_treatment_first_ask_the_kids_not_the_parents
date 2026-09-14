import re,sys
SRC=open('code/housing_first_or_treatment_first_SR_v1.f90',errors='ignore').read()
LOG=open(sys.argv[1],errors='ignore').read()
SEED=dict(l.split()[:2] for l in open(sys.argv[2]) if len(l.split())>=2)

FLAGS={'freeze_to_three_block':1,'calibrate_size_of_smallest_house_hhld_can_buy':1,
       'hold_theta':1,'freeze_relative_share_of_leisure':1,'first_block_only':0}
def ev(e):
    e=re.sub(r'\s*!.*$','',e).strip().rstrip('&').strip()
    e=re.sub(r'(?<=[\d.])[dD](?=[-+]?\d)','e',e); e=re.sub(r'(\d)\.e','\\1.0e',e)
    for k,v in FLAGS.items(): e=re.sub(r'\b%s\b'%k,str(v),e)
    try: return float(eval(e))
    except Exception: return None
L=SRC.split('\n'); adj={}
for i,ln in enumerate(L):
    m=re.match(r'\s*real\(8\)\s*::\s*(\w+)_adjuster\s*=\s*(.*)$',ln)
    if not m or m.group(1) in adj: continue
    e=re.sub(r'\s*!.*$','',m.group(2)); j=i
    while e.rstrip().endswith('&'):
        j+=1; e=e.rstrip().rstrip('&')+re.sub(r'\s*!.*$','',L[j])
    adj[m.group(1)]=ev(e)
adj['weight_on_child']=ev(re.search(r'weight_on_child_adjuster\s*=\s*([^!\n]+)',SRC).group(1))
adj['relative_share_of_addiction_1']=ev(re.search(r'relative_share_of_addiction_adj\s*=\s*([^!\n]+)',SRC).group(1))

val={}
for m in re.finditer(r'(?m)^\s*([a-zA-Z_]\w*)=\s*([-+]?[\d.]+(?:[eEdD][-+]?\d+)?)\s*$',LOG):
    if m.group(1).startswith(('distance_','gap_','model_','stopping_')): continue
    try: val[m.group(1)]=float(m.group(2).replace('D','E').replace('d','e'))
    except: pass
mom={}
for m in re.finditer(r'MOMENT\s+(\S+)\s+.*?model=\s*([-\d.eEdD+]+)\s+target=\s*([-\d.eEdD+]+)',LOG):
    try: mom[m.group(1)]=(float(m.group(2).replace('D','E')),float(m.group(3).replace('D','E')))
    except: pass

# (parameter, adjuster key, moment, stage, note)
PLAN=[
 ('value_of_life','value_of_life','aleph',1,'VSL=80, and ONLY that now'),
 ('addiction_scalar_1','addiction_scalar','b',1,'drug block, 0.5%/loop'),
 ('addiction_onset_base','onset_base','lambda_d',1,'drug block, 0.5%/loop'),
 ('probability_of_becoming_addicted','probability_of_becoming_addicted','lambda_d',1,'second instrument on lambda_d'),
 ('multiple_find_if_addicted','multiple_find','sud_homeless',1,'drug block, 0.5%/loop'),
 ('size_homelessness','size_homelessness','h_1',1,'h_1 free, untied from h_2'),
 ('separation_rate','separation_rate','pi_eu',1,''),
 ('utility_cost_of_treatment','utility_cost_of_treatment','tau_u',1,'take-up; you asked it move faster'),
 ('max_food_cost','max_food_cost','cbar',1,'-> 0.105 and PIN (this turn)'),
 ('relative_share_of_housing','relative_share_of_housing','gamma',1,''),
 ('discount_factor','discount_factor','beta',1,''),
 ('labor_income_tax_rate','labor_income_tax_rate','tau_l',1,'relatively external'),
 ('voucher_probability','voucher_probability','pi_V',1,'relatively external'),
 ('mu_homeless','mu_homeless','mu_H',1,''),
 ('smi_onset_level','smi_onset_level','p_m',1,''),
 ('penalty_child_addicted','penalty_child_addicted','delta_d',1,'uncapped grid scan'),
 ('kappa_phi_d_level','kappa_phi_d_level','kappa_ued',1,'YOU ASKED THIS PINNED AT 2 -- it is drifting'),
 ('relative_share_of_addiction_1','relative_share_of_addiction_1','theta',0,'PINNED 0.095 by you'),
 ('penalty_child_homeless','penalty_child_homeless','delta_h',0,'PINNED 0 by you'),
 ('weight_on_child','weight_on_child','omega_c',3,'PINNED 0; opens LAST, child use gap'),
 ('smallest_house_size','smallest_house_size','h_2',2,''),
 ('largest_house_size','largest_house_size','h_3',2,''),
 ('relative_share_of_leisure','relative_share_of_leisure','omega_l',2,''),
 ('multiple_of_probabilities_of_employment_if_addicted','employment_multiplier','y_u',2,'income of drug users'),
 ('fixed_cost_to_moving','fixed_cost_to_moving','burden50',2,'rent burden over half'),
 ('kappa_uem','kappa_uem','kappa_uem',2,'employment given SMI'),
 ('lambda_m','lambda_m','lambda_m',2,'SMI share of homeless'),
 ('sd_permanent_productivity','sd_permanent_productivity','sigma_y',2,''),
 ('kkk_sigma_scale','kkk_sigma_scale','sigma_y',2,''),
 ('newborn_endowment','newborn_endowment','w_bot',2,'net worth, bottom half'),
 ('inheritance_amount','inheritance_amount','w_bot',2,'net worth, bottom half'),
 ('money_cost_of_treatment','money_cost_of_treatment','tau_u',2,'second instrument on take-up'),
]
HEAD={1:'STAGE 1 -- LIVE NOW',0:'PINNED BY YOUR INSTRUCTION (adjuster or gate is zero)',
      2:'STAGE 2 -- OPENS LATER (held now)',3:'STAGE 3 -- OPENS LAST'}
for st in (1,0,2,3):
    sel=[r for r in PLAN if r[3]==st]
    print(f"\n{HEAD[st]}   ({len(sel)})")
    print(f"{'parameter':<40} {'value':>12} {'adj':>7} {'moment':<13} {'model':>11} {'target':>10} {'gap':>8}  note")
    print('-'*128)
    def k(r):
        mm=mom.get(r[2]); 
        return -abs((mm[0]-mm[1])/mm[1]) if mm and mm[1] else 1e9
    for p,a,mn,_,note in sorted(sel,key=k):
        v=adj.get(a)
        pv=val.get(p)
        src=''
        if pv is None and p in SEED:
            try: pv=float(SEED[p].replace('D','E')); src='*'
            except: pass
        mm=mom.get(mn)
        vs=f"{pv:12.6g}{src}" if pv is not None else f"{'--':>12} "
        av=f"{v:7.4g}" if v is not None else f"{'?':>7}"
        ms=f"{mm[0]:11.6g} {mm[1]:10.6g}" if mm else f"{'--':>11} {'--':>10}"
        gs=f"{(mm[0]-mm[1])/mm[1]*100:+7.1f}%" if mm and mm[1] else f"{'--':>8}"
        print(f"{p:<40} {vs}{av} {mn:<13} {ms} {gs}  {note}")
print("\n* = value read from the seed, the run log never prints it")
