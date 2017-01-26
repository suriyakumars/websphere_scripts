################################################################################
# AddSharedLibrary.py
#  -script does the shared library configuration for managed cell
#  -library artifacts are read from SharedLibSetup.properties file
#  -
################################################################################
import sys, os, os.path, shutil
import java.util
import java.io
import java.lang

#declare global variables
aDict = {}
cell = AdminControl.getCell()
libPath = ''
listOfServers = []
libName = 'MODULE_LIB_PATH'
global userInstallRoot

## global java.util.Properties variable
props = None
fileList = None
fs = None

################################################################################
# init(sType)
#  initialize server libraries based on type (dmgr, standalone, cluster)
################################################################################
def init(sType):
  if (sType == 'dmgr') :
    return '${USER_INSTALL_ROOT}/module-libraries'
  if (sType=='standalone'):
    return '${USER_INSTALL_ROOT}/config/cells/' + cell+'/nodes/%s/servers/%s/module-libraries'
  else:
  	return '${USER_INSTALL_ROOT}/config/cells/'+cell+'/clusters/%s/module-libraries'
  
################################################################################
# findUserInstallRoot()
#  returns USER_INSTALL_ROOT defined for specified scope
################################################################################
def findUserInstallRoot():
  dmgr = AdminControl.queryNames('type=DeploymentManager,*')
  dmgr = dmgr[dmgr.find("node="):]
  dmgr = dmgr[:dmgr.find(",")]
  dmgr = dmgr[dmgr.find("=")+1:] 
  d = dmgr
  dmgr = AdminConfig.getid('/Node:'+dmgr+'/')
  varMap = AdminConfig.list("VariableMap", dmgr).splitlines()[0]
  dmgrEntries = AdminConfig.showAttribute(varMap, "entries")
  entryList = wsadminToList(dmgrEntries)
  for entry in entryList:
    if (AdminConfig.showAttribute(entry, "symbolicName") == 'USER_INSTALL_ROOT'):
      return AdminConfig.showAttribute(entry, "value")
#endDef

################################################################################
# getWPSHome()
#  returns WAS_INSTALL_ROOT value defined for the cell
################################################################################
def getWPSHome():
  dmgr = AdminControl.queryNames('type=DeploymentManager,*')
  dmgr = dmgr[dmgr.find("node="):]
  dmgr = dmgr[:dmgr.find(",")]
  dmgr = dmgr[dmgr.find("=")+1:] 
  d = dmgr
  dmgr = AdminConfig.getid('/Node:'+dmgr+'/')
  varMap = AdminConfig.list("VariableMap", dmgr).splitlines()[0]
  dmgrEntries = AdminConfig.showAttribute(varMap, "entries")
  entryList = wsadminToList(dmgrEntries)
  for entry in entryList:
    if (AdminConfig.showAttribute(entry, "symbolicName") == 'WAS_INSTALL_ROOT'):
      return AdminConfig.showAttribute(entry, "value")
#endDef

################################################################################
# wsadminToList(inStr)
#  helper function that converts wsadmin output lists to standard Python lists
################################################################################
def wsadminToList(inStr):
	outList=[]
	if (len(inStr)>0 and inStr[0]=='[' and inStr[-1]==']'):
		tmpList = inStr[1:-1].split(" ")
	else:
		tmpList = inStr.split("\n")  #splits for Windows or Linux
	for item in tmpList:
		item = item.rstrip()	      #removes any Windows "\r"
		if (len(item)>0):
			outList.append(item)
	return outList
#endDef

################################################################################
# createSharedLibrary()
#  creates a WebSphere Shared Library under Environment > Shared Libraries
#  called 'ModuleSharedLibraries'.
################################################################################
def createSharedLibrary():
  ##Create Shared Library for each server in cluster
  libraries = AdminConfig.list("Library")
  #print "Checking if shared library defined cell"
  if libraries.find('ModuleSharedLibraries') != -1:
    #print "Shared library already configured for cell %s" %cell
    return
  #Create Shared Library
  #print 'Creating shared library for cell %s' %cell
  cellID = AdminConfig.getid('/Cell:'+cell+'/')
  AdminConfig.create('Library', cellID, [['name', 'ModuleSharedLibraries'], ['classPath', '${'+libName+'}']])
  #print 'Shared library created.'
