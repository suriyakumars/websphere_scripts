import sys

dsName = sys.argv[0]
dsUrl = sys.argv[1]
j2cAuthAlias = sys.argv[2]

def setDBurl (dsName, dsUrl, j2cAuthAlias):
	newds = AdminConfig.getid('/DataSource:'+ dsName + '/')
	propSet = AdminConfig.create('J2EEResourcePropertySet', newds, [])
	AdminConfig.create('J2EEResourceProperty', propSet, [['name', 'URL'], ['value', dsUrl]])
	AdminConfig.save()
	print "DB URL configured for "+dsName
	AdminConfig.modify(newds, [['authDataAlias', j2cAuthAlias], ['xaRecoveryAuthAlias', j2cAuthAlias]])
	AdminConfig.save()
	print "Auth Alias "+authName+" configured for "+dsName

setDBurl (dsName, dsUrl, j2cAuthAlias)
