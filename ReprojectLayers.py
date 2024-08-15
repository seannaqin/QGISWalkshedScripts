#native:reprojectlayer -> Reproject layer
#processing.runAndLoadResults("native:reprojectlayer", {'INPUT': 'C:\QGIS Projects\Reproject test\Walksheds39024.json', 
										 #'TARGET_CRS': 'ESPG:32610 - WGS 84 / UTM zone 10N', 
										 #'CONVERT_CURVED_GEOMETRIES': 0,
										 #'OUTPUT': 'C:\QGIS Projects\Reproject test\ReprojectTestWalkshed.json'})

## This script does not reproject files to EPSG:32610
## This script correctly reprojects files to EPSG:3031 (the only other projection tested)

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination)
from qgis import processing

import os

## Run script in QGIS
## Input layer specified in popup is ignored, but a layer must be inserted to run the script
class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        return 'ReprojectLayers'

    def displayName(self):
        return self.tr('Reproject Layers')

    def group(self):
        return self.tr('Personal Script')

    def groupId(self):
        return 'PersonalScript'

    def shortHelpString(self):
        return self.tr("Reprojects layer to ESPG:32610")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ## Change the directories to input and output file folder locations
        # Assign directory
        dir_input = r"C:\QGIS Projects\Test"
        dir_output = r"C:\QGIS Projects\Reproject test"

        # Iterate over files in directory
        for name in os.listdir(dir_input):
            
            # Determine file extension - must be geojson
            file_name, file_ext = os.path.splitext(name)
            if file_ext == ".geojson":

                # Run reproject layer script
                outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
                reprojected_layer = processing.runAndLoadResults("native:reprojectlayer", {
					'INPUT': dir_input + "\\" + name, 
					'TARGET_CRS': 'EPSG:3031', # 'EPSG:32610', 'EPSG::32610', '32610' all did not work
					'CONVERT_CURVED_GEOMETRIES': 0,
					'OUTPUT': dir_output + "\\RP " + name})['OUTPUT']
                


        # Return the results of the algorithm
        return {self.OUTPUT: reprojected_layer}
