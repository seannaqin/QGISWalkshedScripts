from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination)
from qgis import processing

import os

### This class uses the QGIS ExampleProcessingAlgorithm as a base
### https://docs.qgis.org/3.34/en/docs/user_manual/processing/scripts.html#extending-qgsprocessingalgorithm

## Run script in QGIS
## Input file specified in popup is ignored, but a file must be inserted to run the script
class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        return 'CreateBuffers'

    def displayName(self):
        return self.tr('Create Buffers')

    def group(self):
        return self.tr('Personal Script')

    def groupId(self):
        return 'PersonalScript'

    def shortHelpString(self):
        return self.tr("Create buffers for multiple files")

    def initAlgorithm(self, config=None):

        # Add the input vector features source with any geometry
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ## Change the directories to input and output file folder locations
        ## Naming convention assumes each input file begins with "RP "
        ## Naming convention produces each output file to begin with "Buffer "
        # Assign directories
        dir_input = r"C:\QGIS Projects\Walkshed Sim\Amenities"
        dir_output = r"C:\QGIS Projects\Walkshed Sim\Buffered Amenities"

        # Iterate over files in directory
        for name in os.listdir(dir_input):
            
            # Determine file extension - must be geojson
            file_name, file_ext = os.path.splitext(name)
            if file_ext == ".geojson":

                """
                # Determine file projection
                with open(dir_input + "\\" + name, 'r') as file:
                    data = json.load(file)

                crs = data.get('crs', {})
                crs_properties = crs.get('properties', {})

                epsg_name = crs_properties.get('name', '')
                epsg_code = ""
                if 'urn:ogc:def:crs:EPSG::' in epsg_name:
                    epsg_code = epsg_name.split('::')[-1]
                
                if epsg_code == "32610":
                    # Run buffer script
                """


                # Run buffer script
                outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
                buffered_layer = processing.runAndLoadResults("native:buffer", {
                    'INPUT': dir_input + "\\" + name, # name example: RP Joined Burbridge Library.geojson
                    'DISTANCE': 10, # units in meters for EPSG:32610, note units differ depending on projection
                    'SEGMENTS': 5,
                    'END_CAP_STYLE': 0,
                    'JOIN_STYLE': 0,
                    'MITER_LIMIT': 2,
                    'DISSOLVE': False, # True for walksheds, False for amenities
                    'OUTPUT': dir_output + "\\Buffer" + name[2:] # [2:] because of naming convention, deleting "RP"
                })['OUTPUT']


        # Return the results of the algorithm
        return {self.OUTPUT: buffered_layer}