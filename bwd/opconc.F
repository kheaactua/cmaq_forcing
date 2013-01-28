
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
C $Header: /home/amir/work/cmaq4_5/models/CCTM/src/init/init/opconc.F,v 1.1.1.1 2006/03/15 20:43:51 sjr Exp $ 

C what(1) key, module and SID; SCCS file; date and time of last delta:
C %W% %P% %G% %U%

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE OPCONC ( CGRID, JDATE, JTIME, ENDDATE, ENDTIME, TSTEP )

C-----------------------------------------------------------------------
C Function:
C   Create the IO/API netCDF header and open the output CONC file

C Revision history:
C   Jeff - Dec 00 - split out from initscen.F
C                 - move CGRID_MAP into f90 module
C   Jeff - Feb 01 - assumed shape arrays
C   30 Mar 01 J.Young: dyn alloc - Use HGRD_DEFN
C
C    3 Sep 01 David Wong
C     -- let PE 0 open CTM_CONC_1 as new and later on let the rest open
C        it for read and write
C     -- put an explicit barrier before opening a new netCDF file to avoid
C        NCOPEN error
C    7 May 03 J.Young: open and close conc file in processor 0; spin-wait to
C                      deal with nfs network latency for mpich cluster
C   28 Aug 03 J.Young: following Zion Wang at CERT, remove the spin-wait and
C                      simplify opening and closing CONC file (see initscen)
C   31 Jan 05 J.Young: dyn alloc - establish both horizontal & vertical
C                      domain specifications in one module
C-----------------------------------------------------------------------

      USE GRID_CONF             ! horizontal & vertical domain specifications
      USE CGRID_SPCS            ! CGRID species number and offsets

      USE SUBST_MODULES         ! stenex
!     USE SUBST_UTIL_MODULE     ! stenex

      IMPLICIT NONE

!     INCLUDE SUBST_HGRD_ID     ! horizontal dimensioning parameters
!     INCLUDE SUBST_VGRD_ID     ! vertical dimensioning parameters
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
      INCLUDE SUBST_AE_SPC      ! aerosol species table
      INCLUDE SUBST_NR_SPC      ! non-reactive species table
      INCLUDE SUBST_TR_SPC      ! tracer species table
      INCLUDE SUBST_GC_CONC     ! gas chem conc file species and map table
      INCLUDE SUBST_AE_CONC     ! aerosol conc file species and map table
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IOFDESC     ! file header data structure
#include      SUBST_IODECL      # I/O definitions and declarations
      INCLUDE SUBST_FILES_ID    ! file name parameters
      INCLUDE SUBST_GC_EMIS      ! gas chemistry species table
!     INCLUDE SUBST_COORD_ID    ! coord. and domain definitions (req IOPARMS)

C Arguments:

!     REAL      :: CGRID( :,:,:,: )  ! for initial CONC
      REAL, POINTER :: CGRID( :,:,:,: )  ! for initial CONC
      INTEGER      JDATE        ! starting date (YYYYDDD)
      INTEGER      JTIME        ! starting time (HHMMSS)

      INTEGER      ENDDATE        ! ending date (YYYYDDD)
      INTEGER      ENDTIME        ! ending time (HHMMSS)

      INTEGER      TSTEP        ! output timestep (HHMMSS)

C External Functions (not already declared by IODECL3.EXT):

      INTEGER, EXTERNAL :: TRIMLEN      !  string length, excl. trailing blanks

C Local Variables:

      REAL, ALLOCATABLE :: DBUFF( :,:,: )
      INTEGER      ALLOCSTAT

      CHARACTER( 16 ) :: PNAME = 'OPCONC'
      CHARACTER( 96 ) :: XMSG = ' '
 
      INTEGER      LOGDEV

      INTEGER      L, SPC, V    ! loop counters
      INTEGER      STRT, FINI   ! loop counters
      INTEGER      INDX
      
      INTEGER      IDATE, ITIME

c      INTEGER, SAVE :: STRTCOLGRD, ENDCOLGRD, STRTROWGRD, ENDROWGRD

C-----------------------------------------------------------------------

      LOGDEV = INIT3()

C Get CGRID offsets

      CALL CGRID_MAP( NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT )

C Set output file characteristics based on COORD.EXT and open it

      FTYPE3D = GRDDED3
      SDATE3D = JDATE
      STIME3D = JTIME
      TSTEP3D = TSTEP
