#!/bin/tcsh

set startcfg = ${icfg}
set endcfg = ${icfg}

#increment => e.g. set to 10 if on PACS-CS and want to do 1880, 1890, 2000 etc...
set inc = 10


#list of chi interpolators currently supported by this script
#chiBar interpolators are just the list of chi interpolators below followed by "bar"
#e.g. pi+bar

#neutron1
#neutron2
#neutron4
#proton1
#proton2
#proton4
#pi+
#pi-
#rho+
#rho-
#lambda1_com
#lambda2_com
#lambda1_sing
#lambda2_sing
#lambda1_oct
#lambda2_oct
#sigma01
#sigmap
#sigmam
#sigma02
#xi1
#xim
#xi2
#xiStar
#nucleonspin3half
#ug5gmud
#uId
#delta+
#delta++
#proton5
#pis               #just a pi+ but different name
#pid               # ''
#piu               # ''
#nnd1              #just a proton but different name
#nuu1              # ''
#ddn1              #just a neutron but different name
#nnu1              # ''
#uNsu              #sigmap
#dNsd              #sigmam
#uNsNs             #xi1
#dNsNs             #xim
#lambda1_oct_Ns    #lambda1_oct
#rho1+
#rho2+
#rho3+
#rho4+
#rho1-
#rho2-
#rho3-
#rho4-
#rho1u0    #just a rhoi+ with different names
#rho2u0
#rho3u0
#rho4u0
#rho1d0
#rho2d0
#rho3d0
#rho4d0
#kaon+
#kaon-
#kaon0
#kaonbar0



#Make sure cfundir, reportfile, reportdir, tagfiledir are all set already


#rm tag file if still there from last time
rm -rf ${tagfiledir}

mkdir -p ${cfundir}
mkdir -p ${reportdir}
mkdir -p ${tagfiledir}
#mkdir -p ${texdir}

