import time
import sys

def clusterStatus ():
	cellName = AdminControl.getCell()
	#cell = "/Cell:"+cellName+"/"
	#tempList = AdminConfig.list('ServerCluster', AdminConfig.getid(cell))
	#clusterList = tempList.split("\n")
	for each in clusterList:
		clusterName = AdminConfig.showAttribute(each, 'name')
		#print clusterName
		id = "cell="+cellName+",type=Cluster,name="+clusterName+",*"
		clusterObj = AdminControl.completeObjectName(id)
		#print clusterObj
		status = AdminControl.getAttribute(clusterObj, 'state')
		print clusterName+" : "+status
		clusterA = cell+"ServerCluster:"+clusterName+"/"
		clusterB = AdminConfig.getid(clusterA)
		#print clusterB
		member = AdminConfig.list('ClusterMember', clusterB)
		memberList = member.split("\n")
		#print member
		#print memberList
		for mb in memberList:
			#print mb
			servername = AdminConfig.showAttribute(mb, 'memberName')
			nodeName = AdminConfig.showAttribute(mb, 'nodeName')
			ab = "type=Server,node="+nodeName+",process="+servername+",*"
			serverObject = AdminControl.completeObjectName(ab)
			serverStatus = AdminControl.getAttribute(serverObject, 'state')
			print "	"+servername+" : "+serverStatus
			continue
		continue

clusterStatus()
print "Sleeping for 60 secs"
print time.strftime('%H:%M:%S')
time.sleep(60)
print "60 secs passed"
print time.strftime('%H:%M:%S')
clusterStatus()










		clusterA = cell+"ServerCluster:"+clusterName+"/"
		clusterB = AdminConfig.getid(clusterA)
		#print clusterB
		member = AdminConfig.list('ClusterMember', clusterB)
		memberList = member.split("\n")
		#print member
		#print memberList
		for mb in memberList:
			#print mb
			servername = AdminConfig.showAttribute(mb, 'memberName')
			#print servername
			nodeName = AdminConfig.showAttribute(mb, 'nodeName')
			#print nodeName
			ab = "type=Server,node="+nodeName+",process="+servername+",*"
			#print ab
			serverObject = AdminControl.completeObjectName(ab)
			print serverObject
			serverStatus = AdminControl.getAttribute(serverObject, 'state')
			print "	"+servername+" : "+serverStatus
			return serverStatus
			continue