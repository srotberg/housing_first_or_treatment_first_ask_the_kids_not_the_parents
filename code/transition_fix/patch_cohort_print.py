"""patch_cohort_print.py SRC OUT -- THE ENTRANT VALUE BY THE PARENT'S AGE (11 October, the referee: the transition's
"cohort born at the reform" is eq. 31's adult term read at t+25, the average over ALL entrants that year, children of
other cohorts whose parent died that year included, and the cohort's own orphans are not followed; see
TRANSITION_LESSONS.md). Print-only. Per period of the forward pass, for each parent age j = 1..25, the mass of
parents of age j whose child enters next period (dying at j < 25, with the death hazard; all of them at j = 25) and
the sum over them of the child's expected value at entry, so that the cohort born at b can be assembled along its own
life: the children of its surviving parents enter at b+25, the orphans at the parent's death, each valued at the
age-one value function of the period it enters, placed as the distribution iteration places a newborn (productivity
drawn given the parent's node, SUD history and housing, the SMI draw, the endowment draw, employed, clean, no
voucher). Mass-weighted over every j the values reproduce the average entrant of the next period, the check.

Four anchored insertions, each anchor required to be unique; nothing else changes."""
import sys

src, out = sys.argv[1], sys.argv[2]
body = open(src).read()


def insert_after(anchor, text, body):
    n = body.count(anchor)
    assert n == 1, (n, anchor[:60])
    return body.replace(anchor, anchor + text, 1)


# 1. the module arrays, beside the accumulator they mirror
body = insert_after(
    "        real(8), dimension(employment_grid_size,0:1,1:2) :: newborn_parent_share_acc=0\n",
    "        ! COHORT PRINT (patch_cohort_print.py): the entering child's expected value by the parent's node, SUD\n"
    "        ! history and housing, and the mass and value of entrants by the parent's age, summed over the beta types\n"
    "        real(8), dimension(employment_grid_size,0:1,1:2) :: cohort_child_value=0\n"
    "        real(8), dimension(child_at_home_last_index) :: cohort_entrant_mass_by_age=0\n"
    "        real(8), dimension(child_at_home_last_index) :: cohort_entrant_value_by_age=0\n", body)

# 2. the routine's own scalars
body = insert_after(
    "        real(8) :: newborn_weight_1\n",
    "        integer :: cohort_d_1,cohort_h_1,cohort_parent_1,cohort_node_1,cohort_u_1\n"
    "        real(8) :: cohort_smi_1,cohort_v_1\n", body)

# 3. the reset at the first beta type, and the child's value at entry for this period, before the state loop
body = insert_after(
    "        if (accumulating_beta_types==0) newborn_parent_share_acc(:,:,:)=0\n",
    "        if (accumulating_beta_types==0) cohort_entrant_mass_by_age(:)=0\n"
    "        if (accumulating_beta_types==0) cohort_entrant_value_by_age(:)=0\n"
    "        ! COHORT PRINT: E V_{t+1}(1, s') of a child entering next period, by its parent's node, SUD history and\n"
    "        ! housing, placed as the distribution iteration places a newborn; zero while age one is unsolved\n"
    "        cohort_child_value=0\n"
    "        cohort_smi_1=0\n"
    "        if ((number_of_smi_states>1) .AND. (allocated(smi_prevalence_by_age))) cohort_smi_1=smi_prevalence_by_age(1)\n"
    "        if (value_function(1)%vector_transition_real(min(time_period+solve_transition_dynamics,transition_length),1,&\n"
    "            negative_financial_grid_size,1,1,0,0)>large_negative_num/2) then\n"
    "            do cohort_d_1=0,1\n"
    "                do cohort_h_1=1,2\n"
    "                    do cohort_parent_1=1,employment_grid_size\n"
    "                        do cohort_node_1=1,employment_grid_size\n"
    "                            cohort_v_1=0\n"
    "                            do cohort_u_1=0,1\n"
    "                                if ((cohort_u_1==1) .AND. (cohort_smi_1<=0.d0)) cycle\n"
    "                                cohort_v_1=cohort_v_1+((1-cohort_u_1)*(1-cohort_smi_1)+cohort_u_1*cohort_smi_1)*(&\n"
    "                                    include_exogenous_endowment*fraction_with_positive_wealth(cohort_node_1)*&\n"
    "                                    value_function(1)%vector_transition_real(&\n"
    "                                    min(time_period+solve_transition_dynamics,transition_length),1,&\n"
    "                                    initial_endowment(cohort_node_1),idx_of(1,cohort_u_1,0,0),cohort_node_1,0,0)+&\n"
    "                                    (1-include_exogenous_endowment*fraction_with_positive_wealth(cohort_node_1))*&\n"
    "                                    value_function(1)%vector_transition_real(&\n"
    "                                    min(time_period+solve_transition_dynamics,transition_length),1,&\n"
    "                                    negative_financial_grid_size,idx_of(1,cohort_u_1,0,0),cohort_node_1,0,0))\n"
    "                            end do\n"
    "                            cohort_child_value(cohort_parent_1,cohort_d_1,cohort_h_1)=&\n"
    "                                cohort_child_value(cohort_parent_1,cohort_d_1,cohort_h_1)+&\n"
    "                                newborn_employment_probability(cohort_node_1,cohort_parent_1,cohort_d_1,cohort_h_1)*cohort_v_1\n"
    "                        end do\n"
    "                    end do\n"
    "                end do\n"
    "            end do\n"
    "        end if\n", body)

# 4. the accumulation, at the site that builds the entrants' parent shares
body = insert_after(
    "                                    newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),is_homeless_1)=&\n"
    "                                        newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),is_homeless_1)+&\n"
    "                                        distribution_mass_used*newborn_weight_1\n",
    "                                    if ((age_index>=1) .AND. (age_index<=child_at_home_last_index)) then\n"
    "                                        cohort_entrant_mass_by_age(age_index)=cohort_entrant_mass_by_age(age_index)+&\n"
    "                                            distribution_mass_used*newborn_weight_1\n"
    "                                        cohort_entrant_value_by_age(age_index)=cohort_entrant_value_by_age(age_index)+&\n"
    "                                            distribution_mass_used*newborn_weight_1*&\n"
    "                                            cohort_child_value(employment_index,ever_sud_of(unemployment_index),is_homeless_1)\n"
    "                                    end if\n", body)

# 5. the print, beside the childhood-by-age line, after the last beta type
body = insert_after(
    '                write(*,*) "TRANSITION CHILDHOOD_BY_AGE t=", time_period, childhood_utility_by_age(time_period,:)\n',
    '                write(*,*) "TRANSITION ENTRANT_MASS_BY_PARENT_AGE t=", time_period, cohort_entrant_mass_by_age(:)\n'
    '                write(*,*) "TRANSITION ENTRANT_VALUE_BY_PARENT_AGE t=", time_period, cohort_entrant_value_by_age(:)\n', body)

open(out, 'w').write(body)
print(f'patched: {len(open(src).read().splitlines())} -> {len(body.splitlines())} lines')
