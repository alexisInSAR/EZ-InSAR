Digital Elevation Models
========================

Several sources of digital elevation models are available with EZ-InSAR. 

.. note::

    Before running this tool you have to install the AWS CLI tool. Check the installation of AWS at https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html. For example, use the following commands to install aws on a linux OS. 

    .. code:: bash

        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install

SRTM
----

Conventional SRTM DEM. 

+--------+----------------------+----------------------------+
| Source | EZ-InSAR typeDEM key | Username/Password required |
+========+======================+============================+
| None   | SRTM and SRTM-ell    | No                         |
+--------+----------------------+----------------------------+

NASADEM
-------

The NASADEM and NASADEM-ell keys corresponds to the reprocessed SRTM DEM by NASA. See https://earthdata.nasa.gov/esds/competitive-programs/measures/nasadem for more details. 

+-----------------------------+-------------------------+----------------------------+
| Source                      | EZ-InSAR typeDEM key    | Username/Password required |
+=============================+=========================+============================+
| https://opentopography.org/ | NASADEM and NASADEM-ell | No                         |
+-----------------------------+-------------------------+----------------------------+

Copernicus DEM
--------------

The Copernicus corresponds to the reprocessed Copernicus DEM by ESA. See https://spacedata.copernicus.eu/web/cscda/dataset-details?articleId=394198 for more details. 

+------------------------------+--------------------------------+----------------------------+------------+
| Source                       | EZ-InSAR typeDEM key           | Username/Password required | Resolution |
+==============================+================================+============================+============+
|| https://opentopography.org/ || Copernicus and Copernicus-ell || No                        || 30 m      |
|| Copernicus Data Space       || COPDEM30 and COPDEM30-ell     || Yes                       || 30 m      |
|| Copernicus Data Space       || COPDEM90 and COPDEM90-ell     || Yes                       || 90 m      |
+------------------------------+--------------------------------+----------------------------+------------+

ALOS Global Digital Surface Model
---------------------------------

The ALOS Global Digital Surface Model ALOS World 3D - 30m (AW3D30) is a global DEM (c. 30-m spatial resolution, basically 1 arcsecond) by the Panchromatic Remote-sensing Instrument for Stereo Mapping (PRISM). This dataset requires an account (and a registration). Please see https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm. Please use the options username and password. 

+-------------+-----------------------+----------------------------+
| Source      | EZ-InSAR typeDEM key  | Username/Password required |
+=============+=======================+============================+
| JAXA server | AW3D30 and AW3D30-ell | Yes                        |
+-------------+-----------------------+----------------------------+

RGE ALTI®
---------

RGE ALTI® is the French Lidar DEM at high spatial resolution. Its coverage is the French territories. 

+-------------------------------------+----------------------+----------------------------+------------+
| Source                              | EZ-InSAR typeDEM key | Username/Password required | Resolution |
+=====================================+======================+============================+============+
|| https://geoservices.ign.fr/rgealti || RGEALTI-1m          || No                        || 1 m       |
|| https://geoservices.ign.fr/rgealti || RGEALTI-5m          || No                        || 5 m       |
+-------------------------------------+----------------------+----------------------------+------------+

Personal DEM
------------

The EZ-InSAR is able to import any DEM with the *perso* typeDEM key. 

                