if (($#chilist % 2) != 0) then 
echo ${chilist}
echo "*********************************"
echo "*************ERROR***************"
echo "INCORRECT NUMBER OF INTERPOLATORS"
echo "*********************************"
echo "*********************************"
endif



if ( ${kB} == 0 ) then
   set isospin_symm = T
else
   set isospin_symm = F
endif


set kB_snk = ${kB}

# put different levels of smearings in .prop_sm_params file below




set gf_format = ${cfgformat}


#So we know whether to read in propagator types
#Code reads this from interpolator but we need to know
#whether we need to know whether we are 'catting' various prop
#file names or not....todo: fix?
set have_xoprop = T
set have_oxprop = T
set have_xxprop = F
set have_ooprop = F

#Assuming that haves_ means have strange
if ( $CfunHyp == T ) then

set haves_xoprop = T
set haves_oxprop = T
set haves_xxprop = F
set haves_ooprop = F
else
set haves_xoprop = F
set haves_oxprop = F
set haves_xxprop = F
set haves_ooprop = F
endif


if ( ${kB} == 0 ) then
  set havelight2_xoprop = F
  set havelight2_oxprop = F
else
  set havelight2_xoprop = T
  set havelight2_oxprop = T
endif

set havelight2_xxprop = F
set havelight2_ooprop = F

set xoPropsFileName = ${tagfiledir}/xoProps.prop_files
set xxPropsFileName = ${tagfiledir}/xxProps.prop_files
set ooPropsFileName = ${tagfiledir}/ooProps.prop_files
set xoPropstrangeFileName = ${tagfiledir}/xoPropstrange.prop_files
set xxPropstrangeFileName = ${tagfiledir}/xxPropstrange.prop_files
set ooPropstrangeFileName = ${tagfiledir}/ooPropstrange.prop_files
set xoProplight2FileName = ${tagfiledir}/xoProplight2.prop_files
set xxProplight2FileName = ${tagfiledir}/xxProplight2.prop_files
set ooProplight2FileName = ${tagfiledir}/ooProplight2.prop_files
set file_stub = ${tagfiledir}/cfgen_stub


#If false do all interpolator pairs in one job, i.e. only read the props once.
#If true, submit one job for each interpolator pair.

#BE CAREFUL - IF SUBMITTING SEPARATE JOBS FOR EACH CORRELATOR FOR CORRELATION MATRICES MAKE 
#SURE THAT THE CORRECT PROPAGATOR FILES ARE WRITTEN OUT.  FOR EXAMPLE: WRITING OUT THE
#PROP NAMES FOR THE STANDARD POINT TO ALL PROPS, XX LOOPS AND OOLOOPS FOR A 5 AND 3 QUARK CORRELATION
#MATRIX ANALYSIS WILL GIVE INCORRECT NUMBERS FOR THE 5 QUARK CREATION TO 3 QUARK ANNIHILATION PIECE IF
#separate_jobs IS SET TO TRUE AS THE CODE ONLY NEEDS TO READ IN TWO TYPES OF PROPS BUT SEES THE XX PROP
#NAME FIRST AND WILL READ THAT IN AS THE OO LOOP.


if (${separate_jobs} == F) then 
#already have checked size(chilist) is even
@ size = $#chilist / 2
cat <<EOF >> ${file_stub}.part_stubs
$size
EOF
endif



@ num_props = ( ( $endcfg - $startcfg ) / $inc ) + 1

    cat <<EOF > ${file_stub}.prop_cfun_info
${num_props}
${prop_fmt}
${cfun_fmt}
${parallel_io}
${gma_rep}
${gell_man_rep}
${pmin}
${pmax}
${sink_smear}
${do_ustar}
${sink_type}
${use_landau}
EOF

if (${sink_smear} == T) then
cat <<EOF > ${file_stub}.prop_sm_params
${smear_code}
${alpha_snk}
${u0_snk}
${kB_snk}
${nsnk}
EOF
foreach sink_smearing_l ( ${sink_smear_list} )
cat <<EOF >> ${file_stub}.prop_sm_params
${sink_smearing_l}
EOF
end #sink_smearing_l
cat <<EOF >> ${file_stub}.prop_sm_params
${swps_fat}
${use_stout}
${alpha_fat}
EOF
endif

if ( ${sink_type} == "laplacian" || ${sink_type} == "sm-laplacian" )  then

set ndim_lp = 2
set nsnk_lp = 2

#####${pre_proj_modes}
cat <<EOF > ${file_stub}.qpsnk_lp
${ndim_lp}
${dmodefile}
${umodefile}
${smodefile}
${xshift} ${xshift} ${xshift} ${tshift}   # gfshift
${nsnk_lp}
EOF


foreach dsnk ( 64 96 ) #72 144  

@ usnk = ( $dsnk )
@ ssnk = ( $dsnk )

set sink_code = "LPd${dsnk}u${usnk}s${ssnk}"

if ( ${z_smearing} == T ) then
  set sink_code = ${sink_code}"Z"
endif

cat <<EOF >> ${file_stub}.qpsnk_lp
${sink_code}
-1
${dsnk}
1
2
${usnk}
1
-1
${ssnk}
2
EOF

end

endif    #end if sink_type == laplacian


if (${sink_smear} == T || ${prop_fmt} == "ifms") then
cat <<EOF > ${file_stub}.gfs
${num_props}
${gf_format}
EOF
endif



cat <<EOF > ${file_stub}.lat
${nx}
${ny}
${nz}
${nt}
EOF


###Particle Loop starts here


#Loop over particles you want to calculate
foreach ij( `seq 1 2 $#chilist` )

    @ ij2 = $ij + 1

    set part_stub = ${tagfiledir}/$chilist[$ij]$chilist[$ij2]
    set cfun_prefix = ${cfundir}/"icfg"

#write out cfun_name and cfun_prefix
cat <<EOF >> ${part_stub}.interp
$chilist[$ij]$chilist[$ij2]
${cfun_prefix}
EOF

#list of possible chi interpolators to cat.  
##########################################
#Warning: Putting an "illegal" .interp file
#may or may not trigger the appocalypse.
#For example - having a strange quark but
#no anti-strange to contract it with or
#colour indicies that aren't summed will 
#likely seg. fault.  toDO: Fix
##########################################
    if ($chilist[$ij] == "proton1") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) u^{c}
EOF
#
    else if ($chilist[$ij] == "nnd1") then
#proton1 but aim for neutral quarks in place of uquark
#quarks are set to neutral manually in cfun-xy.csh
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) u^{c}
EOF
#
    else if ($chilist[$ij] == "nuu1") then
#proton1 but aim for neutral quarks in place of dquark
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) u^{c}
EOF
#
    else if ($chilist[$ij] == "proton2") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C) d^{b}] (\gamma_{5}) u^{c}
