#!/bin/bash
# THE HIDDEN LABOUR-TAX RISE REMOVED (26 September). long_run_counter_factual set
# increase_in_labour_income_tax to hard-coded "warm starts" (-2.599e-3 for the HF voucher
# rule, 1.449e-3 and -7.359e-4 otherwise) AFTER upload_vars read the benchmark's value (0).
# With the budget cleared by pi_V (tax_system_type 3) or not at all, the tax is never solved
# for, so the warm start was a permanent tax rise inside every counterfactual: the no-policy
# run collected +0.148 of labour tax, welfare -0.26%, 8% better off. Here the three
# assignments keep the uploaded value. Also the counterfactual moments rule 5e-4 -> 1e-4 so
# the parent-to-child penalty has converged at exit. Otherwise AS build_cf_tdm.sh:
# AT LEAST 70 SWEEPS A PASS, THEN 5e-5 (26 September). 5e-6 is below the distribution's
# floor: after one lifetime (life_span 60) the per-sweep change bounces between 1e-5 and
# 4e-4 with paired spikes and never settles, so every pass would hit the 200 cap (about an
# hour a TF pass). What removes the lag is sweeping a whole lifetime every pass, so a
# policy change has passed through every age before the budget is read.
# SEEDED START (the author, 26 September: "You can also use the old equilibrium
# distribution from the convergence"): use_old_distribution 0 -> 1 and its read
# (initialize_feasible_distribution) takes distribution_stationary{1,2}seed.dat, a
# finished run's counter_arm distribution copied in by the arm script; the
# benchmark's own files are not touched. Otherwise AS build_cf_tightdist_b3h.sh:
# THE BUDGET CLEARED TO 1e-3 (the author, 26 September: "You can do 0.001 too if it
# helps"), otherwise AS build_cf_tightdist_b4.sh PLUS: pi_V's step is HALVED whenever the budget gap
# changes sign, floor 0.05/8 (the author, 26 September: "Maybe you need to update
# piv more slowly closer to the end").
# AS build_cf_tightdist.sh BUT THE BUDGET CLEARED TO 2e-4 (the author, 26 September:
# "Why can't you clear the budget around 0.0002?"). pi_V gain left at 0.05.
# THE COUNTERFACTUAL BUILD WITH THE DISTRIBUTION SOLVED EACH PASS (26 September).
# cf_childdecomp_tight (budget rule 2e-3, diagnostic prints of the children's and
# adults' split) plus ONE numerical change: the counterfactual loop's distribution
# rule 6e-4 -> 5e-6, so the distribution is not a lagged state carried across
# passes (CALIBRATION_STATE.md, 26 September 02:30). PERMBAN=1 also sets
# voucher_exclusion_release to 0. Source untouched. All three builds.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
SRC=$CODE/housing_first_or_treatment_first_SR_v1.f90
OUT=$CODE/cf_fix${PERMBAN:+_permban}; mkdir -p "$OUT"
R=$(grep -n '^                stopping_rule_stationary_distribution=6\*10.d0\*\*(-4)$' "$SRC" | cut -d: -f1)
[ "$(echo "$R" | wc -w)" = 1 ] || { echo "REFUSING: the loop's distribution rule is not unique: $R"; exit 1; }
ln_of() { n=$(grep -n -F -x -- "$1" "$SRC" | cut -d: -f1); [ "$(echo "$n" | wc -w)" = 1 ] || { echo "REFUSING: anchor not unique: $1"; exit 1; }; echo $n; }
A=$(ln_of "        real(8) :: total_consumption_1,consumption_1,frac_spent_1,space_1")
B=$(ln_of "        own_childhood_1=0")
C=$(ln_of "            mass_at_age_1=0")
D=$(ln_of "                                    utility_at_age_1=utility_at_age_1+mass_1*child_flow_out")
E=$(ln_of "                own_childhood_1=own_childhood_1+&")
G=$(ln_of "        want_child_flow=.FALSE.")
H=$(ln_of "        adult_num_1=0")
I=$(ln_of "                                adult_den_1=adult_den_1+mass_1")
J=$(ln_of "        childhood_num=childhood_num+own_childhood_1")
K=$(ln_of "        real(8) :: previous_distance")
P=$(ln_of "                            probability_of_voucher_benchmark_used_1=max(min(probability_of_voucher_benchmark_used_1+&")
Q=$(ln_of "                                0.05*(net_govt_revenues(transition_length)-net_govt_revenue_constraint),1.d0),0.d0)")
[ $Q -eq $((P+1)) ] && [ $K -lt $P ] || { echo "REFUSING: pi_V update anchors out of place"; exit 1; }
SL=$(ln_of "                open(unit=12,file=\"distribution_stationary\"//trim(string_used)//trim(old_results)//\".dat\",action='read')")
UL=$(ln_of "        integer, parameter :: use_old_distribution=0")
WL=$(ln_of "        do while (distance_distribution>stopping_rule_stationary_distribution)")
T1=$(ln_of "                    increase_in_labour_income_tax=-7.3590906975202195E-004")
T2=$(ln_of "                    increase_in_labour_income_tax=1.4488423360367944E-003")
T3=$(ln_of "                increase_in_labour_income_tax=-2.59935794204448567E-003")
FM=$(ln_of "        real(8), parameter :: stopping_rule_frozen_moments=5*10.d0**(-4)")
[ $T1 -lt $T2 ] && [ $T2 -lt $T3 ] && [ $((T3-T1)) -lt 20 ] || { echo "REFUSING: tax warm-start lines out of place"; exit 1; }
[ $G -lt $H ] && [ $H -lt $I ] && [ $I -lt $J ] || { echo "REFUSING: adult anchors out of order"; exit 1; }
[ $A -lt $B ] && [ $B -lt $C ] && [ $C -lt $D ] && [ $D -lt $E ] && [ $E -lt $G ] || { echo "REFUSING: anchors out of order"; exit 1; }
sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    -e 's/real(8) :: stopping_rule_govt_budget=2.5\*10.d0\*\*(-2)/real(8) :: stopping_rule_govt_budget=1.0*10.d0**(-3)/' \
    -e "${R}s/6\*10.d0\*\*(-4)/5*10.d0**(-5)/" \
    -e "${T1}s/=-7.3590906975202195E-004/=increase_in_labour_income_tax/" \
    -e "${T2}s/=1.4488423360367944E-003/=increase_in_labour_income_tax/" \
    -e "${T3}s/=-2.59935794204448567E-003/=increase_in_labour_income_tax/" \
    -e "${FM}s/=5\*10.d0\*\*(-4)/=1*10.d0**(-4)/" \
    -e "${WL}s/do while (distance_distribution>stopping_rule_stationary_distribution)/do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))/" \
    -e "${UL}s/use_old_distribution=0/use_old_distribution=1/" \
    -e "${SL}s|trim(old_results)//\".dat\"|\"seed.dat\"|" \
    ${PERMBAN:+-e 's|real(8), parameter :: voucher_exclusion_release=1.d0/3.d0|real(8), parameter :: voucher_exclusion_release=0.d0|'} "$SRC" | \
