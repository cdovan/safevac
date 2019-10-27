import time

### COPY THIS ###
from coapthon.client.helperclient import HelperClient
import logging
import re

# Disable logging
logger = logging.getLogger('coapthon')
logger.setLevel(logging.ERROR)

class LocationServer:
    def __init__(self, host, port, groupid, deviceid, tagid):
        self.host = host
        self.port = port
        self.deviceid = deviceid
        self.groupid = groupid
        self.tagid = tagid

        self.client = HelperClient(server = (self.host, self.port))
        payload = "deviceid=" + str(self.deviceid) + "&" + "groupid=" + str(self.groupid) + "&" + "tagid=" + str(self.tagid)
        response = self.client.post("auth/", str(payload))

    def getLocation(self, **kwargs):
        deviceid = kwargs.get('deviceid', None)
        groupid = kwargs.get('groupid', None)
        lastUpdate = kwargs.get('lastUpdate', None)

        response = self.client.get("location?" + (("groupid=" + str(groupid)) if groupid is not None else "") + ("&" if groupid is not None and deviceid is not None else "") + (("deviceid=" + str(deviceid)) if deviceid is not None else "") + ("&" if (groupid is not None or deviceid is not None) and lastUpdate is not None else "") + (("lastUpdate=" + str(lastUpdate)) if lastUpdate is not None else ""))
        result = str(response.payload.strip('[]'))
        result = re.findall("\((.*?)\)", result)
        result = [[x.strip() for x in str(y).split(',')] for y in result]
        return result

    def getNeighbours(self, **kwargs):
        deviceid = kwargs.get('deviceid', None)
        groupid = kwargs.get('groupid', None)
        radius = kwargs.get('radius', None)
        lastUpdate = kwargs.get('lastUpdate', None)

        response = self.client.get("neighbours?" + (("groupid=" + str(groupid)) if groupid is not None else "") + ("&" if groupid is not None and deviceid is not None else "") + (("deviceid=" + str(deviceid)) if deviceid is not None else "") + ("&" if (groupid is not None or deviceid is not None) and radius is not None else "") + (("radius=" + str(radius)) if radius is not None else "") + ("&" if (radius is not None or groupid is not None or deviceid is not None) and lastUpdate is not None else "") + (("lastUpdate=" + str(lastUpdate)) if lastUpdate is not None else ""))
        result = str(response.payload.strip('[]'))
        result = re.findall("\((.*?)\)", result)
        result = [[x.strip() for x in str(y).split(',')] for y in result]
        return result

### Do not edit this ###
host = "192.168.0.5"
port = 5683
path = "basic"
###

### Do edit this ###
groupid = 2
server_id = 0
server_tagid = -1
###

class LocationRequester:
    def __init__(self):
        self.location_server = LocationServer(host, port, groupid, server_id, server_tagid)
        self.devices = []
    
    def register_device(self, tagid):
        LocationServer(host, port, groupid, tagid, tagid)
        self.devices.append(tagid)
    
    def request_locations(self):
        device_query = (",").join(str(d) for d in self.devices)
        results = self.location_server.getLocation(groupid=groupid, deviceid=device_query)
        locations = {}

        for data in results:
            deviceid = data[1]
            x = data[4]
            y = data[5]
            locations[deviceid] = { "x": x, "y": y }
        
        return locations