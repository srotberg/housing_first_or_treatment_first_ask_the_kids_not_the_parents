Traceback (most recent call last):
  File "/home/user/children_first_housing_later/code/revoked_2c/analyse.py", line 242, in <module>
    {'pair3': pair3, 'rest3': rest3, 'main': main}[sys.argv[1]](sys.argv[2:])
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/user/children_first_housing_later/code/revoked_2c/analyse.py", line 206, in main
    out.append(f"| {t} | {k} | {x['alive']:.6e} | {y['alive']:.6e} | {da:.6e} | {db:.6e} | {pct(da / m0)} | {pct(db / m0)} "
                                                                                                ~~~^~~~
ZeroDivisionError: float division by zero