awk -v K=$K -v P=$P -v Q=$Q -v A=$A -v B=$B -v C=$C -v D=$D -v E=$E -v G=$G -v H=$H -v I=$I -v J=$J '
NR==E {print "                dg_cmass=dg_cmass+(discount_factor**(age_index_1-1))*dg_mass/max(mass_at_age_1,10.d0**(-14))"
       print "                dg_cutil=dg_cutil+(discount_factor**(age_index_1-1))*dg_util/max(mass_at_age_1,10.d0**(-14))"
       print "                dg_ccons=dg_ccons+(discount_factor**(age_index_1-1))*dg_cons/max(mass_at_age_1,10.d0**(-14))"}
NR==G {print "        write(*,\x27(A,I3,5ES16.8)\x27) \" CHILDDECOMP mass type\",current_beta_type,dg_cmass"
       print "        write(*,\x27(A,I3,5ES16.8)\x27) \" CHILDDECOMP util type\",current_beta_type,dg_cutil"
       print "        write(*,\x27(A,I3,5ES16.8)\x27) \" CHILDDECOMP cons type\",current_beta_type,dg_ccons"}
NR==J {print "        write(*,\x27(A,I3,4ES16.8)\x27) \" ADULTDECOMP mass type\",current_beta_type,da_mass/max(sum(da_mass),10.d0**(-14))"
       print "        write(*,\x27(A,I3,4ES16.8)\x27) \" ADULTDECOMP vf type\",current_beta_type,da_vf/max(da_mass,10.d0**(-14))"}
NR==P {print "                            ! HALVE THE STEP WHEN THE GAP CHANGES SIGN, floor 0.05/8 (build copy only)."
       print "                            pv_gap_now_1=net_govt_revenues(transition_length)-net_govt_revenue_constraint"
       print "                            if ((pv_have_gap_1==1) .AND. (pv_gap_now_1*pv_last_gap_1<0.d0)) pv_gain_1=max(0.5d0*pv_gain_1,0.05d0/8.d0)"
       print "                            pv_last_gap_1=pv_gap_now_1"
       print "                            pv_have_gap_1=1"
       print "                            write(*,*) \"PV STEP: gap=\", pv_gap_now_1, \" gain=\", pv_gain_1"
       print "                            probability_of_voucher_benchmark_used_1=max(min(probability_of_voucher_benchmark_used_1+&"
       print "                                pv_gain_1*pv_gap_now_1,1.d0),0.d0)"
       next}
