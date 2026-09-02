# Wealth of drug users and those with SUD: no survey has it, so it is imputed

Asked directly whether we have data on the average wealth of drug users. We do
not, and no single file can give it:

    NSDUH_2024.dta   17 columns. SUD flags, income brackets, days of use.
                     NO wealth, asset, saving or debt variable of any kind.
    SCF_2022.dta     357 columns. Net worth in full detail.
                     NO drug, substance, alcohol or addiction variable.

So it has to be a TWO-SAMPLE imputation through the one thing both carry,
income: take the income-bracket distribution of SUD households from NSDUH, and
E[wealth | income bracket] from the SCF.

## The number

Working age 26-64 to match the NSDUH adult frame, hard-drug use disorder
(cocaine, heroin, hallucinogens, inhalants, methamphetamine -- marijuana
excluded, it is 90 per cent of any "all substances" measure):

    imputed median-based wealth, all adults      $210,240
    imputed median-based wealth, hard-drug SUD    $95,470
    RATIO                                          0.454

**USE THE MEDIAN-BASED FIGURE.** The mean-based one gives 0.620 and should not
be used: SCF mean net worth in the lowest income bracket is $743,386 even after
retirees are dropped, because that bracket holds business owners with current
losses and households with large assets and little income. SUD households are
four times over-represented in exactly that bracket -- 19.6 per cent of them
against 4.8 per cent of all adults -- so the means import a wealthy tail that
has nothing to do with drug users.

The bracket profile, working age, median net worth:

    <$10k      $13,800        $40-50k     $42,580
    $10-20k     $8,850        $50-75k     $81,073
    $20-30k    $12,964        $75k+      $398,345
    $30-40k    $20,801

## 0.454 IS AN UPPER BOUND, and the reasons all point the same way

1. **The imputation assumes SUD affects wealth ONLY through income.** Conditional
   on an income bracket, it gives a SUD household the same wealth as a non-SUD
   household. That is almost certainly false in the direction that matters --
   spending on the drug, job instability, medical costs and legal costs all
   reduce wealth at a given income -- so the true ratio is lower than 0.454.
2. **NSDUH excludes the homeless**, who are the poorest SUD population and the
   one this paper is about.
3. **The brackets are coarse**: seven categories, the top one open-ended and
   holding 47 per cent of the population.

## Why it is worth having anyway

The model already targets `y_u`, the INCOME of drug users relative to average,
at 0.74. There is no wealth analogue, and the AE's central complaint is that the
paper "does not match up to non-targeted moments". A wealth ratio for SUD
households is a non-targeted moment the model can be scored against without
being calibrated to it -- which is exactly the kind the AE asked for. Report it
as an upper bound with the assumption stated, not as a measurement.
