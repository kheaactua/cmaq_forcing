
!***********************************************************************
!  Portions of Models-3/CMAQ software were developed or based on      *
!  information from various groups: Federal Government employees,     *
!  contractors working on a United States Government contract, and    *
!  non-Federal sources (including research institutions).  These      *
!  research institutions have given the Government permission to      *
!  use, prepare derivative works, and distribute copies of their      *
!  work in Models-3/CMAQ to the public and to permit others to do     *
!  so.  EPA therefore grants similar permissions for use of the       *
!  Models-3/CMAQ software, but users are requested to provide copies  *
!  of derivative works to the Government without restrictions as to   *
!  use by others.  Users are responsible for acquiring their own      *
!  copies of commercial software associated with Models-3/CMAQ and    *
!  for complying with vendor requirements.  Software copyrights by    *
!  the MCNC Environmental Modeling Center are used with their         *
!  permissions subject to the above restrictions.                     *
!***********************************************************************

!RCS file, release, date & time of last delta, author, state, [and locker]
!$Header: /home/amir/work/cmaq4_5/models/CCTM/src/driver/ctm/wr_conc.F,v 1.1.1.1 2006/03/15 20:43:50 sjr Exp &

!what(1) key, module and SID; SCCS file; date and time of last delta:
!%W% %P% %G% %U%

!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE RD_FRC ( CGRID, JDATE, JTIME )

!Revision History:
!  10/13/99 David Wong at LM
!     -- Called from driver, where CGRID is a pointer (subset) of PCGRID.
!        Necessary, to keep from referencing parts of PCGRID that don't
!        belong to CGRID.
!   1/31/2000 Jeff Young
!     -- f90 memory mgmt
!  Jeff - Dec 00 - move CGRID_MAP into f90 module
!  Jeff - Feb 01 - assumed shape arrays 
!  30 Mar 01 J.Young: dyn alloc - Use HGRD_DEFN; DBUFF for WRITE3
!  31 Jan 05 J.Young: dyn alloc - establish both horizontal & vertical
!                     domain specifications in one module
!-----------------------------------------------------------------------

      USE GRID_CONF             ! horizontal & vertical domain specifications
      USE CGRID_SPCS            ! CGRID species number and offsets

      IMPLICIT NONE

! Include Files:

!     INCLUDE SUBST_HGRD_ID     ! horizontal dimensioning parameters
!     INCLUDE SUBST_VGRD_ID     ! vertical dimensioning parameters
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
      INCLUDE SUBST_AE_SPC      ! aerosol species table
      INCLUDE SUBST_NR_SPC      ! non-reactive species table
      INCLUDE SUBST_TR_SPC      ! tracer species table
      INCLUDE SUBST_GC_CONC     ! gas chem conc file species and map table
      INCLUDE SUBST_AE_CONC     ! aerosol conc file species and map table
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
#include      SUBST_IODECL      # I/O definitions and declarations
      INCLUDE SUBST_FILES_ID    ! I/O definitions and declarations
      INCLUDE SUBST_RXCMMN      ! Mechanism reaction common block for NPHOTAB

!     REAL         CGRID( NCOLS,NROWS,NLAYS,* )
      REAL, POINTER :: CGRID( :,:,:,: )          
!    REAL      :: CGRID( :,:,:,: )
      INTEGER      JDATE        ! current model date, coded YYYYDDD
      INTEGER      JTIME        ! current model time, coded HHMMSS

! Local variables:

      INTEGER      ALLOCSTAT

      CHARACTER( 16 ) :: PNAME = 'RD_FRC'
      CHARACTER( 96 ) :: XMSG = ' '

      INTEGER, SAVE :: STRTCOLFRC, ENDCOLFRC, STRTROWFRC, ENDROWFRC
      INTEGER      GXOFF, GYOFF               ! global origin offset from file

      INTEGER, SAVE :: LOGDEV       ! FORTRAN unit number for log file
      LOGICAL, SAVE :: FIRSTIME = .TRUE.

      REAL, SAVE, ALLOCATABLE :: HEC ( :,: ), POP( :,: ), DBUFF(:,:)
!     REAL, SAVE :: MAPTOT
      INTEGER I, J

!-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN

         FIRSTIME = .FALSE.
         LOGDEV = INIT3 ()

         CALL CGRID_MAP( NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT )

! open conc file for update

         CALL SUBHFILE ( CTM_FRC_1, GXOFF, GYOFF, &
               STRTCOLFRC, ENDCOLFRC, STRTROWFRC, ENDROWFRC )

         IF ( .NOT. CLOSE3( CTM_FRC_1 ) ) THEN
            XMSG = 'Could not close ' // CTM_FRC_1
            CALL M3WARN( PNAME, JDATE, JTIME, XMSG )
            END IF

         IF ( .NOT. OPEN3( CTM_FRC_1, FSREAD3, PNAME ) ) THEN
            XMSG = 'Could not open ' // CTM_FRC_1
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF

!        IF ( .NOT. OPEN3( 'mort.nc       ', FSREAD3, PNAME ) ) THEN
!           XMSG = 'Could not open cost map file'
!           CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!           END IF

