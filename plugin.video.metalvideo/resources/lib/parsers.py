"""
	Copyright: (c) 2013 William Forde (willforde+kodi@gmail.com)
	License: GPLv3, see LICENSE for more details
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	
	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Call Necessary Imports
import HTMLParser
from xbmcutil import listitem, plugin

class WatchingParser(HTMLParser.HTMLParser):
	""" Parses video from http://metalvideo.com/index.html """
	def parse(self, urlobject, encoding="utf8"):
		return self.fromstring(urlobject.read(), encoding)
	
	def fromstring(self, html, encoding="utf8"):
		""" Parses SourceCode and Scrape Categorys """

		# Class Vars
		self.section = 0
		
		# Proceed with parsing
		results = []
		self.reset_lists()
		self.append = results.append
		try:
			if isinstance(html, unicode): self.feed(html)
			else: self.feed(html.decode(encoding))
		except plugin.ParserError: pass
		
		# Return Results
		return results
	
	def reset_lists(self):
		# Reset List for Next Run
		self.item = listitem.ListItem()
		self.item.urlParams["action"] = "PlayVideo"
	
	def handle_starttag(self, tag, attrs):
		# If not attrs exist then i dont need to proceed
		if not attrs: return
		elif tag == u"div":
			# Convert Attributes to a Dictionary
			for key, value in attrs:
				if key == u"id" and value == u"playingnow":
					self.section = 1
					break
		
		# Search for internel block
		elif self.section == 1 and tag == u"li":
			self.section = 2
			self.reset_lists()
		
		# Search for video content when within video block
		elif self.section == 2:
			# Search for url
			if tag == u"a" and not u"url" in self.item.urlParams:
				for key, value in attrs:
					if key == u"href":
						# Set video url
						self.item.urlParams["url"] = value
						
						# Add Context item to link to related videos
						self.item.addRelatedContext(url=value[value.rfind(u"_")+1:value.rfind(u".")])
			
			# Search for image url
			elif tag == u"img":
				# Search for imgae and title
				for key, value in attrs:
					# Serch for image url
					if key == u"src":
						self.item.setThumb(value)
					
					# Search for video title
					elif key == u"alt":
						self.item.setLabel(value)
	
	def handle_endtag(self, tag):
		# Check for the end video li tag
		if tag == u"li" and self.section == 2:
			self.append(self.item.getListitemTuple(True))
			self.section = 1
		
		# Check for the full end ul tag
		elif tag == u"ul" and self.section == 1:
			raise plugin.ParserError
