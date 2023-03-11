#!/bin/bash
############################################################################################
# Script for preparing DEM data assisting InSAR processing with GAMMA or ISCE.
# It will download either the NASADEM (srtm) OR Copernicus 30m resolution DEM with a AOI box.  
# For the detailed description of NASADEM, go
# https://earthdata.nasa.gov/esds/competitive-programs/measures/nasadem
# For the detailed description of Copernicus DEM, go: 
# https://spacedata.copernicus.eu/web/cscda/dataset-details?articleId=394198 

# Note:
# Before running this script you have to install the GDAL and AWS CLI tool. 
#
# Check the installation of AWS at
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
## For example, use the following commands to install aws on a linux OS.  
#$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#$ unzip awscliv2.zip
#$ sudo ./aws/install

#**************************************
#    Dataset Acknowledgement          #
#**************************************
# OpenTopography Portal (https://opentopography.org/) is acknowledged for accessing the data. 
#
# Copernicus DEM [DOI: https://doi.org/10.5069/G9028PQB]
# https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.032021.4326.1
#
# NASADEM (srtm) [DOI: https://doi.org/10.5069/G93T9FD9]
# https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.032021.4326.2
#
# Copyright Dr. Xiaowen Wang @ (UCD & SWJTU), 10/02/2022
#############################################################################################
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "`basename $0`: Script to download the 30-m NASADEM or Copernicus DEM and prepare"
echo " the input dem file for InSAR processing with ISCE or GAMMA"
echo ""
echo " v1.0, Feb. 10, 2022, Dr. Xiaowen Wang @ [UCD & SWJTU]"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
if [ $# -lt 2 ]; then
  echo "usage: `basename $0` <work_path> <dem_dir> <box> <soft_flag> [out_name]"
  echo " "
  echo "input parameters:"
  echo "work_path:	   the work path where a DEM folder will be created, e.g."$"PWD"
  echo "range_aoi:	   the lat-lon box of AOI (<west>/<east>/<south>/<north>)"
  echo "proc_flag:         which DEM source will be used: [default:0] "
  echo "                       0---> download new NASADEM (SRTM) from aws " 
  echo "                       1---> download new Copernicus DEM from aws " 
  echo "                       2---> use the existing DEM (*.tif) in the *dem_tiff* folder" 
  echo "soft_flag:         the dem will be convert to specific format: [default:0]"
  echo "                       0--->ISCE; 1--->GAMMA"   
  echo "out_name           the name for writting down the final dem product [default: dem]"             
  echo " "
  echo "**Note**:          if the proc_flag is set to be 2, the Geotiff DEM files..."
  echo "                   should be placed in the folder: "\$"work_path/dem/dem_tiff"   
  echo " "
  echo "Example:          `basename $0` "\$"PWD -2.12/-1.35/37.23/38.32"
  echo "		  `basename $0` "\$"PWD -2.12/-1.35/37.23/38.32 0 0 dem_name"
  echo "		  `basename $0` "\$"PWD -2.12/-1.35/37.23/38.32 1 1 dem_name"
  echo " "
  exit 0
fi
##################################################################################################
work_path=$1
box=$2

proc_flag=0
soft_flag=0
out_name="dem"

if [ $# -gt 2 ]; then proc_flag=$3; fi
if [ $# -gt 3 ]; then soft_flag=$4; fi
if [ $# -gt 4 ]; then out_name=$5"_"dem; fi

##
dem_dir=$work_path/dem
if [ ! -d $dem_dir ];then mkdir $dem_dir;fi
##
cd $dem_dir
rm -f list_*.txt
################################################################################################ Check the DEM boundary 
box_w=$(echo $box|cut -d/ -f1); 
box_e=$(echo $box|cut -d/ -f2); 
box_s=$(echo $box|cut -d/ -f3); 
box_n=$(echo $box|cut -d/ -f4); 

####Check the box left boundary 
box_W=$(echo $box_w |awk '{print int($1)}')
flag_W=$(echo $box_W |sed 's/[0-9,.]//g');
if [ "$flag_W"x == "-x" ]; then
  box_W0=$(echo $box_W|sed 's/[-]//g'|awk '{printf("%03d\n",$1+1)}')
  box_L="W"$box_W0
else 
  box_W0=$(echo $box_W|awk '{printf("%03d\n",$1)}')
  box_L="E"$box_W0
fi 

####Check the box right boundary  
box_E=$(echo $box_e |awk '{print int($1)}')
flag_E=$(echo $box_E |sed 's/[0-9,.]//g');
if [ "$flag_E"x == "-x" ]; then
  box_E0=$(echo $box_E|sed 's/[-]//g'|awk '{printf("%03d\n",$1)}')
  box_R="W"$box_E0
else 
  box_E0=$(echo $box_E|awk '{printf("%03d\n",$1)}')
  box_R="E"$box_E0
fi 

####Check the box bottom boundary 
box_S=$(echo $box_s |awk '{print int($1)}')
flag_S=$(echo $box_S |sed 's/[0-9,.]//g');
if [ "$flag_S"x == "-x" ]; then
  box_S0=$(echo $box_S|sed 's/[-]//g'|awk '{printf("%02d\n",$1+1)}')
  box_B="S"$box_S0
else 
  box_S0=$(echo $box_S|awk '{printf("%02d\n",$1)}')
  box_B="N"$box_S0
fi 

####Check the box top boundary  
box_N=$(echo $box_n |awk '{print int($1)}')
flag_N=$(echo $box_N |sed 's/[0-9,.]//g');
if [ "$flag_N"x == "-x" ]; then
  box_N0=$(echo $box_N|sed 's/[-]//g'|awk '{printf("%02d\n",$1)}')
  box_T="S"$box_N0
else 
  box_N0=$(echo $box_N|awk '{printf("%02d\n",$1)}')
  box_T="N"$box_N0
fi 

echo "******The DEM range:*******"
echo "$box_L/$box_R/$box_B/$box_T"
echo "***************************"
########## Configure the downloading DEMs 
flag_L=$(echo $box_L|cut -c1); flag_R=$(echo $box_R|cut -c1)
flag_B=$(echo $box_B|cut -c1); flag_T=$(echo $box_T|cut -c1)
echo "" >list_lon.tmp.txt
echo "" >list_lat.tmp.txt

if [ "$flag_L" == "$flag_R" ]; then
  list_lon=$(echo `seq $box_W0 $box_E0` `seq $box_E0 $box_W0`)
  for id_lon in $list_lon; do
    id_lon0=$(echo $id_lon|awk '{printf("%03d\n",$1)}')
    list_L="$flag_L$id_lon0"
    echo $list_L >>list_lon.txt
  done
else # for case 3W to 2E
  list_lon=$(echo `seq $box_W 0` `seq 1 $box_E`)
  for id_lon in $list_lon; do
    id_lon0=$(echo $id_lon|awk '{printf("%03d\n",$1)}')
    list_L="E$id_lon0"
    echo $list_L >>list_lon.tmp.txt
  done  
  sed 's/E-/W0/g' list_lon.tmp.txt >list_lon.txt
  fi
###
if [ "$flag_B" == "$flag_T" ]; then
  list_lat=$(echo `seq $box_N0 $box_S0` `seq $box_S0 $box_N0`)
  for id_lat in $list_lat; do
    id_lat0=$(echo $id_lat|awk '{printf("%02d\n",$1)}')
    list_B="$flag_B$id_lat0"
    echo $list_B >>list_lat.txt
  done
else #for case -2S to 4N
  list_lat=$(echo `seq $box_S 0` `seq 1 $box_N`)
  for id_lat in $list_lat; do
    id_lat0=$(echo $id_lat|awk '{printf("%02d\n",$1)}')
    list_B="N$id_lat0"
    echo $list_B >>list_lat.tmp.txt
  done  
  sed 's/N-/S0/g' list_lat.tmp.txt >list_lat.txt
fi
########################################################################################## Download the DEM
### SRTM
if [ $proc_flag == 0 ];then
  cat list_lon.txt |tr '[:upper:]' '[:lower:]' >list_lon.srtm.txt
  cat list_lat.txt |tr '[:upper:]' '[:lower:]' >list_lat.srtm.txt
  
  list_lon=$(cat list_lon.srtm.txt|sort -d |uniq)
  list_lat=$(cat list_lat.srtm.txt|sort -d |uniq)
    
  for id_lat in $list_lat; do 
    for id_lon in $list_lon; do 
      dem_name="NASADEM_HGT_"$id_lat""$id_lon""
      ## Check the dem 
      flag=$(aws s3 ls s3://raster/NASADEM/NASADEM_be/$dem_name.tif --endpoint-url https://opentopography.s3.sdsc.edu --no-sign-request)
      if [ "$flag"x == "x" ];then
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "The requested NASADEM $dem_name.tif do not exist, please check!"
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"     
      else 
        echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "The NASADEM file $dem_name has been found."
        if [ -f ./dem_tiff/$dem_name.tif ];then
          echo "Skip the downloading of $dem_name.tif as it has already exist!" 
          echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        else  
          echo "Downloading $dem_name.tif..."
          echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
          aws s3 cp s3://raster/NASADEM/NASADEM_be/$dem_name.tif ./dem_tiff/ --endpoint-url https://opentopography.s3.sdsc.edu --no-sign-request
        fi  
      fi 
    done
  done
  dem_list=$(ls ./dem_tiff/NASADEM_HGT_*.tif)  

####COP-DEM
elif [ $proc_flag == 1 ];then    
  list_lat=$(cat list_lat.txt|sort -d |uniq)
  list_lon=$(cat list_lon.txt|sort -d |uniq)
         
  for id_lat in $list_lat; do 
    for id_lon in $list_lon; do  
      dem_name="Copernicus_DSM_COG_10_"$id_lat"_00_"$id_lon"_00_DEM"
      ## Check the dem 
      flag=$(aws s3 ls s3://copernicus-dem-30m/$dem_name/$dem_name.tif --no-sign-request)
      if [ "$flag"x == "x" ];then
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "The requested CopDEM $dem_name.tif do not exist, please check!"
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"     
      else 
        echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "The CopDEM file $dem_name has been found."
        if [ -f ./dem_tiff/$dem_name.tif ];then
          echo "Skip the downloading of $dem_name.tif as it has already exist!" 
          echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        else  
          echo "Downloading $dem_name.tif..."
          echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
          aws s3 cp s3://copernicus-dem-30m/$dem_name/$dem_name.tif ./dem_tiff/ --no-sign-request
        fi  
      fi
    done
  done
  dem_list=$(ls ./dem_tiff/Copernicus_DSM_*.tif)  
####
else 
 #Check the dem files alreay in the path
  dem_list=$(ls ./dem_tiff/*.tif)   
fi

###Verify the dem files  
if [ "$dem_list"x == "x" ]; then
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  echo "Geotiff files do not exit in $work_path/dem/dem_tiff, please check !" 
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"  
  exit
else 
  echo "$dem_list "
  echo ""
  echo "Downloading of the Geotiff DEM files finished!"  
fi
rm list_*.txt
##########################################################################################
echo $dem_list >dem_list.txt
echo "gdal_merge.py -o dem_merged.tif $dem_list"
gdal_merge.py -o dem_merged.tif $dem_list

if [ $proc_flag == 1 ];then
  #Download the egm08 geoid model 
  echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  echo "Downloading the EGM08 geoid model to correct for the Copernicus DEM datum to WGS84."
  echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  wget -nc https://media.githubusercontent.com/media/insarwxw/proj-datumgrid/master/world/egm08_25.gtx
  
  mv dem_merged.tif dem_merged.tmp0.tif
  gdal_calc.py -A dem_merged.tmp0.tif --outfile=dem_merged.tmp1.tif --calc="numpy.where(A==0,nan,A)"
  gdalwarp -s_srs "+proj=longlat +datum=WGS84 +no_defs +geoidgrids=./egm08_25.gtx" -t_srs "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs" dem_merged.tmp1.tif dem_merged.tmp2.tif
  gdal_calc.py -A dem_merged.tmp2.tif --outfile=dem_merged.tif --calc="numpy.nan_to_num(A,nan=0)"
  rm dem_merged.tmp*.tif
fi

if [ $soft_flag == 0 ]; then
  
  echo "++++++++++++++++++++++++++++++++++++++"
  echo "Prepare the DEM for ISCE processing..."
  echo "++++++++++++++++++++++++++++++++++++++"

  gdal_translate -of ISCE dem_merged.tif $out_name.wgs84
  fixImageXml.py -f -i $out_name.wgs84

elif [ $soft_flag == 1 ]; then

  echo "++++++++++++++++++++++++++++++++++++++"
  echo "Prepare the DEM for GAMMA processing..."
  echo "GAMMA is assumed to be already installed"
  echo "++++++++++++++++++++++++++++++++++++++"
 
   gdal_translate -ot Float32 -of ENVI dem_merged.tif $out_name.en 
   swap_bytes $out_name.en $out_name 4
   
   width=`awk '$1=="samples" {print $3}' $out_name.hdr`
   nlines=`awk '$1=="lines" {print $3}' $out_name.hdr`
   corner_lon=$(cat $out_name.hdr |grep map |awk -F ',' '{print $4}')
   corner_lat=$(cat $out_name.hdr |grep map |awk -F ',' '{print $5}')
   post_lat=$(cat $out_name.hdr |grep map |awk -F ',' '{print $6}')
   post_lat0=$(echo 0 $post_lat |awk '{printf "%.18f", $1-$2}')
   post_lon=$(cat $out_name.hdr |grep map |awk -F ',' '{print $7}')

####### Write the par file for DEM
  if [ -f $out_name.par ];then  rm $out_name.par; fi 
cat <<EOF >> $out_name.par
Gamma DIFF&GEO DEM/MAP parameter file
title: Lisbon-DEM
DEM_projection:     EQA
data_format:        REAL*4
DEM_hgt_offset:          0.00000
DEM_scale:               1.00000
width:                $width
nlines:               $nlines
corner_lat:   $corner_lat   decimal degrees
corner_lon:   $corner_lon   decimal degrees
post_lat:     $post_lat0   decimal degrees
post_lon:     $post_lon   decimal degrees
 
ellipsoid_name: WGS 84
ellipsoid_ra:        6378137.000   m
ellipsoid_reciprocal_flattening:  298.2572236

datum_name: WGS 1984
datum_shift_dx:              0.000   m
datum_shift_dy:              0.000   m
datum_shift_dz:              0.000   m
datum_scale_m:         0.00000e+00
datum_rotation_alpha:  0.00000e+00   arc-sec
datum_rotation_beta:   0.00000e+00   arc-sec
datum_rotation_gamma:  0.00000e+00   arc-sec
datum_country_list Global Definition, WGS84, World
EOF
####################################################
  rasshd $out_name $width 90 90 1 0 - - - - $out_name.bmp 0 1
  rm $out_name.en $out_name.hdr $out_name.en.aux.xml
fi

cd $work_path
######################################################################################## Finish
