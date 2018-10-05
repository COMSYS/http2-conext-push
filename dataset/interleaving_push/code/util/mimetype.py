def isStylesheet(resource):
	
	if 'css' in resource['mime'].lower():
		return True

	return False

def isScript(resource):
	
	if 'javascript' in resource['mime'].lower():
		return True

	return False

def isFont(resource):
	
	if 'font' in resource['mime'].lower():
		return True

	return False

def isImage(resource):
	
	if 'image' in resource['mime'].lower():
		return True

	return False