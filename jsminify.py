# -*- coding: utf-8 -*-
"""
JSMin plugin
"""

from hyde.plugin import Plugin
from jsmin import jsmin

class JSMinifyPlugin(Plugin):
    """
    The plugin class for JSMin
    """

    def __init__(self, site):
        super(JSMinifyPlugin, self).__init__(site)

    def text_resource_complete(self, resource, text):
        """
        Minify all javascript
        """

        if not resource.source_file.kind == 'js':
            return text
		
        return jsmin(text)
