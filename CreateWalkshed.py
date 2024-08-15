import json, random
from urllib.request import urlopen
from urllib.error import HTTPError

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsVectorLayer,
                       QgsProject,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterPoint)
from qgis import processing

### This class is derived from the "ReachableTree" script by TCAT
### The "ReachableTree" script has been edited to automize walkshed creation and identify walksheds by name

## Run script in QGIS
## Input any point in popup panel - the walkshed from that point will 
#  not be created and will produce an error that can be ignored
class AccessMapTreeProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AccessMapTreeProcessingAlgorithm()

    def name(self):
        return 'ReachableTree'

    def displayName(self):
        return self.tr('Reachable Tree')

    def group(self):
        return self.tr('AccessMap')

    def groupId(self):
        return 'AccessMap'

    def shortHelpString(self):
        return self.tr("Reachable Tree from a specific point")

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterPoint(
            "POINT", "Point"))

        self.addParameter(QgsProcessingParameterNumber(
            "UPHILL", "Uphill",
            QgsProcessingParameterNumber.Double,
            0.08,
            minValue = 0.0,
            maxValue = 1.0))
            
        self.addParameter(QgsProcessingParameterNumber(
            "DOWNHILL", "Downhill",
            QgsProcessingParameterNumber.Double,
            0.1,
            minValue = 0.0,
            maxValue = 1.0))
            
        self.addParameter(QgsProcessingParameterBoolean(
            "AVOIDCURBS", "Avoid Curbs",
            defaultValue=True))
            
        self.addParameter(QgsProcessingParameterNumber(
            "STREETAVOIDANCE", "Street Avoidance",
            QgsProcessingParameterNumber.Double,
            1,
            minValue = 0.0,
            maxValue = 1.0))
            
        self.addParameter(QgsProcessingParameterNumber(
            "MAXCOST", "Max Cost",
            QgsProcessingParameterNumber.Double,
            1000.0))
            
        self.addParameter(QgsProcessingParameterBoolean(
            "REVERSE", "Reverse Walkshed",
            defaultValue=False))

    def processAlgorithm(self, parameters, context, feedback):

        def reachable_tree(lon, lat, uphill, downhill, avoidCurbs, streetAvoidance, max_cost, reverse, name, profile):
            url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/reachable_tree/custom.json?lon='+str(lon)+'&lat='+str(lat)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&max_cost='+str(max_cost)
            
            ## Change downloaded_file_prefix to file folder location
            downloaded_file_prefix = 'C:\QGIS Projects\Walksheds'
            ## Can change name of download files to be identifiable (similar to layer_name variables)
            downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

            layer_name = name + ' RT ' + profile
            layer_name2 = name + ' Cost ' + profile
            layer_name3 = name + ' Origin ' + profile

            try:
                r = urlopen(url)
            except HTTPError as e:
                if e.code == 422:
                    feedback.pushInfo('Validation error: ' + e.read().decode())
                    return
                else:
                    raise e
            
            data = json.loads(r.read())

            if not "edges" in data:
                feedback.pushInfo('No results were returned from AccessMap: ' + str(data))
                return
                
            with open(downloaded_file, 'w', encoding='utf-8') as f:
                json.dump(data["edges"], f)

            with open(downloaded_file2, 'w', encoding='utf-8') as f:
                json.dump(data["node_costs"], f)

            with open(downloaded_file3, 'w', encoding='utf-8') as f:
                json.dump(data["origin"], f)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file, layer_name, "ogr")
            layer.renderer().symbol().setWidth(1)
            #layer.renderer().symbol().setColor(QColor.fromRgb(255, 0, 0))
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file2, layer_name2, "ogr")
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file3, layer_name3, "ogr")
            layer.renderer().symbol().symbolLayer(0).setSize(6)
            layer.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            QCoreApplication.processEvents()



        ## Set up location and mobility profile variables
        place = ["Kirkland", "MaryPilgrim", "Redmond", "SacredMed", "SalmonberryL", "SidneyWilson"]
        person = ["Control", "Walking", "Cane", "Powered", "Manual"]
        long = [-122.199038, -122.345688, -122.136845, -122.292986, -122.330440, -122.233181]
        lati = [47.642723, 47.731363, 47.629664, 47.732567, 47.601212, 47.469499]
        up = [0.15, 0.15, 0.14, 0.12, 0.08]
        down = [0.15, 0.15, 0.14, 0.12, 0.1]
        curb = [0, 0, 0, 1, 1]
        street = [0, 1, 1, 1, 1]

        # Loop through each HTH location
        for loc in range(len(place)):
            # Loop through each mobility profile
            for prof in range(len(person)):
                # Call method to create walkshed
                reachable_tree(lon=long[loc],
                    lat=lati[loc],
                    uphill=up[prof],
                    downhill=down[prof],
                    avoidCurbs=curb[prof],  # avoidCurbs = 0 means unchecked
                    streetAvoidance=street[prof],
                    max_cost=900,
                    reverse=0,
                    name=place[loc],
                    profile=person[prof])




        originPoint = self.parameterAsPoint(parameters, "POINT", context)
        reachable_tree(lon=originPoint.x(),
            lat=originPoint.y(),
            uphill=parameters["UPHILL"],
            downhill=parameters["DOWNHILL"],
            avoidCurbs=parameters["AVOIDCURBS"],
            streetAvoidance=parameters["STREETAVOIDANCE"],
            max_cost=parameters["MAXCOST"],
            reverse=parameters["REVERSE"])
        
        return {self.OUTPUT: None}
    