#endDef

################################################################################
# clusters()
#  configures each cluster for shared libraries
#   -this can be modified to handle only the clusters that are needed
#   -creates MODULE_LIB_PATH variable for cluster
#   -creates 'module-libraries' directory under dmgr 'config' tree for each cluster name
#   -copies .jar files to 'module-libraries' folder
################################################################################
def clusters():
  global userInstallRoot
  found = 0
  libPath=init('cluster')
  #print "Finding clusters"
  clusters = AdminConfig.getid('/ServerCluster:/').splitlines()
  listOfServers.append('nodeagent')
  for cluster in clusters:
  	#consider adding Property variable to list clusters/servers to modify
    #if (clusters.find('%CLUSTER_NAME%') < 0):
    #	continue
    c = cluster[:cluster.find('(')]
    varSubstitutions = AdminConfig.list("VariableSubstitutionEntry",cluster).splitlines()
    #print "Checking if MODULE_LIB_PATH exists in cluster %s" %c 
    for varSubst in varSubstitutions:
      getVarName = AdminConfig.showAttribute(varSubst, "symbolicName")
      if getVarName == libName:
        found = 1
        break
    if(found == 1):
      #print "MODULE_LIB_PATH variable aready exists in cluster %s.  Skipping."  % c
      for server in AdminConfig.list("ClusterMember", cluster).splitlines():
        listOfServers.append(server[:server.find('(')])
	uLibPath = (libPath.replace("${USER_INSTALL_ROOT}", userInstallRoot).replace("/", os.sep))
	copyToConfig(uLibPath %c)    
      continue

    #Create WebSphere Variable
    varMap = AdminConfig.list("VariableMap", cluster).splitlines()[0]
    attrs = [["symbolicName", libName], ["value", libPath % c ]]
    AdminConfig.create("VariableSubstitutionEntry", varMap, attrs)
    #print "Created MODULE_LIB_PATH variable for cluster %s" %c
    #Created Shared Library for each server in cluster
    clusterMembers= AdminConfig.list("ClusterMember", cluster).splitlines()
    for server in clusterMembers:
      server = server[:server.find('(')]
      #print "Now creating directories"
      uLibPath = (libPath.replace("${USER_INSTALL_ROOT}", userInstallRoot).replace("/", os.sep))
      
			#create 'module-libraries' directory
      mkfolder(uLibPath %c)
      #copy files here to cluster 'module-libraries'
      copyToConfig(uLibPath %c)
      
      listOfServers.append(server)
      #create and configure classloader
      #print 'Creating and configuring the classloader for %s' %server
      serverID = AdminConfig.getid('/Server:'+server+'/')
      appServer = AdminConfig.list('ApplicationServer', serverID)
      classLoad = AdminConfig.showAttribute(appServer, 'classloaders')
      cleanClassLoaders = classLoad[1:len(classLoad)-1]
      classLoader1 = cleanClassLoaders.split(' ')[0]
      classLoader1 = AdminConfig.create('Classloader', appServer, [['mode',  'PARENT_FIRST']])
      z = AdminConfig.create('LibraryRef', classLoader1, [['libraryName', 'ModuleSharedLibraries'],  ['sharedClassloader', 'true']])
      #print 'Classloader created and configured for %s.  Saving configuration...' %server
      AdminConfig.save()
#endDef

