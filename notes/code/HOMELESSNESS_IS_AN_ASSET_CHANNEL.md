# WITHDRAWN. Homelessness in this model is a PREFERENCE, not an asset channel.

This file previously argued that homelessness here runs through an asset
channel: a bimodal age profile, homeless with above-average income, employment
at 95 per cent. Those numbers were right and the reading of them was wrong. They
are not a mechanism. They are the signature of a defect, and the author named it
on 2 September: *"we need to understand why so many of the homeless are
employed. This is strange especially now that we have poor people with no
wealth... That goes against everything you said about the wealth being the
cause."*

## The measurement

`model_fraction_homeless_by_choice` counts a homeless household whose income
PLUS assets exceed the rent on the smallest dwelling -- it could have been housed
and was not. Across every point measured on the cheapest rung, holding everything
else at the best point:

    h_2        h_1      by choice   could afford   income of    employed
                                    on income      homeless     share
    0.039      0.00012   0.995       0.995          0.297        0.305
    0.060      0.00083   0.999       0.999          0.494        0.886
    0.078      0.00383   1.000       1.000          0.648        0.959
    0.095      0.00297   0.955       0.954          0.817        0.954
    0.117      0.00059   0.980       0.955          1.107        0.758
    0.117 with
    sz=0.0578  0.00416   0.921       0.880          1.015        0.909
    DATA       0.00399     --          --           0.191        0.460

**Nowhere in the archive is anybody shut out.** Between 92 and 100 per cent of
the homeless could have rented and chose not to. The homelessness rate among the
UNEMPLOYED is 0.0014 to 0.0035 -- the genuinely poor are essentially never
homeless. The model's street is free and yields positive housing services, so
choosing it is a SAVING decision, and the households best placed to save are the
employed. That is the whole of the mechanism.

The Fortran itself predicted this, in a comment beside the diagnostic: *"If the
first number is close to one, homelessness in this model is a preference and not
a constraint."* It is close to one everywhere.

## The trade the model cannot escape

Read the table down the h_1 column and the income column together:

- at **h_2 = 0.039** the homeless look most like the data -- income 0.297 against
  0.191, employed 0.305 against 0.460 -- and there is almost NO homelessness,
  0.00012 against a 0.00399 target, 97 per cent short;
- at **h_2 = 0.117 with sz = 0.0578** the homelessness RATE is right, +4.3 per
  cent, and the homeless earn 1.015 times the average household.

**The model can produce the right AMOUNT of homelessness or the right KIND, and
not both.** No point in 581 has both. That is not a calibration gap; the
calibration is doing what it is told, and what it is told is reachable only in
one of the two directions at a time.

## What this bears on

The paper compares Housing First with Treatment First. A housing voucher given
to a population that is voluntarily homeless, employed, and earning average
income does something quite different from a voucher given to people who cannot
afford rent. The counterfactual rests on which of those the model contains.

Nothing has been changed. The street's free positive housing services are the
proximate cause and altering that is a model change, which is the author's call.