!  for 24-hr ozone mortality
!        IF ( .NOT. OPEN3( 'POP_BMR.nc', FSREAD3, PNAME ) ) THEN
!           XMSG = 'Could not open pop file for domain'
!           CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!           END IF

!        ALLOCATE ( HEC( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
!        IF ( ALLOCSTAT .NE. 0 ) THEN
!           XMSG = 'Failure allocating BMR'
!           CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!           END IF

!        ALLOCATE ( POP( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
!        IF ( ALLOCSTAT .NE. 0 ) THEN
!           XMSG = 'Failure allocating POP'
!           CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!           END IF

!        IF ( .NOT. XTRACT3( 'mort.nc', 'POP', 1, 1,
!    &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
!    &        0, 0, POP ) ) THEN
!             XMSG = 'Could not read cost map'
!             CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!             END IF

!        IF ( .NOT. XTRACT3( 'mort.nc', 'HE1', 1, 1,
!    &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
!    &        0, 0, HEC ) ) THEN
!             XMSG = 'Could not read population'
!             CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!             END IF

!        IF ( .NOT. XTRACT3( 'POP_BMR.nc', 'POP', 1, 1,
!    &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
!    &        0, 0, POP ) ) THEN
!             XMSG = 'Could not read POP'
!             CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!             END IF

!        IF ( .NOT. XTRACT3( 'POP_BMR.nc', 'BMR', 1, 1,
!    &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
!    &        0, 0, HEC ) ) THEN
!             XMSG = 'Could not read BMR'
!             CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
!             END IF

	  END IF	    
	  
      ALLOCATE ( DBUFF( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
      IF ( ALLOCSTAT .NE. 0 ) THEN
          XMSG = 'Failure allocating POP'
          CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
          END IF

      IF ( .NOT. XTRACT3( CTM_FRC_1, 'FORCE', 1, 1,     &
          STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC, &
          JDATE, 10000*(JTIME/10000), DBUFF ) ) THEN
           XMSG = 'Could not read forcing'
           CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
           END IF

      DO I = 1, MY_NCOLS
      DO J = 1, MY_NROWS
      
! For probability-weighted 4-th highest ozone
! Cost function = summation of Pi*Ci divided by P for each location
! with a prob-wtd conc > 65 ppb, averaged over U.S.
! and Canada together
! Forcing term has already been multiplied by 1000 to get units of ppb per
! reduction in emissions
! Forcing term is for 8-hr ozone (already considers the factor of 1/8)
! but needs to be divided by 5 for the internal timestep
! Threshold for locations above 65 ppb


! For 8-hr ozone:
! For exposure 5-month simulation, forcings have been multiplied by 1000 already
        CGRID(I,J,1,4)=CGRID(I,J,1,4) &
        + DBUFF(I,J)/5.


! For ozone !!! multiply forcing by 1000 to get units of ppm-1
!c  (0.000839*1000.) is CRF per ppm
! (POP(I,J)/1000000.) is population in million
! (HEC(I,J)/365.) is daily baseline mortality
! SVL of is $5.5M in 2007 dollar
! DBUFF is the fractional forcing for max hour over one sync timestep (=0.2)

! !! for 24-hr ozone mortality
!       CGRID(I,J,1,4)=CGRID(I,J,1,4) 
!    &   + (1.0/120.)
!    &   * (0.00052*1000.) 
!    &   * (POP(I,J)/1000000.) 
!    &   * (HEC(I,J)/365.) 
    

! For ozone
!c  (0.000839*1000.) is CRF per ppm
! (POP(I,J)/1000000.) is population in million
! (HEC(I,J)/365.) is daily baseline mortality
! SVL of is $5.5M in 2007 dollar
! DBUFF is the fractional forcing for max hour over one sync timestep (=0.2)

!       CGRID(I,J,1,4)=CGRID(I,J,1,4) 
!    &   + DBUFF(I,J)
!    &   * (0.000839*1000.) 
!    &   * (POP(I,J)/1000000.) 
!    &   * (HEC(I,J)/365.) 
!    &   * 5.5


! For NO2
!c  (0.000748*1000.) is CRF per ppm
! (POP(I,J)/1000000.) is population in million
! (HEC(I,J)/365.) is daily baseline mortality
! SVL of is $5.5M in 2007 dollar
! NO2 is a daily average metric
! division by 5. for each sync timestep

!     CGRID(I,J,1,1)=CGRID(I,J,1,1) 
!    &   + (0.000748*1000.) 
!    &   * (POP(I,J)/1000000.) 
!    &   * (HEC(I,J)/365.) 
!    &   * 5.5 
!    &   / (24.0 * 5.0)
         
       END DO
       END DO
     
      WRITE( LOGDEV, '( /5X, 3( A, :, 1X ), I8, ":", I6.6 )' ) &
           'forcing read from', CTM_FRC_1,  &
           'for date and time', JDATE, JTIME

!     DEALLOCATE (POP)
!     DEALLOCATE (BMR)
      DEALLOCATE (DBUFF)
      RETURN 
ENDSUBROUTINE RD_FRC