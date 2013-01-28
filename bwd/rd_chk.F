
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
      SUBROUTINE RD_CHK ( CHKGRID, JDATE, JTIME )

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

!     REAL         CGRID( NCOLS,NROWS,NLAYS,* )
      REAL, POINTER :: CGRID( :,:,:,: )          
      REAL, POINTER :: CHKGRID( :,:,:,: )          
!     REAL      :: CGRID( :,:,:,: )
      INTEGER      JDATE        ! current model date, coded YYYYDDD
      INTEGER      JTIME        ! current model time, coded HHMMSS

C Local variables:

      REAL, ALLOCATABLE :: DBUFF ( :,:,: )
      INTEGER      ALLOCSTAT

      INTEGER      SPC, VAR     ! species loop counters

      CHARACTER( 16 ) :: PNAME = 'RD_CHK'
      CHARACTER( 96 ) :: XMSG = ' '

      INTEGER, SAVE :: STRTCOLCHK, ENDCOLCHK, STRTROWCHK, ENDROWCHK
      INTEGER      GXOFF, GYOFF               ! global origin offset from file

      INTEGER, SAVE :: LOGDEV       ! FORTRAN unit number for log file
      LOGICAL, SAVE :: FIRSTIME = .TRUE.

C-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN

         FIRSTIME = .FALSE.
         LOGDEV = INIT3 ()

c         CALL CGRID_MAP( NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT )

C open conc file for update

         CALL SUBHFILE ( CTM_CHK_1, GXOFF, GYOFF,
     &          STRTCOLCHK, ENDCOLCHK, STRTROWCHK, ENDROWCHK )

	 END IF

      ALLOCATE ( DBUFF( MY_NCOLS,MY_NROWS,NLAYS ), STAT = ALLOCSTAT )
      IF ( ALLOCSTAT .NE. 0 ) THEN
         XMSG = 'Failure allocating DBUFF'
         CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
         END IF
    
      DO SPC = 1, N_GC_CONC

         IF ( .NOT. XTRACT3( CTM_CHK_1, GC_CONC( SPC ), 1, NLAYS,
     &      STRTROWCHK, ENDROWCHK, STRTCOLCHK, ENDCOLCHK,
     &      JDATE, JTIME, DBUFF ) ) THEN
            XMSG = 'Could not read ' // GC_CONC( SPC ) // ' from '
     &            // CTM_CHK_1
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF

         CHKGRID( 1:MY_NCOLS,1:MY_NROWS,1:NLAYS,SPC ) = DBUFF

         END DO

         IF ( .NOT. XTRACT3( CTM_CHK_1, 'RHOJ', 1, NLAYS, 
     &      STRTROWCHK, ENDROWCHK, STRTCOLCHK, ENDCOLCHK,
     &      JDATE, JTIME, DBUFF ) ) THEN
            XMSG = 'Could not read RHOJ from '
     &            // CTM_CHK_1
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF

         CHKGRID( 1:MY_NCOLS,1:MY_NROWS,1:NLAYS,N_GC_SPCD ) = DBUFF

         IF ( .NOT. XTRACT3( CTM_CHK_1, 'CHEMSTEP', 1, NLAYS, 
     &      STRTROWCHK, ENDROWCHK, STRTCOLCHK, ENDCOLCHK,
     &      JDATE, JTIME, DBUFF ) ) THEN
            XMSG = 'Could not read CHEMSPET from '
     &            // CTM_CHK_1
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF
 
         CHKGRID( 1:MY_NCOLS,1:MY_NROWS,1:NLAYS,N_GC_SPCD+1 ) = DBUFF

      DEALLOCATE ( DBUFF )

      WRITE( LOGDEV, '( /5X, 3( A, :, 1X ), I8, ":", I6.6 )' )
     &      'Timestep written to', CTM_CHK_1,
     &      'for date and time', JDATE, JTIME

      RETURN 
      END
