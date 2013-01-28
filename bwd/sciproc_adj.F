
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

C RCS file, release, date & time of last delta, author, state, [and locker]
C $Header: /home/amir/work/cmaq4_5/models/CCTM/src/driver/yamo/sciproc.F,v 1.1.1.1 2006/03/15 20:43:50 sjr Exp $ 

C what(1) key, module and SID; SCCS file; date and time of last delta:
C %W% %P% %G% %U%

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE SCIPROC_ADJ (CGRID,CHKGRID,JDATE,JTIME,TSTEP,ASTEP)

C-----------------------------------------------------------------------
C Function:
C    Controls all of the physical and chemical processes for a grid
C    Operator splitting symmetric around chemistry
 
C Preconditions:
C    Dates and times represented YYYYDDD:HHMMSS.
C    No "skipped" dates and times.  All boundary input variables (layered or
C    non-layered) have the same perimeter structure with a thickness of NTHIK
 
C Subroutines and functions called:
C    All physical and chemical subroutines, 
C    DECOUPLE, COUPLE
 
C Revision History:
C    Oct. 24, 1995 by M. Talat Odman and Clint L. Ingram at NCSC: created
C    Jeff
C    13 Dec 97 - Jeff - uncouple diffusion processes
C    27 Jun 98 - Jeff - sync step = chem step
C     7 Jul 01 - Shawn - mv cloud processing before chem
C       Jan 02 - Jeff - dyn alloc; remove PCGRID argument to ping
C    23 Jun 03 J.Young: for layer dependent advection tstep
C    18 Aug 03 J. Pleim - move vdiff before advection
C    29 Aug 03 J.Young: eliminate symmetric processing option and unsed
C                       SUBST_GRID_ID string
C   30 May 05 J.Young: mass-conserving advection (yamo)
C-----------------------------------------------------------------------


      USE PCGRID_DEFN  ! inherits GRID_CONF and CGRID_SPCS
!     USE CGRID_SPCS   ! CGRID species number and offsets

      IMPLICIT NONE   

C Include files:

!     INCLUDE SUBST_HGRD_ID     ! horizontal dimensioning parameters
!     INCLUDE SUBST_VGRD_ID     ! vertical dimensioning parameters
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
!     INCLUDE SUBST_AE_SPC      ! aerosol species table
!     INCLUDE SUBST_NR_SPC      ! non-reactive species table
!     INCLUDE SUBST_TR_SPC      ! tracer species table
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_PACTL_ID    ! PA control parameters
      INCLUDE SUBST_FILES_ID    ! I/O files

C Arguments:
      REAL, POINTER :: CGRID( :,:,:,: )
      REAL, POINTER :: CHKGRID( :,:,:,: )

      INTEGER      JDATE        ! current model date, coded YYYYDDD
      INTEGER      JTIME        ! current model time, coded HHMMSS
      INTEGER      TSTEP( 2 )   ! time step vector (HHMMSS)
                                ! TSTEP(1) = local output step
                                ! TSTEP(2) = sciproc sync. step (chem)

!     INTEGER      ASTEP( NLAYS )  ! layer advection time step
      INTEGER      ASTEP( : )      ! layer advection time step

C Parameters:

C External Functions (not already declared by IODECL3.EXT):

      INTEGER, EXTERNAL :: SEC2TIME, TIME2SEC
      LOGICAL, EXTERNAL :: ENVYN

C Local Variables:

      CHARACTER( 16 ) :: PNAME = 'SCIPROC'

      LOGICAL, SAVE :: FIRSTIME = .TRUE.
      LOGICAL, SAVE :: XFIRST = .FALSE. !.TRUE.

      CHARACTER( 120 ) :: XMSG = ' '
      CHARACTER( 36 ) :: NMSG = 'After NEXTIME: returned JDATE, JTIME'

      INTEGER, SAVE :: LOGDEV

      INTEGER      SDATE        ! current science process date, coded YYYYDDD
      INTEGER      STIME        ! current science process time, coded HHMMSS
 
      INTEGER      ALLOCSTAT
      INTEGER      STATUS          ! ENV... status
      CHARACTER( 80 ) :: VARDESC   ! environment variable description
      CHARACTER( 80 ) :: MSG = ' '
      CHARACTER( 16 ) :: CTM_CKSUM = 'CTM_CKSUM'     ! env var for cksum on
!     LOGICAL, SAVE   :: CKSUM     ! flag for cksum on, default = [F]
      LOGICAL, SAVE   :: CKSUM     ! flag for cksum on, default = [T]
      
      real :: temp1, temp2, temp3

      INTERFACE
         SUBROUTINE XADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
            INTEGER, INTENT( IN )     :: ASTEP( : )
         END SUBROUTINE XADV_ADJ
         SUBROUTINE YADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
            INTEGER, INTENT( IN )     :: ASTEP( : )
         END SUBROUTINE YADV_ADJ
         SUBROUTINE ZADV_ADJ ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE ZADV_ADJ
!        SUBROUTINE LOAD_RHOJ ( CGRID, JDATE, JTIME )
!           IMPLICIT NONE
!           REAL, POINTER             :: CGRID( :,:,:,: )
!           INTEGER, INTENT( IN )     :: JDATE, JTIME
!        END SUBROUTINE LOAD_RHOJ
         SUBROUTINE ADJADV ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE ADJADV
         SUBROUTINE COUPLE ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE COUPLE
         SUBROUTINE DECOUPLE ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE DECOUPLE
         SUBROUTINE HDIFF ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE HDIFF
         SUBROUTINE VDIFF_ADJ ( CGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE VDIFF_ADJ
         SUBROUTINE CHEM_ADJ ( CGRID, CHKGRID, JDATE, JTIME, TSTEP )
            IMPLICIT NONE
            REAL, POINTER             :: CGRID( :,:,:,: )
            REAL, POINTER             :: CHKGRID( :,:,:,: )
            INTEGER, INTENT( IN )     :: JDATE, JTIME
            INTEGER, INTENT( IN )     :: TSTEP( 2 )
         END SUBROUTINE CHEM_ADJ
      END INTERFACE

  
C-----------------------------------------------------------------------

C Physical Processes for any Grid

      IF ( FIRSTIME ) THEN
         FIRSTIME = .FALSE.
         LOGDEV = INIT3 ()
	 
         END IF

      SDATE = JDATE
      STIME = JTIME

      CALL NEXTIME ( JDATE, JTIME, -TSTEP( 2 ) )
      WRITE( LOGDEV,'(/ 5X, A, I8, I7.6)' ) NMSG, JDATE, JTIME

      CALL CHEM_ADJ ( CGRID, CHKGRID, JDATE, JTIME, TSTEP )

      CALL HDIFF ( CGRID, JDATE, JTIME, TSTEP )

      CALL DECOUPLE ( CGRID, SDATE, STIME, TSTEP )

      CGRID(:,:,:,N_GC_SPCD)=CHKGRID(:,:,:,N_GC_SPCD)

      CALL ZADV_ADJ ( CGRID, JDATE, JTIME, TSTEP )

      IF ( XFIRST ) THEN
         XFIRST = .FALSE.

         CALL XADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )

         CALL YADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )

         ELSE
         XFIRST = .TRUE.

         CALL YADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )

         CALL XADV_ADJ ( CGRID, JDATE, JTIME, TSTEP, ASTEP )

         END IF

      CALL COUPLE ( CGRID, JDATE, JTIME, TSTEP ) 

      CALL VDIFF_ADJ ( CGRID, JDATE, JTIME, TSTEP )

      RETURN
      END
