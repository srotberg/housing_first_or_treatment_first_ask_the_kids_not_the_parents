program dbg2
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    integer, parameter :: NHG=4001
    integer :: j,ia,iy,ie,id,iv,im,ihp,ireg,itr,iap,ielig,ig,k
    integer :: bhp,breg,btr,bap,nc,ec(NCAND)
    real(dp) :: cfloor,phi,w,base,vcap,cfl_net,cost_tr,acost,akcon
    real(dp) :: hours,res,dres,Rr,Rt,vv,cc,val,brute,bh,bb,A1,AK
    real(dp) :: hc(NCAND),rc(NCAND),warm(NBPMAX),vgap
    type(hpts_t) :: G
    logical :: found
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants(); call solve_household()
    cfloor = cfloor_share*avg_income
    akcon = (alpha_u/(alpha_u+gamma_u))**alpha_u*(gamma_u/((alpha_u+gamma_u)*p_v))**gamma_u
    found=.false.
    do j = 2, j_ret-1, 6
    call build_EV(j)
    do im=1,NM; do iv=1,NV; do id=1,ND; do iy=1,NY,2; do ia=1,NA,7
        if (found) cycle
        ie=1
        w = wage_rate(j,iy,id,im); cfl_net = cfloor - max(0.0_dp,r_free*a_grid(ia))
        brute=-1.0e13_dp
        do ihp=1,NH
            phi=survival(j,ihp,id,im)
            bb = b_of(id,im,ihp)
            if (ihp>1 .and. iv==2) then; vcap=p_rent*h_grid(ihp); else; vcap=0.0_dp; end if
            base=a_grid(ia)+bequest+r_free*a_grid(ia); if (ihp>1) base=base-p_rent*h_grid(ihp)
            do itr=0,1
                if (itr==1 .and. (id==1 .or. allow_treatment==0)) cycle
                cost_tr=0.0_dp; if (itr==1) cost_tr=treat_cost*avg_income
                do ireg=1,NREG
                    if (id==1 .and. j>j_exp .and. ireg>1) cycle
                    do iap=1,NA
                        acost=a_grid(iap)+cost_tr
                        do ig=1,NHG
                            hours=real(ig-1,dp)/real(NHG-1,dp)
                            call res_slope(hours,w,base,vcap,cfl_net,res,dres)
                            Rr=res-acost; if (Rr<=0.0_dp) cycle
                            if (hours*w+max(0.0_dp,r_free*a_grid(ia))<kappa_V*median_income) then
                                ielig=1; else; ielig=0; end if
                            Rt=Rr+p_v*bb
                            if (ireg==1) then; vv=0.0_dp
                            else; vv=max(gamma_u/(alpha_u+gamma_u)*Rt/p_v-bb,1.0e-8_dp); end if
                            cc=Rr-p_v*vv; if (cc<=0.0_dp) cycle
                            val=util(cc,h_pow(ihp),vv,bb,1.0_dp-hours)+ &
                                beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)
                            if (val>brute) then
                                brute=val; bh=hours; bhp=ihp; breg=ireg; btr=itr; bap=iap
                            end if
                        end do
                    end do
                end do
            end do
        end do
        vgap = brute - V(ia,iy,ie,id,iv,im,j)
        if (vgap > 1.0e-3_dp .and. .not.found) then
            found=.true.
            write(*,'(A,7I5)') ' bad state (j,ia,iy,ie,id,iv,im):',j,ia,iy,ie,id,iv,im
            write(*,'(A,ES13.5,A,ES13.5,A,ES11.3)') '  brute=',brute,'  V=',V(ia,iy,ie,id,iv,im,j),'  vgap=',vgap
            write(*,'(A,4I5,F10.5)') '  brute argmax (ihp,reg,tr,iap), hours:',bhp,breg,btr,bap,bh
            write(*,'(A,4I5,F10.5)') '  model policy (ihp,reg,tr,iap), hours:', &
                pol_h(ia,iy,ie,id,iv,im,j),pol_reg(ia,iy,ie,id,iv,im,j), &
                pol_tr(ia,iy,ie,id,iv,im,j),pol_a(ia,iy,ie,id,iv,im,j),pol_l(ia,iy,ie,id,iv,im,j)
            ! what does hours_candidates return at the BRUTE argmax combo?
            ihp=bhp; ireg=breg; itr=btr; iap=bap
            bb = b_of(id,im,ihp)
            if (ihp>1 .and. iv==2) then; vcap=p_rent*h_grid(ihp); else; vcap=0.0_dp; end if
            base=a_grid(ia)+bequest+r_free*a_grid(ia); if (ihp>1) base=base-p_rent*h_grid(ihp)
            cost_tr=0.0_dp; if (itr==1) cost_tr=treat_cost*avg_income
            acost=a_grid(iap)+cost_tr
            A1=h_pow(ihp)*bb**gamma_u; AK=akcon*h_pow(ihp)
            call build_hpoints(w,base,vcap,cfl_net, &
                 (kappa_V*median_income-max(0.0_dp,r_free*a_grid(ia)))/w, G)
            write(*,'(A,I3,A,F10.6)') '  n bp=',G%n,'   h_elig=',G%hE
            do k=1,G%n
                write(*,'(A,I2,A,5ES12.4)') '   bp',k,'  h,res,dL,dR,lp:',G%h(k),G%res(k),G%dL(k),G%dR(k),G%lp(k)
            end do
            warm=-1.0_dp
            call hours_candidates(G,A1,AK,bb,acost,ireg,warm,nc,hc,rc,ec)
            write(*,'(A,I3)') '  nc=',nc
            do k=1,nc
                write(*,'(A,I2,A,2ES13.5,I3)') '   cand',k,'  h,res,elig:',hc(k),rc(k),ec(k)
            end do
            write(*,'(A)') '  --- objective vs hours at the brute argmax ---'
            do ig=1,41
                hours=real(ig-1,dp)/40.0_dp
                call res_slope(hours,w,base,vcap,cfl_net,res,dres)
                Rr=res-acost
                if (Rr<=0.0_dp) then
                    write(*,'(F8.4,A)') hours,'   infeasible'; cycle
                end if
                if (hours*w+max(0.0_dp,r_free*a_grid(ia))<kappa_V*median_income) then
                    ielig=1; else; ielig=0; end if
                Rt=Rr+p_v*bb
                if (ireg==1) then; vv=0.0_dp
                else; vv=max(gamma_u/(alpha_u+gamma_u)*Rt/p_v-bb,1.0e-8_dp); end if
                cc=Rr-p_v*vv
                if (cc<=0.0_dp) then
                    write(*,'(F8.4,A)') hours,'   c<=0'; cycle
                end if
                phi=survival(j,ihp,id,im)
                val=util(cc,h_pow(ihp),vv,bb,1.0_dp-hours)+beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)
                write(*,'(F8.4,4ES14.6,I3)') hours,res,dres,cc,val,ielig
            end do
        end if
    end do; end do; end do; end do; end do
    end do
end program dbg2
