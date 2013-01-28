
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
C $Header: /home/amir/work/cmaq4_5/models/CCTM/src/procan/pa/pa_mkhdr.F,v 1.1.1.1 2006/03/15 20:43:52 sjr Exp $ 

C what(1) key, module and SID; SCCS file; date and time of last delta:
C %W% %P% %G% %U%

C=======================================================================
      SUBROUTINE PA_MKHDR ( TYPE, NFL, OUTFNAME, SDATE, STIME, TSTEP )

!     USE VGRD_DEFN
      USE GRID_CONF             ! horizontal & vertical domain specifications
      USE PAGRD_DEFN            ! PA horiz domain specs

      IMPLICIT NONE

C used in pa_init
C FIRSTIME gets some DESC3 common variables from CTM_CONC_1 to be used
C for both IPR and IRR if needed. Assumes DESC3 common unchanged between
C calls

!     INCLUDE SUBST_HGRD_ID     ! horizontal dimensioning parameters
!     INCLUDE SUBST_VGRD_ID     ! vertical dimensioning parameters
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IOFDESC     ! file header data structure
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_FILES_ID    ! file name parameters
!     INCLUDE SUBST_COORD_ID    ! coordinate and domain definitions
!     INCLUDE SUBST_BLKPRM      ! cell blocking parameters
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
      INCLUDE SUBST_AE_SPC      ! aerosol species table

      INCLUDE SUBST_PACMN_ID    ! PA common block definitions

C Arguments:
      CHARACTER( 3 ) ::  TYPE   ! IPR or IRR
      INTEGER NFL               ! file sequence no.
      CHARACTER( 16 ) :: OUTFNAME  ! Assigned IPR or IRR output file name
      INTEGER SDATE             ! starting date,    format YYYYDDD
      INTEGER STIME             ! starting time,    format HHMMSS
      INTEGER TSTEP( 2 )        ! time step vector (HHMMSS)
                                ! TSTEP(1) = local output step
                                ! TSTEP(2) = sciproc sync. step (chem)

C Parameters:
      INTEGER, PARAMETER :: AE_START = N_GC_SPC + 2

      INTEGER, PARAMETER :: NR_START = AE_START + N_AE_SPC

      INTEGER AE_INDX   ! Index for aerosol species
      INTEGER IPRSPC    ! Index for IPR species
      INTEGER PL        ! Index for PA output level
      INTEGER VARINDX   ! Index for output variable
      INTEGER L, NOUT   ! Loop indicies
      INTEGER NSP, NPR  ! Loop indices for finding IPR species
      INTEGER ICG       ! species pointer

      CHARACTER( 16 ) ::  PNAME = 'PA_MKHDR'  ! Subroutine Name

      LOGICAL, SAVE :: FIRSTIME = .TRUE.

C-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN
         FIRSTIME = .FALSE.

ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
C  Get concfile description and reconfigure output domain
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
         IF ( .NOT. OPEN3( CTM_CONC_1, FSREAD3, PNAME ) ) THEN
            CALL M3EXIT( PNAME, SDATE, STIME,
     &         'Could not open ' // CTM_CONC_1 // ' file for readonly', 1 )
            END IF

         IF ( .NOT. DESC3( CTM_CONC_1 ) ) THEN
            CALL M3EXIT( PNAME, SDATE, STIME,
     &         'Could not get description of concentration file ' //
     &          CTM_CONC_1, 2 )
            END IF

         IF ( .NOT. CLOSE3( CTM_CONC_1 ) ) THEN
            CALL M3EXIT( PNAME, SDATE, STIME,
     &         'Could not close ' // CTM_CONC_1 // ' file', 1 )
            END IF

         SDATE3D = SDATE
         STIME3D = STIME
         CALL NEXTIME( SDATE3D, STIME3D, TSTEP( 1 ) )

         NCOLS3D = PACOLS
         NROWS3D = PAROWS
         NLAYS3D = PALEVS

         XORIG3D = XORIG3D + DBLE( PA_BEGCOL - 1 ) * XCELL3D
         YORIG3D = YORIG3D + DBLE( PA_BEGROW - 1 ) * YCELL3D

         DO L = PA_BEGLEV, PA_ENDLEV + 1
            PL = L - PA_BEGLEV + 1
            VGLVS3D ( PL ) = VGLVS_GD( L )
            END DO

         END IF   ! FIRSTIME

      IF ( TYPE .EQ. 'IPR' ) THEN

         FDESC3D( 1 ) = 'Integrated Process Rates Output File ' // OUTFNAME
         NVARS3D = MIN( MXVARS3 , ( NIPRVAR - ( NFL - 1 ) * MXVARS3 ) )

         DO NOUT = 1, NVARS3D
            VARINDX = ( NFL - 1 ) * MXVARS3 + NOUT
            VNAME3D( NOUT ) = IPRNAME( VARINDX )
            VTYPE3D( NOUT ) = M3REAL

C..Find the IPR species to set correct units descriptor
            DO NSP = 1, N_IPR_SPC
               DO NPR = 1, NPRCS
                  IF ( VARINDX .EQ. IPROUT( NSP, NPR ) ) THEN
                     IPRSPC = NSP
                     EXIT
                     ENDIF
                  ENDDO
               ENDDO

            ICG = IPR2GRD( IPRSPC, 1 )
            UNITS3D( NOUT ) = 'ppmV'

            IF ( ICG .GE. AE_START .AND. ICG .LT. NR_START ) THEN
               AE_INDX = ICG - AE_START + 1
               IF ( AE_SPC( AE_INDX ) ( 1 : 3 ) .EQ. 'NUM' ) THEN
                  UNITS3D( NOUT ) = 'number/m**3'
                  ELSE IF ( AE_SPC( AE_INDX ) ( 1 : 3 ) .EQ. 'SRF' ) THEN
                  UNITS3D( NOUT ) = 'm**2/m**3'
                  ELSE
                  UNITS3D( NOUT ) = 'micrograms/m**3'
                  END IF
               END IF

               VDESC3D( NOUT ) = IPRDESC( VARINDX )
            END DO

         ELSE IF ( TYPE .EQ. 'IRR' ) THEN

         FDESC3D( 1 ) = 'Integrated Reaction Rate Output File ' // OUTFNAME
         NVARS3D = MIN( MXVARS3 , ( NIRRVAR - ( ( NFL - 1 ) * MXVARS3 ) ) )

         DO NOUT = 1, NVARS3D
            VARINDX = ( NFL - 1 ) * MXVARS3 + NOUT
            VNAME3D( NOUT ) = IRRNAME( VARINDX )
            VTYPE3D( NOUT ) = M3REAL
            UNITS3D( NOUT ) = 'ppm'
            VDESC3D( NOUT ) = IRRDESC( VARINDX )
            END DO

         ELSE

         CALL M3EXIT( PNAME, SDATE, STIME,
     &        'Incorrect process analysis type specified', 2 )

         END IF

      RETURN
      END