EOF



    else if ($chilist[$ij] == "proton4") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}\gamma_{4}) d^{b}] (I) u^{c}
EOF

   else if ($chilist[$ij] == "neutron1") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) d^{c}
EOF
#
   else if ($chilist[$ij] == "nnu1") then
#neutron1 but aim for neutral quarks in place of d quark
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) d^{c}
EOF
#
   else if ($chilist[$ij] == "ddn1") then
#neutron1 but aim for neutral quarks in place of d quark
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) d^{b}] (I) d^{c}
EOF
#
    else if ($chilist[$ij] == "neutron2") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C) d^{b}] (\gamma_{5}) d^{c}
EOF

    else if ($chilist[$ij] == "neutron4") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}\gamma_{4}) d^{b}] (I) d^{c}
EOF
  ############### K^{+}
    else if ($chilist[$ij] == "kaon+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [As^{e} (\gamma_{5}) u^{e}]
EOF

  ############### K^{-}
    else if ($chilist[$ij] == "kaon-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{5}) s^{e}]
EOF

  ############### K^{0}
    else if ($chilist[$ij] == "kaon0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [As^{e} (\gamma_{5}) d^{e}]
EOF

  ############### \overline{K^{0}}
    else if ($chilist[$ij] == "kaonbar0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{5}) s^{e}]
EOF


    else if ($chilist[$ij] == "pi+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{5}) u^{e}]
EOF

    else if ($chilist[$ij] == "pi-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{5}) d^{e}]
EOF
    else if ($chilist[$ij] == "piu") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{5}) u^{e}]
EOF

    else if ($chilist[$ij] == "pis") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{5}) u^{e}]
EOF

    else if ($chilist[$ij] == "pid") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{5}) u^{e}]
EOF

    else if ($chilist[$ij] == "rho+") then
	   
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end

cat <<EOF >> ${part_stub}.interp
0
0
1
1.0 * [Ad^{e} (\gamma_{\mu}) u^{e}]
EOF

    else if ($chilist[$ij] == "rho-") then
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end