!     CALL NEXTIME( SDATE3D, STIME3D, TSTEP3D )
      NVARS3D = N_GC_CONC + N_AE_CONC + N_NR_SPC + N_TR_SPC
      NCOLS3D = GL_NCOLS
      NROWS3D = GL_NROWS
      NLAYS3D = NLAYS
      NTHIK3D =     1
      GDTYP3D = GDTYP_GD
      P_ALP3D = P_ALP_GD
      P_BET3D = P_BET_GD 
      P_GAM3D = P_GAM_GD
      XORIG3D = XORIG_GD
      YORIG3D = YORIG_GD
      XCENT3D = XCENT_GD
      YCENT3D = YCENT_GD
      XCELL3D = XCELL_GD
      YCELL3D = YCELL_GD
      VGTYP3D = VGTYP_GD
      VGTOP3D = VGTOP_GD
!     VGTPUN3D = VGTPUN_GD ! currently, not defined
      DO L = 1, NLAYS3D + 1
         VGLVS3D( L ) = VGLVS_GD( L )
         END DO
!     GDNAM3D = GDNAME_GD
      GDNAM3D = GRID_NAME  ! from HGRD_DEFN

      FDESC3D( 1 ) = 'Concentration file output'
      FDESC3D( 2 ) = 'From CMAQ model dyn alloc version CTM'
      DO SPC = 3, MXDESC3
         FDESC3D( SPC ) = ' '
         END DO

      V = 0
      STRT = 1
      FINI = N_GC_CONC
      DO SPC = STRT, FINI
         V = V + 1
         INDX = GC_CONC_MAP( V )
         VTYPE3D( SPC ) = M3REAL
         VNAME3D( SPC ) = GC_SPC( INDX )
         UNITS3D( SPC ) = 'ppmV'
         VDESC3D( SPC ) = 'Variable ' // VNAME3D( SPC )
         END DO

C create header

      IF ( MYPE .EQ. 0 ) THEN   ! open new
	 IF ( .NOT. OPEN3( CTM_ADJ_1, FSNEW3, PNAME ) ) THEN
            XMSG = 'Could not open ' // CTM_ADJ_1 // ' file'
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF
         END IF

C write the initial concentrations as step 0 on the conc file
C (inital data assumed to be in correct output units)

      ALLOCATE ( DBUFF( MY_NCOLS,MY_NROWS,NLAYS ), STAT = ALLOCSTAT )
         IF ( ALLOCSTAT .NE. 0 ) THEN
            XMSG = 'Failure allocating DBUFF'
            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF

c      DO SPC = 1, N_GC_CONC

c         DBUFF = CGRID( 1:MY_NCOLS,1:MY_NROWS,1:NLAYS,SPC )

c         IF ( .NOT. WRITE3( CTM_ADJ_1, GC_CONC( SPC ),
c     &                      ENDDATE, ENDTIME, DBUFF ) ) THEN
c            XMSG = 'Could not write ' //
c     &             GC_CONC( SPC )(1:TRIMLEN( GC_CONC( SPC ) ) ) //
c     &             ' to ' // CTM_ADJ_1
c            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
c            END IF
	    
c	 END DO

!! --> Create gradient file
         
          SDATE3D = JDATE
          STIME3D = 0
	  TSTEP3D = 0
	  NVARS3D = N_GC_EMIS
          VTYPE3D( 1 ) = M3REAL
          DO V = 1, N_GC_EMIS
             VTYPE3D( V ) = M3REAL
             VNAME3D( V ) = GC_EMIS( V )
             UNITS3D( SPC ) = 'ppm'
             VDESC3D( SPC ) = 'Gradient of ' // VNAME3D( SPC )
          END DO

	 IF (MYPE.EQ.0) THEN
	  IF ( .NOT. OPEN3( CTM_GRD_1, FSNEW3, PNAME ) ) THEN
            XMSG = 'Could not open ' // CTM_GRD_1 // ' file'
            CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF
          END IF

	  DBUFF = 0.
c          IDATE = JDATE
c          ITIME = JTIME

c      do v = 1, 121 !for 12 minute runs
      
          DO V = 1, N_GC_EMIS
	  
	  IF ( .NOT. WRITE3( CTM_GRD_1, GC_EMIS(V), 0, 0, DBUFF ) ) THEN
             XMSG = 'writing zeros to grad file failed'
             CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
             END IF
	  
	  END DO  
      
c             CALL NEXTIME ( IDATE, ITIME, 1200 )
      
c      end do
	    
      DEALLOCATE (DBUFF)

      WRITE( LOGDEV, '( /5X, 3( A, :, 1X ), I8, ":", I6.6 )' )
     &  'Timestep written to', CTM_CONC_1( 1:TRIMLEN( CTM_CONC_1 ) ),
     &  'for date and time', JDATE, JTIME
      WRITE( LOGDEV, '(  5X,  A, 1X, I8, ":", I6.6 )' )
     &  'from timestep on initial data files for date and time',
     &   JDATE, JTIME

      RETURN
      END
