"""patch_ckpt.py IN OUT -- THE BACKWARD PASS CHECKPOINTED (20 October; the author, on container restarts: "you can just
start from the most recent paths, no?", and "yes" to the safeguards).

The forward pass already writes the price and pi_V paths every period (drug_price_path_seed_out.txt and
pi_v_path_seed_out.txt hold a mixed path while a loop is in flight), so a relaunch starts from the latest paths. What a
restart still loses is the loop's backward pass, 8 to 15 hours, which lives only in memory. This patch, on any T = 70
transition source (rule CA, announced, grace years):

  1. AFTER EACH BACKWARD PASS, writes VF_CHECKPOINT.bin in the run directory: the whole value-function path (both
     tenure types, every period) and the five paths it was solved under (drug price, pi_V, house price, rent, lump
     sum), with their sizes and a checksum, through a temporary file and a rename so a kill mid-write leaves no
     half file under the real name.
  2. AT THE BINARY'S FIRST LOOP (a fresh start or a relaunch), if VF_CHECKPOINT.bin is there and its sizes match, it
     restores the paths and the value functions and skips the backward pass: the forward pass re-solves each period's
     policies from the value-function path, which the source already relies on ("re-solving at t reproduces exactly
     the policies the backward pass computed"), so the loop the kill interrupted is redone from its forward pass. The
     seeds the launcher staged are overridden by the checkpoint's own paths, so value functions and prices agree.
     A checksum that does not match stops the binary with CHECKPOINT CORRUPT (the launcher then deletes the file).
  3. WHEN A LOOP'S FORWARD PASS ENDS ('TRANSITION PATHS SAVED'), deletes the checkpoint, so a later restart (during the
     next backward pass) starts that loop afresh from the saved paths, as before.

Prints TRANSITION CHECKPOINT ... restored= 0|1 at every loop, SAVED after each backward pass and CLEARED at each loop's
end. The warm-start asset search (warm_start_a_prime) is not saved: its window falls back to the full grid whenever the
optimum sits on its edge, so a cold start finds the same policies."""
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src).read()


def once(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)


once("        integer :: voucher_conditional_on_clean=0\n",
     "        integer :: voucher_conditional_on_clean=0\n"
     "        integer :: ckpt_used=0,ckpt_ios=0,ckpt_n(7)=0,ckpt_m(7)=0   ! patch_ckpt.py\n"
     "        real(8) :: ckpt_sum=0.d0,ckpt_sum_file=0.d0                  ! patch_ckpt.py\n"
     "        logical :: ckpt_exists=.FALSE.                               ! patch_ckpt.py\n")

bwd = "            do time_index=max(transition_length-1,1),1,-1\n"
assert s.count(bwd) == 1, s.count(bwd)
end = ("                end do\n                            \n            end do\n            \n"
       "            ! THE DISTRIBUTION AND STATISTICS PASSES ARE ONE LOOP.\n")
assert s.count(end) == 1, s.count(end)

sizes = ("                ckpt_m=(/size(value_function(1)%vector_transition_real),size(value_function(2)%vector_transition_real),&\n"
         "                    size(price_of_addictive_good_path),size(probability_of_voucher_path),size(housing_price),&\n"
         "                    size(rent),size(lump_sum_transfer)/)\n")
cksum = ("sum(value_function(1)%vector_transition_real)+sum(value_function(2)%vector_transition_real)+&\n"
         "                            sum(price_of_addictive_good_path)+sum(probability_of_voucher_path)+sum(housing_price)+&\n"
         "                            sum(rent)+sum(lump_sum_transfer)")
