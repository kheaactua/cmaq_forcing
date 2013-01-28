  
C***********************************************************************
C   Portions of Models-3/CMAQ software were developed or based on      *
C   information from various groups: Federal Government employees,     *
C   contractors working on a United States Government contract, and    *
C   non-Federal sources (including research institutions).  These      *
C   research institutions have given the Government permission to      *
C   use, prepare derivative works, and distribute copies of their      *
C   work in Models-3/CMAQ to the public and to permit others to do     *
C   so.  EPA therefore grants similar permissions for use of the       *
C   Models-3/CMAQ software, but users are requested to provide copies  *
C   of derivative works to the Government without restrictions as to   *
C   use by others.  Users are responsible for acquiring their own      *
C   copies of commercial software associated with Models-3/CMAQ and    *
C   for complying with vendor requirements.  Software copyrights by    *
C   the MCNC Environmental Modeling Center are used with their         *
C   permissions subject to the above restrictions.                     *
C***********************************************************************

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE TRIDIAG_BWD ( L, D, U, B, X )
C-----------------------------------------------------------------------

C  FUNCTION:
C    Solves tridiagonal system by Thomas algorithm.  Algorithm fails
C    ( M3ERR ) if first pivot is zero.  In that case, rewrite the
C    equation as a set of order KMAX-1, with X(2) trivially eliminated.
C The associated tri-diagonal system is stored in 3 arrays
C   D : diagonal
C   L : sub-diagonal
C   U : super-diagonal
C   B : right hand side function
C   X : return solution from tridiagonal solver

C     [ D(1) L(2) 0    0    0 ...       0     ]
C     [ U(1) D(2) L(3) 0    0 ...       .     ]
C     [ 0    U(2) D(3) L(4) 0 ...       .     ]
C     [ .       .     .     .           .     ] X(i) = B(i)
C     [ .             .     .     .     0     ]
C     [ .                   .     .    L(n)   ]
C     [ 0                         .    D(n)   ]

C   where n = NLAYS

C  PRECONDITIONS REQUIRED:
C    Dimensionality set up in terms of NLAYS from SUBST_VGRD_ID

C  SUBROUTINES AND FUNCTIONS CALLED:

C  REVISION HISTORY:
C    NO.   DATE         WHO                     WHAT
C    __    ____         ___                     ____
C    1   04/07/07   Sandu A. &        developed TAMC equivalent of tridiag 
C                   Kumaresh Singh    subroutine for adjoint calculations
C    2   Jul 2010 by Peter Percell at UH-IMAQS: corrected N_SPC_DIFF
C         
C-----------------------------------------------------------------------

      USE VGRD_DEFN           ! vertical layer specifications

      IMPLICIT NONE

C Includes:

!     INCLUDE SUBST_VGRD_ID   ! vertical dimensioning parameters
      INCLUDE SUBST_GC_DIFF   ! gas chem diffusion species and map table
      INCLUDE SUBST_AE_DIFF   ! aerosol diffusion species and map table
      INCLUDE SUBST_NR_DIFF   ! non-react diffusion species and map table
      INCLUDE SUBST_TR_DIFF   ! tracer diffusion species and map table

      INTEGER     N_SPC_DIFF               ! global diffusion species
      PARAMETER ( N_SPC_DIFF = N_GC_DIFF
     &                       + N_AE_DIFF
     &                       + N_NR_DIFF
     &                       + N_TR_DIFF)

C Arguments:

      REAL        L( NLAYS )              ! subdiagonal
      REAL        D( N_SPC_DIFF,NLAYS )   ! diagonal
      REAL        U( NLAYS )              ! superdiagonal
      REAL        B( N_SPC_DIFF,NLAYS )   ! R.H. side
      REAL        X( N_SPC_DIFF,NLAYS )   ! solution

C Local Variables:

      REAL        GAM( N_SPC_DIFF,NLAYS )
      REAL        BET( N_SPC_DIFF )
      INTEGER     V, K, K1

C Decomposition and forward substitution:

      do v = 1, n_spc_diff
        bet(v) = 1./d(v,1)
      end do
      do k = 2, nlays-1
        do v = 1, n_spc_diff
          gam(v,k) = bet(v)*u(k-1)
          bet(v) = 1./(d(v,k)-l(k)*gam(v,k))
        end do
      end do
      k = nlays
      do v = 1, n_spc_diff
        gam(v,k) = bet(v)*u(k-1)
      end do
      do k = 1, nlays-1
        do v = 1, n_spc_diff
          x(v,k+1) = x(v,k+1)-x(v,k)*gam(v,k+1)
        end do
      end do
      do k = nlays, 2, -1
        do v = 1, n_spc_diff
          bet(v) = 1./d(v,1)
        end do
        do k1 = 2, k-1
          do v = 1, n_spc_diff
            gam(v,k1) = bet(v)*u(k1-1)
            bet(v) = 1./(d(v,k1)-l(k1)*gam(v,k1))
          end do
        end do
        do v = 1, n_spc_diff
          gam(v,k) = bet(v)*u(k-1)
          bet(v) = 1./(d(v,k)-l(k)*gam(v,k))
          b(v,k) = b(v,k)+x(v,k)*bet(v)
          x(v,k-1) = x(v,k-1)-x(v,k)*bet(v)*l(k)
          x(v,k) = 0.
        end do
      end do
      do v = 1, n_spc_diff
        bet(v) = 1./d(v,1)
        b(v,1) = b(v,1)+x(v,1)*bet(v)
        x(v,1) = 0.
      end do

      RETURN
      END
