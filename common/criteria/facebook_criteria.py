
class FacebookCriteria(object):
	"""docstring for FacebookCriteria"""
	def __init__(self, date_range,authors,min_likes,min_loves,limit):
		super(object, self).__init__()
		self.date_range,self.authors,self.min_likes,self.min_loves,self.limit = date_range,authors,min_likes,min_loves,limit
		self.group_id=""
		self.app_id=""
		self.app_secret=""

	def __str__(self):
		return "%s %s %s %s" % (self.date_range, self.authors, self.group_id, self.app_id)