restore = ("            ! THE BACKWARD-PASS CHECKPOINT (patch_ckpt.py): at the binary's first loop, a checkpoint left by a\n"
           "            ! killed run restores the value-function path and the paths it was solved under, and the backward\n"
           "            ! pass is skipped\n"
           "            ckpt_used=0\n"
           + sizes +
           "            if (loop_count==0) then\n"
           "                inquire(file='VF_CHECKPOINT.bin',exist=ckpt_exists)\n"
           "                if (ckpt_exists) then\n"
           "                    open(unit=96,file='VF_CHECKPOINT.bin',access='stream',form='unformatted',status='old',&\n"
           "                        action='read',iostat=ckpt_ios)\n"
           "                    if (ckpt_ios==0) read(96,iostat=ckpt_ios) ckpt_n,ckpt_sum_file\n"
           "                    if ((ckpt_ios==0) .AND. all(ckpt_n==ckpt_m)) then\n"
           "                        read(96) value_function(1)%vector_transition_real\n"
           "                        read(96) value_function(2)%vector_transition_real\n"
           "                        read(96) price_of_addictive_good_path,probability_of_voucher_path,housing_price,rent,&\n"
           "                            lump_sum_transfer\n"
           "                        ckpt_sum=" + cksum + "\n"
           "                        if (abs(ckpt_sum-ckpt_sum_file)>1.d-9*max(1.d0,abs(ckpt_sum_file))) then\n"
           "                            write(*,*) 'CHECKPOINT CORRUPT: checksum', ckpt_sum, ' against', ckpt_sum_file\n"
           "                            stop 'CHECKPOINT CORRUPT'\n"
           "                        end if\n"
           "                        ckpt_used=1\n"
           "                    end if\n"
           "                    close(96)\n"
           "                end if\n"
           "            end if\n"
           "            write(*,*) 'TRANSITION CHECKPOINT loop=', loop_count, ' restored=', ckpt_used\n"
           "            if (ckpt_used==0) then\n")
once(bwd, restore + bwd)
save = ("                end do\n                            \n            end do\n"
        "            ! THE BACKWARD-PASS CHECKPOINT (patch_ckpt.py): saved through a temporary file and a rename\n"
        "            ckpt_sum=" + cksum + "\n"
        "            open(unit=96,file='VF_CHECKPOINT.tmp',access='stream',form='unformatted',status='replace',&\n"
        "                action='write',iostat=ckpt_ios)\n"
        "            if (ckpt_ios==0) write(96,iostat=ckpt_ios) ckpt_m,ckpt_sum\n"
        "            if (ckpt_ios==0) write(96,iostat=ckpt_ios) value_function(1)%vector_transition_real\n"
        "            if (ckpt_ios==0) write(96,iostat=ckpt_ios) value_function(2)%vector_transition_real\n"
        "            if (ckpt_ios==0) write(96,iostat=ckpt_ios) price_of_addictive_good_path,probability_of_voucher_path,&\n"
        "                housing_price,rent,lump_sum_transfer\n"
        "            if (ckpt_ios==0) then\n"
        "                close(96)\n"
        "                call rename('VF_CHECKPOINT.tmp','VF_CHECKPOINT.bin')\n"
        "                write(*,*) 'TRANSITION CHECKPOINT SAVED loop=', loop_count, ' elements=', sum(ckpt_m)\n"
        "            else\n"
        "                close(96,status='delete',iostat=ckpt_ios)\n"
        "                write(*,*) 'TRANSITION CHECKPOINT NOT SAVED loop=', loop_count, ' (could not write; the run goes on)'\n"
        "            end if\n"
        "            end if\n"
        "            \n            ! THE DISTRIBUTION AND STATISTICS PASSES ARE ONE LOOP.\n")
once(end, save)

saved = '            write(*,*) "TRANSITION PATHS SAVED after loop", loop_count, &\n'
once(saved, "            ! THE LOOP IS DONE: its checkpoint is no longer the work in progress (patch_ckpt.py)\n"
             "            open(unit=96,file='VF_CHECKPOINT.bin',status='old',iostat=ckpt_ios)\n"
             "            if (ckpt_ios==0) close(96,status='delete')\n"
             "            write(*,*) 'TRANSITION CHECKPOINT CLEARED loop=', loop_count\n" + saved)
open(out, 'w').write(s)
print(f'ckpt: the backward pass saved after each loop, restored at a relaunch, cleared at each loop end -> {out}')
