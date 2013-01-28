MODEL = shells/CCTM_fwd 

# Compiler Definitions
FC   = /opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/bin/mpif90
CC    = /opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/bin/mpicc
CPLUS = /opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/bin/mpicpp

# Preprocessor
FPP  = /opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/bin/mpif90

# Compiler Flags
F_FLAGS = -O2 tp=istanbul -module /opt/home/amir/work/cmaq/modified/4.5.1/base/1208/fwd/MOD_DIR -I. 
C_FLAGS = -O2 -Msignextend tp=istanbul -I/opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/include
LINK_FLAGS = 

CPP_FLAGS =    \
 -Dparallel \
 -Dcluster \
 -DINTERPB=PINTERPB \
 -DM3ERR=PM3ERR \
 -DM3EXIT=PM3EXIT \
 -DM3WARN=PM3WARN \
 -DSHUT3=PSHUT3 \
 -DWRITE3=PWRITE3 \
 -DSUBST_MODULES=SE_MODULES \
 -DSUBST_BARRIER=SE_BARRIER \
 -DSUBST_GLOBAL_MAX=SE_GLOBAL_MAX \
 -DSUBST_GLOBAL_MIN=SE_GLOBAL_MIN \
 -DSUBST_GLOBAL_MIN_DATA=SE_GLOBAL_MIN_DATA \
 -DSUBST_GLOBAL_TO_LOCAL_COORD=SE_GLOBAL_TO_LOCAL_COORD \
 -DSUBST_GLOBAL_SUM=SE_GLOBAL_SUM \
 -DSUBST_GLOBAL_LOGICAL=SE_GLOBAL_LOGICAL \
 -DSUBST_LOOP_INDEX=SE_LOOP_INDEX \
 -DSUBST_SUBGRID_INDEX=SE_SUBGRID_INDEX \
 -DSUBST_HI_LO_BND_PE=SE_HI_LO_BND_PE \
 -DSUBST_SUM_CHK=SE_SUM_CHK \
 -DSUBST_INIT_ARRAY=SE_INIT_ARRAY \
 -DSUBST_COMM=SE_COMM \
 -DSUBST_MY_REGION=SE_MY_REGION \
 -DSUBST_SLICE=SE_SLICE \
 -DSUBST_GATHER=SE_GATHER \
 -DSUBST_DATA_COPY=SE_DATA_COPY \
 -DSUBST_IN_SYN=SE_IN_SYN

# Libraries
LIBRARIES = -L/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/lib/stenex -lse_snl \
 -L/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/lib/pario.netcdf3.6.3 -lpario  \
 -L/opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/lib -lmpich \
 -L/opt/local/support/Linux2_x86_64pgi/ioapi/3.1-netcdf3.6.3/Linux2_x86_64pg -lioapi \
 -L/opt/local/support/Linux2_x86_64pgi/netcdf/3.6.3/lib -lnetcdf

# Include file subsitution definitions
INCLUDES = \
 -DSUBST_GRID_ID= \
 -DSUBST_PE_COMM=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/PE_COMM.EXT\" \
 -DSUBST_CONST=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/CONST.EXT\" \
 -DSUBST_FILES_ID=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/FILES_CTM_adj.EXT\" \
 -DSUBST_EMPR_VD=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/EMISPRM.vdif.EXT\" \
 -DSUBST_EMPR_CH=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/EMISPRM.chem.EXT\" \
 -DSUBST_IOPARMS=\"/opt/local/support/Linux2_x86_64pgi/ioapi/3.1-netcdf3.6.3/ioapi/fixed_src/PARMS3.EXT\" \
 -DSUBST_IOFDESC=\"/opt/local/support/Linux2_x86_64pgi/ioapi/3.1-netcdf3.6.3/ioapi/fixed_src/FDESC3.EXT\" \
 -DSUBST_IODECL=\"/opt/local/support/Linux2_x86_64pgi/ioapi/3.1-netcdf3.6.3/ioapi/fixed_src/IODECL3.EXT\" \
 -DSUBST_RXCMMN=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/RXCM.EXT\" \
 -DSUBST_RXDATA=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/RXDT.EXT\" \
 -DSUBST_GC_SPC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_SPC.EXT\" \
 -DSUBST_GC_EMIS=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_EMIS.EXT\" \
 -DSUBST_GC_ICBC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_ICBC.EXT\" \
 -DSUBST_GC_DIFF=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_DIFF.EXT\" \
 -DSUBST_GC_DDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_DDEP.EXT\" \
 -DSUBST_GC_DEPV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_DEPV.EXT\" \
 -DSUBST_GC_ADV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_ADV.EXT\" \
 -DSUBST_GC_CONC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_CONC.EXT\" \
 -DSUBST_GC_G2AE=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_G2AE.EXT\" \
 -DSUBST_GC_G2AQ=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_G2AQ.EXT\" \
 -DSUBST_GC_SCAV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_SCAV.EXT\" \
 -DSUBST_GC_WDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/GC_WDEP.EXT\" \
 -DSUBST_AE_SPC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_SPC.EXT\" \
 -DSUBST_AE_EMIS=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_EMIS.EXT\" \
 -DSUBST_AE_ICBC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_ICBC.EXT\" \
 -DSUBST_AE_DIFF=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_DIFF.EXT\" \
 -DSUBST_AE_DDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_DDEP.EXT\" \
 -DSUBST_AE_DEPV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_DEPV.EXT\" \
 -DSUBST_AE_ADV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_ADV.EXT\" \
 -DSUBST_AE_CONC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_CONC.EXT\" \
 -DSUBST_AE_A2AQ=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_A2AQ.EXT\" \
 -DSUBST_AE_SCAV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_SCAV.EXT\" \
 -DSUBST_AE_WDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/AE_WDEP.EXT\" \
 -DSUBST_NR_SPC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_SPC.EXT\" \
 -DSUBST_NR_EMIS=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_EMIS.EXT\" \
 -DSUBST_NR_ICBC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_ICBC.EXT\" \
 -DSUBST_NR_DIFF=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_DIFF.EXT\" \
 -DSUBST_NR_DDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_DDEP.EXT\" \
 -DSUBST_NR_DEPV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_DEPV.EXT\" \
 -DSUBST_NR_ADV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_ADV.EXT\" \
 -DSUBST_NR_N2AE=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_N2AE.EXT\" \
 -DSUBST_NR_N2AQ=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_N2AQ.EXT\" \
 -DSUBST_NR_SCAV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_SCAV.EXT\" \
 -DSUBST_NR_WDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/saprc99/NR_WDEP.EXT\" \
 -DSUBST_TR_SPC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_SPC.EXT\" \
 -DSUBST_TR_EMIS=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_EMIS.EXT\" \
 -DSUBST_TR_ICBC=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_ICBC.EXT\" \
 -DSUBST_TR_DIFF=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_DIFF.EXT\" \
 -DSUBST_TR_DDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_DDEP.EXT\" \
 -DSUBST_TR_DEPV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_DEPV.EXT\" \
 -DSUBST_TR_ADV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_ADV.EXT\" \
 -DSUBST_TR_T2AQ=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_T2AQ.EXT\" \
 -DSUBST_TR_SCAV=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_SCAV.EXT\" \
 -DSUBST_TR_WDEP=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/trac0/TR_WDEP.EXT\" \
 -DSUBST_PACTL_ID=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/pa_noop/PA_CTL.EXT\" \
 -DSUBST_PACMN_ID=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/pa_noop/PA_CMN.EXT\" \
 -DSUBST_PADAT_ID=\"/opt/local/models/Linux2_x86_64pgi/cmaq/4.5.1/models/include/release/pa_noop/PA_DAT.EXT\" \
 -DSUBST_MPICH=\"/opt/local/support/Linux2_x86_64pgi/mpich2/1.4.1p1/include/mpif.h\"

