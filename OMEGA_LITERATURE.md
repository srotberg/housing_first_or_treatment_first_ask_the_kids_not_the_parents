# Where omega_c could come from

The author, 10 September: *"we can set omega_c to something but it needs to be
based on something real"*, and *"dig into the literature to see how we can get a
more reliable way to set omega_c based on other studies"*.

## What omega_c IS, so that a literature value is the same object

An earlier note in this session claimed a literature altruism weight is not
transplantable here, because omega_c multiplies a DEATH CONTINGENT child value.
THAT WAS WRONG and is withdrawn. The model's form is

    V_j = u_j + beta*[ phi_j * V_{j+1} + (1 - phi_j) * omega * X ]

which is the canonical dynastic overlapping generations form -- Barro-Becker
with mortality. So an altruism weight estimated in a heterogeneous agent OLG
model with bequests IS this parameter.

## The best candidate found

NISHIYAMA, "Measuring Time Preference and Parental Altruism", Congressional
Budget Office Technical Paper 2000-7, October 2000. A paper whose whole purpose
is estimating this parameter, in a heterogeneous agent OLG model with bequests,
both altruistic and accidental, calibrated to the US economy.

    annual time preference            0.934      (6.6 per cent discount rate)
    parental altruism, per child      0.509
    child households per parent       1.35
    total altruism toward children    0.686

The companion paper is Nishiyama (2002), "Bequests, Inter Vivos Transfers, and
Wealth Distribution", Review of Economic Dynamics 5(4), 892-931, which measures
time preference and altruism jointly against the capital output ratio and the
size of intergenerational transfers.

THIS MODEL'S discount_factor IS 0.934317, against Nishiyama's 0.934. The two
calibrations are in the same world, which is the case for treating his altruism
estimate as the same parameter.

## Which number

The model has ONE newborn replacing ONE dying household, so the single child is
the parent's whole next generation. Matching the TOTAL gives omega_c = 0.686;
matching the per child weight gives 0.509. Both are defensible and the range is

    omega_c = 0.51 to 0.69

## What that buys, against the measured ladder

    omega_c   externality (1-omega)   parental gap (interpolated)
    0.509           49 per cent            ~7 to 9 per cent
    0.686           31 per cent            ~12 to 15 per cent
    data                                    18.34 per cent

So a literature anchored value keeps a THIRD TO A HALF of the child cost
external AND brings the model within reach of the observed parental response.
That is the outcome the moment based calibration could not deliver: matching the
gap exactly needs omega_c near 1, which leaves no externality at all.

The gap figures are interpolated on a curve measured to be convex, so they are
upper bounds. A run at omega_c = 0.6 would pin them.

## NOT VERIFIED

The numbers above come from a web search extraction. The proxy in this container
blocks cbo.gov, govinfo.gov, ideas.repec.org, sites.google.com, Wiley and
qeconomics.org, so the paper could not be opened. The extraction is specific and
internally consistent, and its time preference matches this model's to three
decimals, but that is corroboration and not verification. NOBODY SHOULD PUT
0.509 OR 0.686 IN THE PAPER UNTIL THE PDF HAS BEEN READ.

## Two anchors considered and rejected

ALTONJI, HAYASHI AND KOTLIKOFF (1997, JPE) find that moving a dollar from a
recipient child to a donor parent raises transfers by less than 13 cents against
the dollar altruism implies. This is NOT an estimate of omega: under operative
altruism the predicted transfer derivative is -1 for ANY positive weight, since
total family resources are unchanged and the optimum leaves both consumptions
where they were. It is a rejection statistic for the model class. An earlier
note in this session suggested omega_c = 0.13 on the strength of it; that was a
category error and is withdrawn. Barczyk and Kredler (2021, JET) have since
argued the test was misspecified in any case.

THE MODEL'S OWN BEHAVIOURAL MOMENT gives omega_c near 1 -- the internal moment
reads 0.1729 at omega_c = 1 against a target of 0.18343, and the cross run
statistic 0.2004. It is real data and it is the model's own calibration, so
nobody could object to the source. What they would object to is that at
omega_c = 1 the externality share, 1 - omega, is ZERO, and the paper's central
mechanism has been calibrated out of existence.
