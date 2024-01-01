function splitTSXPAZdualpolheader(xmlint,xmlout,pol)
%   splitTSXPAZdualpolheader(src,evt,action,miesar_para)
%       [xmlint]           : callback value
%       [xmlout]           : callback value
%       [pol]        : name of the action to perform (string value)
%
%       Function to manage the dual-polarisation images from TSX and PAZ.
%
%       Script from EZ-InSAR toolbox: https://github.com/alexisInSAR/EZ-InSAR
%
%   See also createlistSLC, GUIpathdirectory, displayextensionS1, initparmslc, readxmlannotationS1, displayextensionTSXPAZ, manageparamaterSLC, downloaderSLC, manageSLC.
%
%   -------------------------------------------------------
%   Alexis Hrysiewicz, UCD / iCRAG
%   Version: 2.1.1 Beta
%   Date: 16/10/2023
%
%   -------------------------------------------------------
%   Version history:
%           2.1.1 Beta: Initial (unreleased)


% Comment: 
% The seperation of polarisation-related layers is very complex if the use
% of automatic algorithm is desired. The first option is to manually script
% the wanted and desired part from the .xml header file. 

%% Read the xml file
xmldata = xml2struct(xmlint);

%% Read the idx of the polarisation layer
idx_pol = 0; 
nb_layer = length(xmldata.level1Product.productInfo.acquisitionInfo.polarisationList.polLayer); 
for i1 = 1 : length(xmldata.level1Product.productInfo.acquisitionInfo.polarisationList.polLayer)
    if strcmp(xmldata.level1Product.productInfo.acquisitionInfo.polarisationList.polLayer{i1}.Text,pol)
        idx_pol = i1; 
    end 
end 

if idx_pol == 0
    error('')
end 

%% Remove the other polarisation layer
xmldata.level1Product.productComponents.imageData(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.productComponents.imageData{1}.Attributes.layerIndex = '1'; 

xmldata.level1Product.productComponents.quicklooks(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.productComponents.quicklooks{1}.Attributes.layerIndex = '1';

xmldata.level1Product.productInfo.acquisitionInfo.polarisationList.polLayer(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.productInfo.imageDataInfo.numberOfLayers.Text = '1'; 

xmldata.level1Product.setup.orderInfo.polList.polLayer(setdiff(1:nb_layer,idx_pol)) = [];

xmldata.level1Product.processing.doppler.dopplerCentroid(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.processing.doppler.dopplerCentroid{1}.Attributes.layerIndex = '1';
xmldata.level1Product.processing.processingParameter.correctedInstrumentDelay(setdiff(1:nb_layer,idx_pol)) = [];

xmldata.level1Product.instrument.settings(setdiff(1:nb_layer,idx_pol)) = [];

xmldata.level1Product.calibration.calibrationData.numberOfAntennaPatterns.Text = '1'; 
xmldata.level1Product.calibration.calibrationData.antennaPattern(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.calibration.calibrationData.calibrationInfoAndInstrumentCharacteristics.absCalFactor(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.calibration.calibrationData.calibrationInfoAndInstrumentCharacteristics.totalInstrumentTimeDelay.internalDelay(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.calibration.calibrationConstant(setdiff(1:nb_layer,idx_pol)) = [];

xmldata.level1Product.noise(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.noise{1}.Attributes.layerIndex = '1'; 

xmldata.level1Product.productQuality.rawDataQuality(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.productQuality.imageDataQuality(setdiff(1:nb_layer,idx_pol)) = [];
xmldata.level1Product.productQuality.imageDataQuality{1}.Attributes.layerIndex = '1'; 

%% Write the new header
struct2xml(xmldata,xmlout)