################################################################################
# fsas()
#  configures each *federated* standalone server
#  servers must be managed by a deployment manager for this to work
#  currently this will modify all federated servers in the cell
#   -this can be modified to handle only the servers that are needed
#   -creates MODULE_LIB_PATH variable for server
#   -creates 'module-libraries' directory under dmgr 'config' tree for each server name
#   -copies .jar files to 'module-libraries' folder
################################################################################
##Move on to federated stand-alone servers
def fsas():
  global userInstallRoot
  found = 0
  libPath = init('standalone')
  #print 'Finding list of federated stand-alone servers...'
  for server in AdminConfig.list("Server").splitlines():
    s = server[:server.find('(')]
    if s not in listOfServers:
      #print "Found server %s.  Checking if MODULE_LIB_PATH variable exists." %s
      varSubstitutions = AdminConfig.list("VariableSubstitutionEntry",server).splitlines()
      for varSubst in varSubstitutions:
        getVarName = AdminConfig.showAttribute(varSubst, "symbolicName")
        if getVarName == libName:
          found = 1
          break
      if(found == 1):
        #print "MODULE_LIB_PATH variable already exists on " + s
        continue   
    ##Create WAS Variable
      #print "Creating variable for server %s" %s
      varMap = AdminConfig.list("VariableMap", server).splitlines()[0]
      node = server[server.find('nodes')+6:server.find("/servers")]
      attrs = [["symbolicName", libName], ["value", libPath %(node,s)]]
      AdminConfig.create("VariableSubstitutionEntry", varMap, attrs)
      #print "Created MODULE_LIB_PATH variable for server %s.  Now making directory" %s
      serverEntries = AdminConfig.showAttribute(varMap, "entries")
      uLibPath = (libPath.replace("${USER_INSTALL_ROOT}", userInstallRoot).replace("/", os.sep))

      #create 'module-libraries' directory
      mkfolder(uLibPath %(node,s))
      
      #print 'Removing the existing jars'
            
      removeFromConfig(uLibPath %(node,s))
      
      #copy files here to cluster 'module-libraries'
      
      #print 'copying the shared jars'
      copyToConfig(uLibPath %(node,s))
      
      serverID = AdminConfig.getid('/Server:'+s+'/')
      #print 'Creating and configuring the classloader for %s' %s
      appServer = AdminConfig.list('ApplicationServer', serverID)
      #create and configure classloader
      classLoad = AdminConfig.showAttribute(appServer, 'classloaders')
      cleanClassLoaders = classLoad[1:len(classLoad)-1]
      classLoader1 = cleanClassLoaders.split(' ')[0]
      classLoader1 = AdminConfig.create('Classloader', appServer, [['mode',  'PARENT_FIRST']])
      z = AdminConfig.create('LibraryRef', classLoader1, [['libraryName', 'ModuleSharedLibraries'],  ['sharedClassloader', 'true']])
      #print 'Classloader created and configured for %s.  Saving configuration...' %s
      AdminConfig.save()
      listOfServers.append(s)
    elif server in listOfServers:
      continue
#endDef

################################################################################
# mkfolder(folder)
#  creates the specified folder
#  this is OS-independent--should work for both Windows and Posix environments
################################################################################
def mkfolder(folder):
  if(os.path.isdir(folder)==0):
    print "Creating directory " + folder
    #status = java.io.File(folder).mkdir()
    os.mkdir(folder)
  else:
    print "Directory already exists:  " + folder
#endDef

################################################################################
# sync()
#  synchronizes all nodes in the cell
#  after synchronization, all nodes should have 'module-libraries'
################################################################################
def sync():
  	cellName = AdminControl.getCell()
	#print "Cell : " + cellName
	cellId = AdminConfig.getid("/Cell:"+cellName+"/")
	
	#print "sync: Start synchronizing nodes...... " 
	nodes = AdminConfig.list("Node", cellId)
	if len(nodes) == 0:
	   print "  There is no node in " + cellName 

	nodesList = nodes.split(lineSeparator)
	for node in nodesList:
        	nodeName = AdminConfig.showAttribute(node, "name")
        	refreshRepo = AdminControl.completeObjectName("type=ConfigRepository,process=nodeagent,node=" + nodeName + ",*" )
        	if len(refreshRepo) != 0:
			AdminControl.invoke(refreshRepo, "refreshRepositoryEpoch" )
		 	
	        nodeSync = AdminControl.completeObjectName("type=NodeSync,node=" + nodeName + ",*")
	        if len(nodeSync) != 0:
                #print "sync: Synchronizing node: " + nodeName
		        #print "sync: Node Sync: " + nodeSync
					AdminControl.invoke(nodeSync, 'sync')

	print "Synchronisation completed"