NR==Q {next}
{print}
NR==K {print "        real(8) :: pv_gain_1=0.05d0,pv_last_gap_1=0.d0,pv_gap_now_1"; print "        integer :: pv_have_gap_1=0"}
NR==H {print "        da_mass=0; da_vf=0"}
NR==I {print "                                da_g=((employment_index-1)/employment_base_size)*2+1"
       print "                                if (unemployment_index>threshold_addiction_index) da_g=da_g+1"
       print "                                da_mass(da_g)=da_mass(da_g)+mass_1"
       print "                                da_vf(da_g)=da_vf(da_g)+mass_1*value_function(years_left_on_mortgage_index)%vector_transition_real(time_period,1,financial_index,unemployment_index,employment_index,housing_status_index,voucher_index)"}
NR==A {print "        real(8) :: dg_mass(5),dg_util(5),dg_cons(5),dg_cmass(5),dg_cutil(5),dg_ccons(5)"; print "        integer :: dg_g"; print "        real(8) :: da_mass(4),da_vf(4)"; print "        integer :: da_g"}
NR==B {print "        dg_cmass=0; dg_cutil=0; dg_ccons=0"}
NR==C {print "            dg_mass=0; dg_util=0; dg_cons=0"}
NR==D {print "                                    if (housing_1==lowest_housing_grid_point) then"
       print "                                        dg_g=1"
       print "                                    elseif (frac_spent_1>0.d0) then"
       print "                                        dg_g=2"
       print "                                    elseif (voucher_index==1) then"
       print "                                        dg_g=3"
       print "                                    elseif ((include_voucher_exclusion==1) .AND. (voucher_index==voucher_excl)) then"
       print "                                        dg_g=4"
       print "                                    else"
       print "                                        dg_g=5"
       print "                                    end if"
       print "                                    dg_mass(dg_g)=dg_mass(dg_g)+mass_1"
       print "                                    dg_util(dg_g)=dg_util(dg_g)+mass_1*child_flow_out"
       print "                                    dg_cons(dg_g)=dg_cons(dg_g)+mass_1*consumption_1"}
' > "$OUT/cf.f90"
n=$(diff <(sed -e "\$a\\" "$SRC") "$OUT/cf.f90" | grep -c "^[<>]" || true)
want=65; [ -n "$PERMBAN" ] && want=67;
[ "$(grep -cE "^ +increase_in_labour_income_tax=increase_in_labour_income_tax$" "$OUT/cf.f90")" = 3 ] || { echo "REFUSING: tax warm starts not neutralised"; exit 1; }
grep -q -x "        real(8), parameter :: stopping_rule_frozen_moments=1\*10.d0\*\*(-4)" "$OUT/cf.f90" || { echo "REFUSING: moments rule not 1e-4"; exit 1; }
grep -q -x "        do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))" "$OUT/cf.f90" || { echo "REFUSING: minimum sweeps not set"; exit 1; }
grep -q -x "        integer, parameter :: use_old_distribution=1" "$OUT/cf.f90" || { echo "REFUSING: use_old_distribution not 1"; exit 1; }
[ "$(grep -c "distribution_stationary\"//trim(string_used)//\"seed.dat\"" "$OUT/cf.f90")" = 1 ] || { echo "REFUSING: seed read not set exactly once"; exit 1; }
 [ "$n" -eq "$want" ] || { echo "REFUSING: expected $want diff lines, got $n"; exit 1; }
[ "$(grep -c -x "                stopping_rule_stationary_distribution=5\*10.d0\*\*(-5)" "$OUT/cf.f90")" = 1 ] || { echo "REFUSING: the loop's rule is not 5e-5"; exit 1; }
[ "$(grep -c "stopping_rule_stationary_distribution=6\*10.d0\*\*(-4)" "$OUT/cf.f90")" = 1 ] || { echo "REFUSING: the benchmark loop's rule was touched"; exit 1; }
grep -q "real(8) :: stopping_rule_govt_budget=1.0\*10.d0\*\*(-3)" "$OUT/cf.f90" || { echo "REFUSING: budget rule not set"; exit 1; }
if [ -n "$PERMBAN" ]; then grep -q "real(8), parameter :: voucher_exclusion_release=0.d0" "$OUT/cf.f90" || { echo "REFUSING: release not zero"; exit 1; }; fi
[ -n "$GEN_ONLY" ] && { echo "generated $OUT/cf.f90 ($n diff lines against the source)"; exit 0; }
cd "$OUT"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_cf_snan 2> build_snan.err
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
