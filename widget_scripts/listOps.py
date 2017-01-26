import sys

def listApp():
	applist = AdminApp.list().split("\n")
	print "Deployed Applications are : "
	for a in applist:
		print a
		continue
#endDef

def listServers(nodeName):		
	slist = []
	print "Available Servers are : "
	for n in nodeName:
		plist = "[-serverType APPLICATION_SERVER -nodeName " + n + "]"
		#print plist
		slist.append(AdminTask.listServers(plist).split("\n"))
		#print slist
	#
	for s in slist:
		for a in s:
			new = a.split("(")
			print new[0]
	  #print s
			continue
#endDef

def synchNode():
	nodelist = AdminConfig.list('Node').split("\n")
	#print nodelist
	print "Synchronising with the nodes"

	for n in nodelist:
		nodename = AdminConfig.showAttribute(n, 'name')
		#print nodename
		objname = "type=NodeSync,node=" + nodename + ",*"
		#print objname
		Syncl = AdminControl.completeObjectName(objname)
		if Syncl != "":
			AdminControl.invoke(Syncl, 'sync')
			print "Done with node " + nodename
		else:
			print "Skipping node " + nodename
		continue
#endDef

#Script execution starts here

listApp()

listServers('test')

synchNode()
