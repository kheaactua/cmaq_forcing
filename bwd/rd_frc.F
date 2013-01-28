
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
C $Header: /home/amir/work/cmaq4_5/models/CCTM/src/driver/ctm/wr_conc.F,v 1.1.1.1 2006/03/15 20:43:50 sjr Exp $

C what(1) key, module and SID; SCCS file; date and time of last delta:
C %W% %P% %G% %U%

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE RD_FRC ( CGRID, JDATE, JTIME )

C Revision History:
C   10/13/99 David Wong at LM
C      -- Called from driver, where CGRID is a pointer (subset) of PCGRID.
C         Necessary, to keep from referencing parts of PCGRID that don't
C         belong to CGRID.
C    1/31/2000 Jeff Young
C      -- f90 memory mgmt
C   Jeff - Dec 00 - move CGRID_MAP into f90 module
C   Jeff - Feb 01 - assumed shape arrays 
C   30 Mar 01 J.Young: dyn alloc - Use HGRD_DEFN; DBUFF for WRITE3
C   31 Jan 05 J.Young: dyn alloc - establish both horizontal & vertical
C                      domain specifications in one module
C-----------------------------------------------------------------------

      USE GRID_CONF             ! horizontal & vertical domain specifications
      USE CGRID_SPCS            ! CGRID species number and offsets

      IMPLICIT NONE

C Include Files:

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
C     REAL      :: CGRID( :,:,:,: )
      INTEGER      JDATE        ! current model date, coded YYYYDDD
      INTEGER      JTIME        ! current model time, coded HHMMSS

C Local variables:

      INTEGER      ALLOCSTAT

      CHARACTER( 16 ) :: PNAME = 'RD_FRC'
      CHARACTER( 96 ) :: XMSG = ' '

      INTEGER, SAVE :: STRTCOLFRC, ENDCOLFRC, STRTROWFRC, ENDROWFRC
      INTEGER      GXOFF, GYOFF               ! global origin offset from file

      INTEGER, SAVE :: LOGDEV       ! FORTRAN unit number for log file
      LOGICAL, SAVE :: FIRSTIME = .TRUE.

      REAL, SAVE, ALLOCATABLE :: HEC ( :,: ), POP( :,: ), DBUFF(:,:)
c      REAL, SAVE :: MAPTOT
      INTEGER I, J

C-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN

         FIRSTIME = .FALSE.
         LOGDEV = INIT3 ()

         CALL CGRID_MAP( NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT )

C open conc file for update

         CALL SUBHFILE ( CTM_FRC_1, GXOFF, GYOFF,
     &          STRTCOLFRC, ENDCOLFRC, STRTROWFRC, ENDROWFRC )

         IF ( .NOT. CLOSE3( CTM_FRC_1 ) ) THEN
            XMSG = 'Could not close ' // CTM_FRC_1
            CALL M3WARN( PNAME, JDATE, JTIME, XMSG )
            END IF

         IF ( .NOT. OPEN3( CTM_FRC_1, FSREAD3, PNAME ) ) THEN
            XMSG = 'Could not open ' // CTM_FRC_1
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF

c         IF ( .NOT. OPEN3( 'mort.nc       ', FSREAD3, PNAME ) ) THEN
c            XMSG = 'Could not open cost map file'
c            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c            END IF

c   for 24-hr ozone mortality
c         IF ( .NOT. OPEN3( 'POP_BMR.nc', FSREAD3, PNAME ) ) THEN
c            XMSG = 'Could not open pop file for domain'
c            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c            END IF

