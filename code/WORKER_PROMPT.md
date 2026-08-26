You run points of a model calibration, as many as you can. Work autonomously; the author is asleep. Never ask questions, never wait for input. Do not edit any source file.

REPOSITORY: https://github.com/srotberg/housing_first_children_later, branch claude/two-period-addiction-hazard-d7gb61. If it is not already checked out in the home directory, clone it there.

YOU ARE WORKER __N__ OF 8. YOUR LINES ARE __LINES__ ... every 8th line of code/ROUND.txt starting at line __N__.

HOW LONG THIS TAKES, SO YOU DO NOT GIVE UP EARLY. Compiling the Fortran takes about ONE MINUTE (measured: 59 seconds on 4 cores) and only happens on the first point in a fresh container. Solving one point takes 25 to 40 minutes on 4 cores. So a point is due back within about 45 minutes of you launching it. A point still running at 20 or 30 minutes is NORMAL and is never a reason to stop, to conclude something is broken, or to end your turn. A point still running after 60 minutes is NOT normal: say so explicitly in your report, with the tail of its log, and move to your next line.

1. cd into the checkout, then:
     git checkout claude/two-period-addiction-hazard-d7gb61 || git checkout -b claude/two-period-addiction-hazard-d7gb61 origin/claude/two-period-addiction-hazard-d7gb61
     git pull --rebase origin claude/two-period-addiction-hazard-d7gb61

2. WORK THROUGH YOUR LINES IN ORDER, for as long as your turn lasts. For each line number L in __LINES__ ... up to the number of lines in code/ROUND.txt:

   a. Read it:  sed -n "${L}p" code/ROUND.txt
      If there is no such line, you are done: report and stop.

   b. RUN IT. Do NOT try to work out whether it was already measured. run_one_point.sh makes that decision itself and exactly, from the md5 of the full parameter vector: if the point is already in code/points/ it prints "is already measured, skipping" and exits within a second. NEVER skip a line on your own judgement.

      HOW TO LAUNCH IT -- THIS EXACT SHAPE MATTERS AND GETTING IT WRONG IS WHY
      THE FIRST TWO AUTOMATED ROUNDS MEASURED NOTHING AT ALL. Issue ONE Bash
      tool call with run_in_background set to true, whose command is the round
      line running in the FOREGROUND of that call:

        eval "$(sed -n "${L}p" code/ROUND.txt)" > /tmp/line_${L}.log 2>&1

      DO NOT write `nohup ... &` inside a tool call, and do not append `&`. A
      backgrounded child of a tool call is reaped the moment the launcher
      returns: the model binary is killed a second or two into its build, no
      point file is ever written, and you are left polling for a file that
      cannot appear. That is what happened to all eight workers on the first
      two rounds -- one quit after four minutes, seven hung for over an hour,
      and between them they produced nothing across two and a half hours.

      run_in_background keeps the command alive across turns and notifies you
      when it exits, which is exactly what a 25 to 40 minute solve needs. Wait
      for that notification. Do not poll it with a foreground sleep.

   c. When it ends, a file appears under code/points/ -- either point_<hash>.txt carrying the moments, or point_<hash>.FAILED.txt saying why it could not run. COMMIT AND PUSH EITHER ONE immediately, before starting your next line:
        git add code/points
        git commit -m "Round worker __N__, line ${L}"
        git pull --rebase origin claude/two-period-addiction-hazard-d7gb61 && git push origin HEAD:claude/two-period-addiction-hazard-d7gb61
      If the push is rejected, pull --rebase and retry, up to four times. A failure that leaves nothing in the repository looks exactly like a point still solving, which is why the FAILED file gets pushed too.

   d. Then go on to your next line. Do not stop after one point. Keep going until you run out of lines.

3. At the end, report how many points you ran, and for each the MOMENT lines with their targets and any DIAG lines. If you ran none, say so plainly and say why -- never report success for a turn that measured nothing.

NOTES
- A line "OMEGA SKIPPED" instead of a "MOMENT omega" line is CORRECT, not a failure.
- If one point fails, say what the error was, push its FAILED file, and CONTINUE with your next line. Do not stop the whole turn for one bad point. Do not edit anything to work around it.
- Do not run simplex.py. Do not change ROUND.txt. Another trigger coordinates the rounds.
- Another firing of you will start in an hour. That is fine: it will skip whatever is already measured.
