class FacebookPost(object):

	def __init__(self, fb_post_tuple):
		super(FacebookPost,self).__init__()
		self.status_id=fb_post_tuple[0]
		self.status_message=fb_post_tuple[1]
		self.status_author=fb_post_tuple[2]
		self.link_name=fb_post_tuple[3]
		self.status_type=fb_post_tuple[4]
		self.status_link=fb_post_tuple[5]
		self.status_published=fb_post_tuple[6]
		self.num_reactions=fb_post_tuple[7]
		self.num_comments=fb_post_tuple[8]
		self.num_shares=fb_post_tuple[9]
		self.num_likes=fb_post_tuple[10]
		self.num_loves=fb_post_tuple[11]
		self.num_wows=fb_post_tuple[12]
		self.num_hahas=fb_post_tuple[13]
		self.num_sads=fb_post_tuple[14]
		self.num_angrys=fb_post_tuple[15]
		self.num_special=fb_post_tuple[16]

	def get_tuple(self):
		return (self.status_id,
		self.status_message,
		self.status_author,
		self.link_name,
		self.status_type,
		self.status_link,
		self.status_published,
		self.num_reactions,
		self.num_comments,
		self.num_shares,
		self.num_likes,
		self.num_loves,
		self.num_wows,
		self.num_hahas,
		self.num_sads,
		self.num_angrys,
		self.num_special)

	def __str__(self):
		selfstr=""
		for item in self.get_tuple():
			selfstr = selfstr + str(item) + ','
		return selfstr
		