c         ALLOCATE ( HEC( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
c         IF ( ALLOCSTAT .NE. 0 ) THEN
c            XMSG = 'Failure allocating BMR'
c            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c            END IF

c         ALLOCATE ( POP( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
c         IF ( ALLOCSTAT .NE. 0 ) THEN
c            XMSG = 'Failure allocating POP'
c            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c            END IF

c         IF ( .NOT. XTRACT3( 'mort.nc', 'POP', 1, 1,
c     &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
c     &        0, 0, POP ) ) THEN
c              XMSG = 'Could not read cost map'
c              CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c              END IF

c         IF ( .NOT. XTRACT3( 'mort.nc', 'HE1', 1, 1,
c     &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
c     &        0, 0, HEC ) ) THEN
c              XMSG = 'Could not read population'
c              CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c              END IF

c         IF ( .NOT. XTRACT3( 'POP_BMR.nc', 'POP', 1, 1,
c     &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
c     &        0, 0, POP ) ) THEN
c              XMSG = 'Could not read POP'
c              CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c              END IF

c         IF ( .NOT. XTRACT3( 'POP_BMR.nc', 'BMR', 1, 1,
c     &        STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
c     &        0, 0, HEC ) ) THEN
c              XMSG = 'Could not read BMR'
c              CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c              END IF

	  END IF	    
	  
      ALLOCATE ( DBUFF( MY_NCOLS,MY_NROWS ), STAT = ALLOCSTAT )
      IF ( ALLOCSTAT .NE. 0 ) THEN
          XMSG = 'Failure allocating POP'
          CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
          END IF

      IF ( .NOT. XTRACT3( CTM_FRC_1, 'FORCE', 1, 1,
     &     STRTROWFRC, ENDROWFRC, STRTCOLFRC, ENDCOLFRC,
     &     JDATE, 10000*(JTIME/10000), DBUFF ) ) THEN
           XMSG = 'Could not read forcing'
           CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
           END IF

      DO I = 1, MY_NCOLS
      DO J = 1, MY_NROWS
      
c  For probability-weighted 4-th highest ozone
c  Cost function = summation of Pi*Ci divided by P for each location
c  with a prob-wtd conc > 65 ppb, averaged over U.S.
c  and Canada together
c  Forcing term has already been multiplied by 1000 to get units of ppb per
c  reduction in emissions
c  Forcing term is for 8-hr ozone (already considers the factor of 1/8)
c  but needs to be divided by 5 for the internal timestep
c  Threshold for locations above 65 ppb


c  For 8-hr ozone:
c  For exposure 5-month simulation, forcings have been multiplied by 1000 already
        CGRID(I,J,1,4)=CGRID(I,J,1,4)
     &   + DBUFF(I,J)/5.


c  For ozone !!! multiply forcing by 1000 to get units of ppm-1
c
c  (0.000839*1000.) is CRF per ppm
c  (POP(I,J)/1000000.) is population in million
c  (HEC(I,J)/365.) is daily baseline mortality
c  SVL of is $5.5M in 2007 dollar
c  DBUFF is the fractional forcing for max hour over one sync timestep (=0.2)

c  !! for 24-hr ozone mortality
c        CGRID(I,J,1,4)=CGRID(I,J,1,4) 
c     &   + (1.0/120.)
c     &   * (0.00052*1000.) 
c     &   * (POP(I,J)/1000000.) 
c     &   * (HEC(I,J)/365.) 
    

c  For ozone
c
c  (0.000839*1000.) is CRF per ppm
c  (POP(I,J)/1000000.) is population in million
c  (HEC(I,J)/365.) is daily baseline mortality
c  SVL of is $5.5M in 2007 dollar
c  DBUFF is the fractional forcing for max hour over one sync timestep (=0.2)

c        CGRID(I,J,1,4)=CGRID(I,J,1,4) 
c     &   + DBUFF(I,J)
c     &   * (0.000839*1000.) 
c     &   * (POP(I,J)/1000000.) 
c     &   * (HEC(I,J)/365.) 
c     &   * 5.5


c  For NO2
c
c  (0.000748*1000.) is CRF per ppm
c  (POP(I,J)/1000000.) is population in million
c  (HEC(I,J)/365.) is daily baseline mortality
c  SVL of is $5.5M in 2007 dollar
c  NO2 is a daily average metric
c  division by 5. for each sync timestep

c      CGRID(I,J,1,1)=CGRID(I,J,1,1) 
c     &   + (0.000748*1000.) 
c     &   * (POP(I,J)/1000000.) 
c     &   * (HEC(I,J)/365.) 
c     &   * 5.5 
c     &   / (24.0 * 5.0)
         
       END DO
       END DO
     
      WRITE( LOGDEV, '( /5X, 3( A, :, 1X ), I8, ":", I6.6 )' )
     &      'forcing read from', CTM_FRC_1, 
     &      'for date and time', JDATE, JTIME

C      DEALLOCATE (POP)
C      DEALLOCATE (BMR)
      DEALLOCATE (DBUFF)
      RETURN 
      END
