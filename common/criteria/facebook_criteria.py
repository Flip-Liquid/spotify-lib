
class FacebookCriteria(object):
	"""docstring for FacebookCriteria"""
	def __init__(self):
		super(object, self).__init__()
		self.date_range=tuple()
		self.authors=list()
		self.group_id=""
		self.app_id=""
		self.app_secret=""

	def __str__(self):
		return "%s %s %s %s" % (self.date_range, self.authors, self.group_id, self.app_id)