cat <<EOF >> ${part_stub}.interp
0
0
1
1.0 * [Au^{e} (\gamma_{\mu}) d^{e}]
EOF

    else if ($chilist[$ij] == "rhoup+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{8}) u^{e}]
EOF

    else if ($chilist[$ij] == "rhodn+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{9}) u^{e}]
EOF

    ########## rho+ with lorentz index separated
    else if ($chilist[$ij] == "rho1+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{1}) u^{e}]
EOF

    else if ($chilist[$ij] == "rho2+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{2}) u^{e}]
EOF

    else if ($chilist[$ij] == "rho3+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{3}) u^{e}]
EOF

    else if ($chilist[$ij] == "rho4+") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Ad^{e} (\gamma_{4}) u^{e}]
EOF

    ########## rho- with lorentz index separated
    else if ($chilist[$ij] == "rho1-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{1}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho2-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{2}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho3-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{3}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho4-") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{4}) d^{e}]
EOF

    #neutral connected rho meson, d part
    ########## rho0u with lorentz index separated. FEED IN ONLY u props. i.e. u=d=uprop
    else if ($chilist[$ij] == "rho1u0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{1}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho2u0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{2}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho3u0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{3}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho4u0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{4}) d^{e}]
EOF

    #neutral connected rho meson, d part
    ########## rho0d with lorentz index separated. FEED IN ONLY d props. i.e. u=d=uprop
    else if ($chilist[$ij] == "rho1d0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{1}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho2d0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{2}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho3d0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{3}) d^{e}]
EOF

    else if ($chilist[$ij] == "rho4d0") then
cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (\gamma_{4}) d^{e}]
EOF


    ############Lambda1 common
    else if ($chilist[$ij] == "lambda1_com") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
2
1.0/sqrt(2.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(2.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

   ############Lambda2 common
   else if ($chilist[$ij] == "lambda2_com") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
2
1.0/sqrt(2.0) * [u^{a} (C) s^{b} ] (\gamma_{5}) d^{c}
-1.0/sqrt(2.0) * [d^{a} (C) s^{b} ] (\gamma_{5}) u^{c}
EOF

  ############Lambda1 singlet
   else if ($chilist[$ij] == "lambda1_sing") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0 * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
-2.0 * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
2.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda2 singlet
   else if ($chilist[$ij] == "lambda2_sing") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0 * [u^{a} (C) d^{b} ] (\gamma_{5}) s^{c}
-2.0 * [u^{a} (C) s^{b} ] (\gamma_{5}) d^{c}
2.0 * [d^{a} (C) s^{b} ] (\gamma_{5}) u^{c}
EOF


  ############Lambda1 octet
   else if ($chilist[$ij] == "lambda1_oct") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral S
   else if ($chilist[$ij] == "lambda1_oct_Ns") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral light S
   else if ($chilist[$ij] == "lambda1_oct_ddnL") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral light u,d with a heavy s quark
   else if ($chilist[$ij] == "lambda1_oct_nLnLs") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral light u,d with a light s quark (a d)
   else if ($chilist[$ij] == "lambda1_oct_nLnLd") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral heavy u,d with a heavy s quark
   else if ($chilist[$ij] == "lambda1_oct_NsNss") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF

  ############Lambda1 octet but neutral heavy u,d with a light s quark (a d)
   else if ($chilist[$ij] == "lambda1_oct_NsNsd") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) d^{b} ] (I) s^{c}
1.0/sqrt(6.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF


  ############Lambda2 oct
   else if ($chilist[$ij] == "lambda2_oct") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
2.0/sqrt(6.0) * [u^{a} (C) d^{b} ] (\gamma_{5}) s^{c}
1.0/sqrt(6.0) * [u^{a} (C) s^{b} ] (\gamma_{5}) d^{c}
-1.0/sqrt(6.0) * [d^{a} (C) s^{b} ] (\gamma_{5}) u^{c}
EOF

  ############sigma^{0}_{1}
   else if ($chilist[$ij] == "sigma01") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
2
1.0/sqrt(2.0) * [u^{a} (C\gamma_{5}) s^{b} ] (I) d^{c}
1.0/sqrt(2.0) * [d^{a} (C\gamma_{5}) s^{b} ] (I) u^{c}
EOF
   ##################sigma^{+}
    else if ($chilist[$ij] == "sigmap") then
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) u^{c}
EOF

   ##################sigmam^{-}
    else if ($chilist[$ij] == "sigmam") then
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) d^{c}
EOF

   ##################sigma^{+} but neutral s
    else if ($chilist[$ij] == "uNsu") then
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) s^{b}] (I) u^{c}
EOF

   ##################sigma^{-} but neutral s
    else if ($chilist[$ij] == "dNsd") then
cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b}] (I) d^{c}
EOF


  ############sigma^{0}_{2}
   else if ($chilist[$ij] == "sigma02") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
2
1.0/sqrt(2.0) * [u^{a} (C) s^{b} ] (\gamma_{5}) d^{c}
1.0/sqrt(2.0) * [d^{a} (C) s^{b} ] (\gamma_{5}) u^{c}
EOF

  ############xi1
   else if ($chilist[$ij] == "xi1") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) s^{b} ] (I) s^{c}
EOF

  ############xi^{-}
   else if ($chilist[$ij] == "xim") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) s^{c} 
EOF

    ############xi^{-} but with a neutral down quark
   else if ($chilist[$ij] == "ssn") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) s^{c} 
EOF

    ############xi^{-} but with three strange quarks - manually of course
    ############i.e. this is the octet Xi^{-}_{3S}
   else if ($chilist[$ij] == "sss") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) s^{c} 
EOF

    ############xi^{-} but with three strange quarks - manually of course
    ############i.e. this is the octet Xi^{-}_{3S}
    ############ Now one of them (the singly rep, i.e. the d) is a neutral strange quark
   else if ($chilist[$ij] == "ssNs") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) s^{c} 
EOF



  ############xi1 but neutral s
   else if ($chilist[$ij] == "uNsNs") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}) s^{b} ] (I) s^{c}
EOF

  ############xi^{-} but neutral s
   else if ($chilist[$ij] == "dNsNs") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [d^{a} (C\gamma_{5}) s^{b} ] (I) s^{c} 
EOF


  ############xi2
   else if ($chilist[$ij] == "xi2") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
1
1.0 * [s^{a} (C) u^{b} ] (\gamma_{5}) s^{c}
EOF

 ############xiStar
   else if ($chilist[$ij] == "xiStar") then

cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end

cat <<EOF >> ${part_stub}.interp
0
1
a;b;c;
2
2.0/sqrt(3.0) * [s^{a} (C\gamma_{\mu}) u^{b} ] (I) s^{c}
1.0/sqrt(3.0) * [s^{a} (C\gamma_{\mu}) s^{b} ] (I) u^{c}
EOF

 ############nucleon spin 3/2 (only term proportional to g_{/mu/nu})
   else if ($chilist[$ij] == "nucleonspin3half") then
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end
cat <<EOF >> ${part_stub}.interp
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{5}\gamma_{\mu}) d^{b} ] (\gamma_{5}) u^{c}
EOF

   ############u g5 gmu d
   else if ($chilist[$ij] == "ug5gmud") then
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end


cat <<EOF >> ${part_stub}.interp
0
0
1
1.0 * [Ad^{e} (\gamma_{5}\gamma_{\mu}) u^{e}]
EOF

    ##########u I d
    else if ($chilist[$ij] == "uId") then

cat <<EOF >> ${part_stub}.interp
0
0
0
1
1.0 * [Au^{e} (I) d^{e}]
EOF

 ############delta+
   else if ($chilist[$ij] == "delta+") then
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end
cat <<EOF >> ${part_stub}.interp
0
1
a;b;c;
2
2.0/sqrt(3.0) * [u^{a} (C\gamma_{\mu}) d^{b} ] (I) u^{c}
1.0/sqrt(3.0) * [u^{a} (C\gamma_{\mu}) u^{b} ] (I) d^{c}
EOF

############delta++
   else if ($chilist[$ij] == "delta++") then
cat <<EOF >> ${part_stub}.interp
$#lorentz_in
EOF
	#cat the lorentz indicies we want to calculate
	foreach ik( `seq 1 $#lorentz_in` )
cat <<EOF >> ${part_stub}.interp
$lorentz_in[$ik]
EOF
	end
cat <<EOF >> ${part_stub}.interp
0
1
a;b;c;
1
1.0 * [u^{a} (C\gamma_{\mu}) u^{b} ] (I) u^{c}
EOF

############proton5
   else if ($chilist[$ij] == "proton5") then

cat <<EOF >> ${part_stub}.interp
0
0
1
a;b;c;
3
1.0/sqrt(3.0) * [u^{a} (C\gamma_{5}) d^{b} ] (\gamma_{5}) d^{c} [Ad^{e} (\gamma_{5}) u^{e}]
-0.5/sqrt(3.0) * [u^{a} (C\gamma_{5}) d^{b} ] (\gamma_{5}) u^{c} [Ad^{e} (\gamma_{5}) d^{e}]
0.5/sqrt(3.0) * [u^{a} (C\gamma_{5}) d^{b} ] (\gamma_{5}) u^{c} [Au^{e} (\gamma_{5}) u^{e}]
EOF

    endif


###########################################################################
#list of possible chiBar's to cat
###########################################################################
    if ($chilist[$ij2] == "proton1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF
#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "nnd1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF
#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "nuu1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF
#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "proton2bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "sigmapbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "sigmambar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) As^{ap}]
EOF

    else if ($chilist[$ij2] == "uNsubar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "dNsdbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) As^{ap}]
EOF


    else if ($chilist[$ij2] == "proton4bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}\gamma_{4}) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "neutron1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF
#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "nnu1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF

#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "ddn1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF
#-1.0 * Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
    else if ($chilist[$ij2] == "neutron2bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "neutron4bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}\gamma_{4}) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "kaon+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{5}) s^{ep}]
