# -*- coding: utf-8 -*-
"""
cssmin plugin
"""

from hyde.plugin import Plugin
from operator import attrgetter
from cssmin import cssmin

class CSSMinifyPlugin(Plugin):
    """
    The plugin class for cssmin
    """

    def __init__(self, site):
        super(CSSMinifyPlugin, self).__init__(site)

    def text_resource_complete(self, resource, text):
        """
        Minify all CSS
        """

        if not resource.source_file.kind == 'css':
            return

        return cssmin(text)