#endDef

################################################################################
# readProperties(fileName)
#  reads the specified java.util.Property file, and loads fields to 'props' global var
################################################################################
def readProperties(fileName):
	global props
	props = java.util.Properties()
	f = java.io.FileInputStream(fileName)
	props.load(f)
	return
#endDef

################################################################################
# getSharedLibFileNames()
#  loads the reads the specified java.util.Property file, and loads fields to 'props' global var
#  assumes that file names in "LIBRARY_JARS" are space-delimited, but can be modified to handle any delimiter
################################################################################
def getSharedLibFileNames():
	global props
	fileNames = props.getProperty("LIBRARY_JARS").strip()
	return fileNames.split()
#endDef

################################################################################
# removeFromLibExt()
#  removes .jar files from lib/ext after application install
################################################################################
def removeFromLibExt():
	# delete files from lib/ext (only used after app install)
	global props, fileList, fs, userInstallRoot
	i = 0
	while i < len(fileList):
		#print 'del "' + getWPSHome() + '/lib/ext' + fs  + fileList[i] + '"'
		os.remove(getWPSHome()  + '/lib/ext' + fs + fileList[i])
		i = i+1 
	#endWhile
#endDef

################################################################################
# copyToLibExt()
# copy library .jar files to dmgr lib/ext
################################################################################
def copyToLibExt():
	global props, fileList, fs, userInstallRoot
	i = 0
	while i < len(fileList):
		shutil.copy(props.getProperty("SOURCE_FILE_PATH") + fs + fileList[i], getWPSHome() + "/lib/ext")
		i = i+1
	#endWhile
#endDef

################################################################################
# copyToConfig(filePath)
#  copy library .jar files to specific 'module-libraries' directory in config tree
################################################################################
def copyToConfig(filePath):
	#print 'copying the libraies to below location'
	global props, fileList, fs
	i = 0
	while i < len(fileList):
		#os.system('copy "' + props.getProperty("SOURCE_FILE_PATH") + fs + fileList[i] + '" "' + filePath + '"')
		#print filePath
		shutil.copy(props.getProperty("SOURCE_FILE_PATH") + fs + fileList[i], filePath)
		i = i+1
	#endWhile
#endDef


################################################################################
# copyToConfig(filePath)
#  copy library .jar files to specific 'module-libraries' directory in config tree
################################################################################
def removeFromConfig(filePath):
	print 'Insider removeFrom Config'
	global props, fileList, fs
	i = 0
	while i < len(fileList):
		#os.system('copy "' + props.getProperty("SOURCE_FILE_PATH") + fs + fileList[i] + '" "' + filePath + '"')
		print filePath
		os.remove(filePath + fs + fileList[i])
		i = i+1
	#endWhile
#endDef


################################################################################
################################################################################
# Run script

readProperties("properties/SharedLibSetup.properties")
#store shared lib file names in fileList global var
fileList = getSharedLibFileNames()

#set OS-specific file separator ('/' for Posix, '\' for Windows)
fs = java.lang.System.getProperty("file.separator")

userInstallRoot = findUserInstallRoot()
createSharedLibrary()

#copy jars to dmgr lib/ext
#copyToLibExt()

#configure all clusters
clusters()

#there are no federated standalone servers in this case, so no need to call fsas()
#fsas()

#synchronize all nodes in the cell after shared library configuration is complete
sync()
