# TF 70 per cent, damped build: LOST at pass 7 to a container restart (26 September ~22:05)

Six complete passes on cf_fix2_damp (seeded from TF 85's distribution, pi_V 0.0801, price
0.8736, target 6.0370824603); the run died in pass 7 with the container. passes.txt:

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      2  0.8743  0.08010   -29.1%   -29.7%    +4.6%  3.48e-03  9.85e-03   789.9240  +1.71%
      3  0.8731  0.08128   -29.1%   -29.7%    +4.2%  3.09e-03  3.78e-03   789.9415  +1.76%
      4  0.8730  0.08105   -29.0%   -29.6%    +4.3%  2.92e-04  4.40e-03   789.9115  +1.67%
      5  0.8730  0.08079   -28.9%   -29.5%    +4.5%  2.93e-04  3.81e-03   789.8903  +1.60%
      6  0.8731  0.08056   -28.9%   -29.5%    +4.6%  2.28e-04  3.37e-03   789.8756  +1.56%

(budget gaps are deficits.) The damping removed the two-pass flip (b moved +9e-5, +5e-5, +1e-5
between passes 3 and 6, monotone), and the moments rule was met at pass 6 (5.8e-5); only the budget
was open. Not a result. Rerun moved to the worker session (session_01CNbZe1BHmxiBzKxWgBVugk) at
pi_V 0.0800, price 0.8733, because this machine now runs the T = 60 transition and cannot hold a
steady-state solve beside it.
