class cwf_Dispatch(object):
	def __init__(self):
		self.viewObjs = {}
	
	def __getitem__(self, key):
		try:
			view = self.viewObjs[key]
		except KeyError:
			obj = key.split('.')
			pkg = __import__('.'.join(obj[:-1]), globals(), locals(), [obj[-1]], -1)
			view = getattr(pkg, obj[-1])
			self.viewObjs[key] = view = view(self.request)
		
		return view
		
	def __call__(self, request, obj, target, section, *args, **kwargs):
		self.request = request
		return self[obj](request, target, section=section, *args, **kwargs)
	
dispatch = cwf_Dispatch()
