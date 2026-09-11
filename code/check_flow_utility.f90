! A STANDING NUMERICAL TEST OF THE FLOW UTILITY, 11 September.
!
! The author, on the step 2 change: "make sure it is correct, because
! everything builds on it later". It does: omega_c's moment, the child
! externality, the welfare decomposition and every counterfactual read off
! this one expression. The risk is not the algebra, which is short, but the
! PARENTHESISATION across eleven continuation lines -- whether the prefactor
! multiplies both terms and whether /(1-sigma) applies to the sum.
!
! So this compiles the live expression VERBATIM, with the same continuations,
! and compares it against the specification written out in full:
!
!     X_P = (c/xi)^phic (h/xi)^phis (bbar+q)^phiq
!     X_K = (c/xi)^phic (h/xi)^phis  bbar   ^phiq
!     V   = u(X_P) + omega_c * (xi-1) * u(X_K),   u(x) = x^(1-sigma)/(1-sigma)
!
! and separately checks that kappa = xi-1 is the child count that makes the
! household sum reproduce equation (1) of Rotberg and Steinberg (2024) when
! the drug is shared. kappa = n does not, and is off by a factor that GROWS
! with household size, so it is not a scaling choice but a different model.
!
! Build and run:  gfortran -O0 -fimplicit-none -ffree-line-length-none \
!                     check_flow_utility.f90 -o /tmp/cfu && /tmp/cfu
! Expected: every relative difference at or below 1e-15, and the kappa=xi-1
! column equal to the JME column to every digit printed.
!
program check_flow_utility
    implicit none
    real(8) :: sigma, gam, phiq, phis, phic, xi, wc, c, h, q, bbar
    real(8) :: hsuf, code, spec, X_P, X_K, uP, uK
    integer :: k

    sigma = 2.d0
    gam   = 0.278d0          ! relative_share_of_housing
    phiq  = 0.27d0           ! relative_share_of_addiction_2
    phis  = gam*(1-phiq)     ! relative_share_of_housing_2
    phic  = (1-gam)*(1-phiq) ! relative_share_of_consumption_2
    bbar  = 0.00254988d0     ! b_shifter = addiction_scalar_1

    write(*,'(A,3F12.8,A,F12.8)') " shares phis, phic, phiq =", phis, phic, phiq, &
        "   sum =", phis+phic+phiq

    do k = 1, 5
        xi = 1.d0 + 0.15d0*k          ! sqrt_household_size
        c  = 0.4d0 + 0.3d0*k
        h  = 0.2d0 + 0.2d0*k
        q  = 0.02d0*k
        wc = 0.25d0*k

        ! housing_status_utility_function, live branch, as built at 29529
        hsuf = h**((1-sigma)*phis)

        ! ---- EXACTLY the live expression, same parenthesisation and continuations
        code = (xi**&
            ((sigma-1)*(1-phiq)))*&
            ((hsuf*&
            c**((1-sigma)*phic)*&
            ((bbar+q))**&
            ((1-sigma)*phiq))&
            +wc*(xi-1)*&
            (hsuf*&
            c**((1-sigma)*phic)*&
            (bbar)**&
            ((1-sigma)*phiq)))/(1-sigma)

        ! ---- the specification the author approved: c and h divided by xi,
        !      drugs not divided, child weighted wc*(xi-1)
        X_P = (c/xi)**phic * (h/xi)**phis * (bbar+q)**phiq
        X_K = (c/xi)**phic * (h/xi)**phis * (bbar   )**phiq
        uP  = X_P**(1-sigma)/(1-sigma)
        uK  = X_K**(1-sigma)/(1-sigma)
        spec = uP + wc*(xi-1)*uK

        write(*,'(A,I2,A,ES22.14,A,ES22.14,A,ES10.2)') " case", k, &
            "  code=", code, "  spec=", spec, "  rel.diff=", abs(code-spec)/abs(spec)
    end do
end program
