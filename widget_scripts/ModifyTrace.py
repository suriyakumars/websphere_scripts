processList = <>
configProcessList = <>

#runTimeAction='display'
runTimeAction='modify'
saveConfig='true'
newTraceString=sys.argv[0]

# Set Runtime tracing
for processStr in processList:
	process=AdminControl.queryNames(processStr)
        print "Trace String for " + processStr + " " + AdminControl.getAttribute(process,'traceSpecification')
        if (runTimeAction == 'modify'):     	
        	AdminControl.setAttribute(process,'traceSpecification',newTraceString)
        	print "Trace String for " + processStr + " changed to " + AdminControl.getAttribute(process,'traceSpecification')

# Set Configuration tracing
if (saveConfig == 'true'):
	for configProcessStr in configProcessList:
		configProcess=AdminConfig.getid(configProcessStr)
		print "Trace String in Configuration for " + configProcessStr + " before change is " + AdminConfig.showAttribute(configProcess,'startupTraceSpecification')
		AdminConfig.modify(configProcess,[['startupTraceSpecification',newTraceString]])
		print "Trace String in Configuration for " + configProcessStr + " after change is " + AdminConfig.showAttribute(configProcess,'startupTraceSpecification')
		
if (AdminConfig.hasChanges() == 1):
	AdminConfig.save()
