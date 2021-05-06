# !/bash/bin 

## Output Dir
#odir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem2D/loc2D/locNSC/
#odir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem2D/loc2D/loc/
odir=/Users/banjo/Projects/nll_pnsn/NLLoc/outHypParse/

## Output File 
ofile=bremUP_2DNSC512.txt
#ofile=bremUP_2DSC.txt
#ofile=bremUP_3DSC.txt
#ofile=bremUP_3DNSC.txt

## Input Dir
#ddir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem2D/loc2D/locNSC/
#ddir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem2D/loc2D/loc/
#ddir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem3D/loc3D/loc/
#ddir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem3D/loc3D/locNSC/
ddir=/Users/banjo/Projects/nll_pnsn/NLLoc/test/brem2D/loc


## Input Files 
ifile=bremUP_2Dnsc.sum.grid0.loc.hyp
ifile2=bremUP_2Dnsc.sum.grid0.loc.arc
ifile3=evid_header.txt



awk '{print $1}' ${ifile3} > tmp.evidsH
mv tmp.evidsH $ddir

cd $ddir

grep ^QML_ConfidenceEllipsoid ${ifile} | awk  '{print $2,$4,$6,$8,$10,$12}' | uniq > tmp.qceH
grep ^QML_ConfidenceEllipsoid ${ifile} | awk '{print $3,$5,$7,$9,$11,$13}' > tmp.qceD
cat tmp.qceH tmp.qceD > tmp.g

grep ^QUALITY ${ifile} | awk '{print $8,$10,$12,$14}' | uniq  > tmp.qualityH
grep ^QUALITY ${ifile} | awk '{print $9,$11,$13,$15}' > tmp.qualityD
cat tmp.qualityH tmp.qualityD > tmp.a

grep ^GEOGRAPHIC ${ifile} | awk '{print $2}' | uniq > tmp.geographicKK
grep ^GEOGRAPHIC ${ifile} | awk '{printf "%4s %2s %2s %2s %2s %06.3f\n" ,$3,$4,$5,$6,$7,$8}' | awk '{print $1"-"$2"-"$3"T"$4":"$5":"$6}' > tmp.geographicBBB
cat tmp.geographicKK tmp.geographicBBB > tmp.y

grep ^GEOGRAPHIC ${ifile} | awk '{print "m"$9,"m"$11,"m"$13}' | uniq > tmp.geographicH
grep ^GEOGRAPHIC ${ifile} | awk '{print $10,$12,$14}' > tmp.geographicD
cat tmp.geographicH tmp.geographicD > tmp.b

grep ^VPVSRATIO ${ifile} | awk '{print $2,$4,$6}' | uniq > tmp.vpvsH
grep ^VPVSRATIO ${ifile} | awk '{print $3,$5,$7}' > tmp.vpvsD
cat tmp.vpvsH tmp.vpvsD > tmp.c

grep ^STAT_GEOG ${ifile} | awk '{print $2,"ex"$4,"ex"$6}' | uniq > tmp.stat_geogH
grep ^STAT_GEOG ${ifile} | awk '{print $3,$5,$7}' > tmp.stat_geogD
cat tmp.stat_geogH tmp.stat_geogD > tmp.d

grep ^QML_OriginQuality ${ifile} | awk '{print $2,$4,$6,$8}' | uniq > tmp.qoqH
grep ^QML_OriginQuality ${ifile} | awk '{print $3,$5,$7,$9}' > tmp.qoqD
cat tmp.qoqH tmp.qoqD > tmp.e

grep ^QML_OriginUncertainty ${ifile} | awk '{print $2,$4,$6,$8}' | uniq > tmp.qouH
grep ^QML_OriginUncertainty ${ifile} | awk '{print $3,$5,$7,$9}' > tmp.qouD 
cat tmp.qouH tmp.qouD > tmp.f

grep ^NLLOC ${ifile} | awk '{print $1}' | uniq > tmp.xxx
grep ^NLLOC ${ifile} | awk '{print $3}' > tmp.yyy
cat tmp.xxx tmp.yyy > tmp.z

grep "^[ 0-9]" ${ifile2} | sed '1,$s/ /0/g' | awk '{print $1}' | cut -c139-146 > tmp.evidsD 
cat tmp.evidsH tmp.evidsD > tmp.evids

#paste tmp.y tmp.z tmp.a tmp.g tmp.b tmp.d tmp.c tmp.e tmp.f > ${odir}/$ofile
paste tmp.y tmp.evids tmp.z tmp.a tmp.g tmp.b tmp.d tmp.c tmp.e tmp.f > ${odir}/$ofile

rm tmp.*
