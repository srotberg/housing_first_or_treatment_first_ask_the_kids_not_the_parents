#!/usr/bin/env python3
"""Persist b_smi_multiple and its adjuster across a resume.

    patch_b_smi_persist.py <master .f90> <output .f90>

WITHOUT THIS THE CHANNEL CANNOT MOVE. calibration_state.dat is written
positionally and b_smi_multiple is not in it, so every resume would reset it to
its declared 1.0 and throw away the loops spent lowering it. That matters more
than usual right now: the containers are rebooting on roughly a ten minute
cadence, and a parameter that resets on every reboot never leaves its starting
value.

THE ADJUSTER GOES WITH IT, for the reason the file already gives for
rho_intergenerational -- "Its adjuster goes with it, or a resumed run rings
again from a full step" -- and for a sharper one here: the adjuster arrives
through PARAM_HANDOVER, which consumes itself as it is read, so on a resume it
would fall back to its declared 0 and the bracket would come back HELD while
looking like it was running.

AT THE TAIL, which is the file's own convention: "AT THE TAIL, for the reason
the comment above gives", so that an older state file short-reads gracefully
rather than mis-parsing every field after the insertion point.

THE SHORT READ IS THE SAFE DIRECTION, as for kappa_find_smi above it. A state
file written before this existed runs out here and leaves b_smi_multiple at its
declared 1.0, which is the channel OFF -- the value every such checkpoint was
actually solved under.
"""
import sys

WRITE_ANCHOR = """            write(71,'(F30.15)') kappa_find_smi

        close(71)
"""
WRITE_NEW = """            write(71,'(F30.15)') kappa_find_smi
            ! AND AT THE TAIL AGAIN. Without these two a resume resets the SMI
            ! channel to off and the loops spent moving it are gone; the
            ! adjuster goes with the level because it arrives through the
            ! handover, which is consumed on the first read.
            write(71,'(F30.15)') b_smi_multiple
            write(71,'(F30.15)') b_smi_multiple_adjuster

        close(71)
"""

READ_ANCHOR = """                    if (state_ios_1/=0) then
                        write(*,*) "calibration_state.dat predates kappa_find_smi;",&
                            " it starts at its declared", kappa_find_smi
                    else
                        kappa_find_smi=max(min(kappa_find_smi,100.d0),1.d0)
                    end if

                end if
"""
READ_NEW = READ_ANCHOR + """
                if (state_ios_1==0) then

                    read(72,'(F30.15)',iostat=state_ios_1) b_smi_multiple

                    ! SAFE DIRECTION AGAIN. A checkpoint written before the SMI
                    ! channel existed runs out here and leaves b_smi_multiple at
                    ! its declared 1.0, which is the channel OFF -- the value
                    ! every such checkpoint was solved under.
                    if (state_ios_1/=0) then
                        write(*,*) "calibration_state.dat predates b_smi_multiple;",&
                            " it starts at its declared", b_smi_multiple,&
                            " which is the SMI channel off"
                    else
                        b_smi_multiple=max(min(b_smi_multiple,10.d0),10.d0**(-6))

                        read(72,'(F30.15)',iostat=state_ios_1) b_smi_multiple_adjuster

                        if (state_ios_1/=0) then
                            write(*,*) "calibration_state.dat carries b_smi_multiple but",&
                                " not its adjuster; the bracket resumes HELD at",&
                                b_smi_multiple_adjuster
                        else
                            b_smi_multiple_adjuster=max(min(b_smi_multiple_adjuster,10.d0),0.d0)
                        end if

                    end if

                end if
"""

src = open(sys.argv[1]).read()
for anchor, new in ((WRITE_ANCHOR, WRITE_NEW), (READ_ANCHOR, READ_NEW)):
    n = src.count(anchor)
    if n != 1:
        sys.exit("REFUSED: anchor appears %d times, expected 1:\n%r" % (n, anchor[:90]))
    src = src.replace(anchor, new, 1)
open(sys.argv[2], "w").write(src)
print("b_smi_multiple and its adjuster now persist across a resume")
