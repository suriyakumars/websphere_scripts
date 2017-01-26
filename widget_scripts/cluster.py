#################### This script can be used to start / stop / get status of one or more webserver(s) ###############################
#
# Author: Suriyakumar Subramanian
# Date: 09/02/2010
# USAGE: <WAS_PATH>/wsadmin.sh -f <path/cluster.py> <start|stop|status> <cluster_name1,cluster_name2,...>
# USAGE Example: 
####################################################################################################

import sys

opType = sys.argv[0]
clusterNames = sys.argv[1]

#Setting global variables
stopStatusArray = []
startStatusArray = []
cellName = AdminControl.getCell()

#Checks the status of the given cluster
def clusterStatus(clusterName):
	cell = "/Cell:"+cellName+"/"
	logger("Checking status for the cluster "+clusterName)
	id = "cell="+cellName+",type=Cluster,name="+clusterName+",*"
	#print id
	clusterObj = AdminControl.completeObjectName(id)
	#print clusterObj
	clusterState = AdminControl.getAttribute(clusterObj, 'state')
	clusterState = clusterState.split(".")
	clusterState = clusterState[2]
	#print clusterName+" : "+clusterState
	if (clusterState == "running"):
		logger("Cluster "+clusterName+" is in started status")
		return "running"
	elif (clusterState == "stopped"):
		logger("Cluster "+clusterName+" is in stopped status")
		return "stopped"
	else:
		logger("Cluster "+clusterName+" is in partial status")
		return "partial"

#Checks the status of the given clusters and interprets the results for START status
def checkClusterStatus(clusterValues):
	for cluster in clusterValues:
		status = clusterStatus(cluster)
		continue

#Stops the given cluster
def stopCluster(clusterName):
	logger("Stopping cluster "+clusterName)
	obj = "cell="+cellName+",type=Cluster,name="+clusterName+",*"
	#print obj
	clusterObj = AdminControl.completeObjectName(obj)
	doServerAction("stop", clusterObj)
	logger("Cluster stop command initiated")

#Stops the given clusters
def stopClusters(clusterValues):
	for cluster in clusterValues:
		stopCluster(cluster)
		continue

#Starts the given cluster
def startCluster(clusterName):
	logger("Starting cluster "+clusterName)
	obj = "cell="+cellName+",type=Cluster,name="+clusterName+",*"
	#print obj
	clusterObj = AdminControl.completeObjectName(obj)
	doServerAction("start", clusterObj)
	logger("Cluster start command initiated")

#Starts the given clusters
def startClusters(clusterValues, stopStatus):
	for cluster in clusterValues:
		startCluster(cluster)
		continue

def doServerAction(action, clusterObj):
	AdminControl.invoke(clusterObj, action)

#Script execution starts here ----------------------------------
clusterList = []
clusterNames=clusterNames.split(",")
for each in clusterNames:
	clusterList.append(each)
	continue

if (opType == "status"):
	
	checkClusterStatus (clusterList)

elif (opType == "stop"):

	stopClusters (clusterList)
	
elif (opType == "start"):
	
	startClusters (clusterList)
	
else:
	print "Please provide a valid Operation Type (status | start | stop)"

#Script execution ends here ----------------------------------