EOF

    else if ($chilist[$ij2] == "kaon-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [As^{ep} (\gamma_{5}) u^{ep}]
EOF

    else if ($chilist[$ij2] == "kaon0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{5}) s^{ep}]
EOF

    else if ($chilist[$ij2] == "kaonbar0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [As^{ep} (\gamma_{5}) d^{ep}]
EOF


    else if ($chilist[$ij2] == "pi+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "pi-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{5}) u^{ep}]
EOF

    else if ($chilist[$ij2] == "piubar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "pisbar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "pidbar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{5}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "rho+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{\nu}) d^{ep}]
EOF

   else if ($chilist[$ij2] == "rho-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{\nu}) u^{ep}]
EOF
    else if ($chilist[$ij2] == "rhoup+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{9}) d^{ep}]
EOF

   else if ($chilist[$ij2] == "rhodn+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{8}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "rho1+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{1}) d^{ep}]
EOF

   else if ($chilist[$ij2] == "rho2+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{2}) d^{ep}]
EOF
   else if ($chilist[$ij2] == "rho3+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{3}) d^{ep}]
EOF

   else if ($chilist[$ij2] == "rho4+bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Au^{ep} (\gamma_{4}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "rho1-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{1}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho2-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{2}) u^{ep}]
EOF
   else if ($chilist[$ij2] == "rho3-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{3}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho4-bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{4}) u^{ep}]
EOF

    else if ($chilist[$ij2] == "rho1u0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{1}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho2u0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{2}) u^{ep}]
EOF
   else if ($chilist[$ij2] == "rho3u0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{3}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho4u0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{4}) u^{ep}]
EOF


    else if ($chilist[$ij2] == "rho1d0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{1}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho2d0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{2}) u^{ep}]
EOF
   else if ($chilist[$ij2] == "rho3d0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{3}) u^{ep}]
EOF

   else if ($chilist[$ij2] == "rho4d0bar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (\gamma_{4}) u^{ep}]
EOF


    else if ($chilist[$ij2] == "lambda1_combar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-1.0/sqrt(2.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(2.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda2_combar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-1.0/sqrt(2.0) * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]
1.0/sqrt(2.0) * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_singbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0 * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
2.0 * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
-2.0 * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda2_singbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0 * As^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap} ]
2.0 * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]
-2.0 * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_octbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_Nsbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_ddnLbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_nLnLsbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_nLnLdbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_NsNsdbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "lambda1_oct_NsNssbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF


    else if ($chilist[$ij2] == "lambda2_octbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-2.0/sqrt(6.0) * As^{cp} (\gamma_{5}) [Ad^{bp} (C) Au^{ap} ]
-1.0/sqrt(6.0) * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]
1.0/sqrt(6.0) * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "sigma01bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-1.0/sqrt(2.0) * Ad^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
-1.0/sqrt(2.0) * Au^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "sigma02bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-1.0/sqrt(2.0) * Ad^{cp} (\gamma_{5}) [As^{bp} (C) Au^{ap} ]
-1.0/sqrt(2.0) * Au^{cp} (\gamma_{5}) [As^{bp} (C) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "xi1bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
EOF

    else if ($chilist[$ij2] == "ximbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "ssnbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "sssbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "ssNsbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF

    else if ($chilist[$ij2] == "uNsNsbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Au^{ap} ]
EOF

    else if ($chilist[$ij2] == "dNsNsbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [As^{bp} (C\gamma_{5}) Ad^{ap} ]
EOF


    else if ($chilist[$ij2] == "xi2bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * As^{cp} (I) [Au^{bp} (C\gamma_{5}) As^{ap} ]
EOF

    else if ($chilist[$ij2] == "xiStarbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-2.0/sqrt(3.0) * As^{cp} (I) [Au^{bp} (\gamma_{\nu}C) As^{ap} ]
-1.0/sqrt(3.0) * Au^{cp} (I) [As^{bp} (\gamma_{\nu}C) As^{ap} ] 
EOF

    else if ($chilist[$ij2] == "nucleonspin3halfbar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp}(\gamma_{5}) [Ad^{bp} (\gamma_{\nu}\gamma_{5}C) Au^{ap}]
EOF

    else if ($chilist[$ij2] == "ug5gmudbar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0*[Au^{ep} (\gamma_{\nu}\gamma_{5}) d^{ep}]
EOF

    else if ($chilist[$ij2] == "uIdbar") then
cat <<EOF >> ${part_stub}.interp
0
0
1
-1.0 * [Ad^{ep} (I) u^{ep}]
EOF
 
   else if ($chilist[$ij2] == "delta+bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
2
-2.0/sqrt(3.0) *  Au^{cp} (I)[Ad^{bp} (\gamma_{\nu}C) Au^{ap} ] 
-1.0/sqrt(3.0) *  Ad^{cp} (I)[Au^{bp} (\gamma_{\nu}C) Au^{ap} ] 
EOF
 
   else if ($chilist[$ij2] == "delta++bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
1
-1.0 * Au^{cp} (I) [Au^{bp} (\gamma_{\nu}C) Au^{ap} ]
EOF

  else if ($chilist[$ij2] == "proton5bar") then
cat <<EOF >> ${part_stub}.interp
0
1
ap;bp;cp;
3
-0.5/sqrt(3.0) * [Au^{ep} (\gamma_{5}) u^{ep}] Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
0.5/sqrt(3.0) * [Ad^{ep} (\gamma_{5}) d^{ep}] Au^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
-1.0/sqrt(3.0) * [Au^{ep} (\gamma_{5}) d^{ep}] Ad^{cp} (I) [Ad^{bp} (C\gamma_{5}) Au^{ap}]
EOF

    endif


cat <<EOF >> ${part_stub}.interp
${isospin_symm}
${su3flav_lim}
EOF

if (${separate_jobs} == T) then

cat <<EOF > ${part_stub}$chilist[$ij]$chilist[$ij2].part_stubs
1
${part_stub}
EOF

set name = $chilist[$ij]
#qsub -N ${name} -v file_stub=${file_stub}$chilist[$ij]$chilist[$ij2].file_stubs job.csh

else

cat <<EOF >> ${file_stub}.part_stubs
${part_stub}
EOF

endif

end

foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${file_stub}.cfg_ids
-${run}-00${icfg}
EOF
end

foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${file_stub}.gfs
${cfgdir}${cfgprefix}${icfg}
EOF
end

#############################################################
#							    #
#        If doing 3 quarks, i.e. u, d and s                 #
#        Must be fed into cfgen in order u, s, d            #
#							    #
#############################################################

##/short/e31/alk566/MPhil/cfg/FLIC/su3b394k1324s20t40IMPFLIC/su3b394k1324s20t40IMPFLICc0${icfg}
#uquark
if ($have_xoprop == T || $have_oxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xoPropsFileName}
EOF
#foreach icfg ( `seq -w $startcfg $inc $endcfg` )
#set uquark = "uquarkBF${kBu}${usrc}-${run}-00${icfg}"
set uquarkname = $upropdir$uquark$upropsuffix
cat <<EOF >> ${xoPropsFileName}
${uquarkname}
EOF
#end
endif

if ($have_xxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xxPropsFileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${xxPropsFileName}
/short/e31/alk566/mdssgetstuff/PACS-CS/props/kud13770/xx/series-a/srcsm35/RC32x64_B1900Kud01377000Ks01364000C1715-${run}-00${icfg}k13770srcsm35xx.prop
EOF
end
endif

if ($have_ooprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${ooPropsFileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${ooPropsFileName}
/short/e31/alk566/mdssgetstuff/PACS-CS/props/kud13770/oo/srcsm35/ooloops32t64sm100c0${icfg}.sc_mat
EOF
end
endif

#strange quark
if ($haves_xoprop == T || $haves_oxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xoPropstrangeFileName}
EOF
#foreach icfg ( `seq -w $startcfg $inc $endcfg` )
set squarkname = $spropdir$squark$spropsuffix
cat <<EOF >> ${xoPropstrangeFileName}
${squarkname}
EOF
#end
endif


if ($haves_xxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xxPropstrangeFileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${xxPropstrangeFileName}
EOF
end
endif

if ($haves_ooprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${ooPropstrangeFileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${ooPropstrangeFileName}
EOF
end
endif

#dquark
if ($havelight2_xoprop == T || $havelight2_oxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xoProplight2FileName}
EOF
#foreach icfg ( `seq -w $startcfg $inc $endcfg` )
#set dquark = "dquarkBF${kB}${dsrc}-${run}-00${icfg}"
set dquarkname = $dpropdir$dquark$dpropsuffix
cat <<EOF >> ${xoProplight2FileName}
${dquarkname}
EOF
#end
endif


if ($havelight2_xxprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${xxProplight2FileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${xxProplight2FileName}
EOF
end
endif

if ($havelight2_ooprop == T) then
    cat <<EOF >> ${file_stub}.prop_cfun_info
${ooProplight22FileName}
EOF
foreach icfg ( `seq -w $startcfg $inc $endcfg` )
cat <<EOF >> ${ooProplight2FileName}
EOF
end
endif


echo "here" $reportfile

set exe = ./cfungenGPU${exeend}

mpirun -np ${numgpus} $exe <<EOF >> $reportfile
${file_stub}
2
EOF