# List of Object files needed for linking
OBJECTS =\
 VGRD_DEFN.o \
 CGRID_SPCS.o \
 HGRD_DEFN.o \
 GRID_CONF.o \
 PCGRID_DEFN.o \
 AVG_CONC.o \
 AERO_EMIS.o \
 kppdata_mod.o \
 PAGRD_DEFN.o \
 WVEL_DEFN.o \
 advstep.o \
 chkstep.o \
 driver.o \
 hcontvel.o \
 hcvelchk.o \
 sciproc.o \
 wr_aconc.o \
 wr_conc.o \
 wr_chk.o \
 distr_env.o \
 par_init.o \
 par_term.o \
 diffmsg.o \
 flcheck.o \
 grdcheck.o \
 initscen.o \
 initchk.o \
 load_cgrid.o \
 opconc.o \
 setup_logdev.o \
 couple.o \
 ppmv_msmr.o \
 advbc_map.o \
 hppm.o \
 vppm.o \
 rdbcon.o \
 xadvppm.o \
 yadvppm.o \
 zfdbc.o \
 vcontvel.o \
 zadvyamo.o \
 deform.o \
 hcdiff3d.o \
 hdiff.o \
 rho_j.o \
 conv_cgrid.o \
 edyintb.o \
 opddep.o \
 opemis.o \
 opmet.o \
 opssemis.o \
 rddepv.o \
 rdemis.o \
 rdmet.o \
 ssemis.o \
 tridiag.o \
 vdiff_map.o \
 vdiffim.o \
 phot.o \
 ping_noop.o \
 KPP_Precision.o \
 KPP_Pars.o \
 KPP_Glob.o \
 KPP_Util.o \
 KPP_JacobianSP.o \
 KPP_Jacobian.o \
 KPP_Function.o \
 KPP_LinAlg.o \
 KPP_Integrator.o \
 KPP_HessianSP.o \
 KPP_Hessian.o \
 kppinit.o \
 kppcalcks.o \
 kppdriver.o \
 aero_noop.o \
 aero_depv_noop.o \
 cloud_noop.o \
 pa_init.o \
 pa_irr.o \
 pa_irr_ctl.o \
 pa_mkhdr.o \
 pa_output.o \
 pa_update.o \
 cksummer.o \
 findex.o \
 get_envlist.o \
 lstepf.o \
 subhdomain.o \
 subhfile.o 

.SUFFIXES: .F .f .f90 .c


$(MODEL): $(OBJECTS)
	$(FC) $(LINK_FLAGS) $(OBJECTS) $(LIBRARIES) -o $@

.F.o:
	$(FC) -c -Mfixed -Mextend $(F_FLAGS) $(CPP_FLAGS) $(INCLUDES) $<

.f.o:
	$(FC) -Mfixed -Mextend $(F_FLAGS) -c $<

.f90.o:
	$(FC) -Mfreeform $(F_FLAGS) -c $<

.c.o:
	$(CC) $(C_FLAGS) -c $<
