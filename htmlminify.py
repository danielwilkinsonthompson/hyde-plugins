# -*- coding: utf-8 -*-
# Copyright 2012 django-compresshtml authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
"""
HTMLminify plugin
"""

from hyde.plugin import Plugin
import re

class HTMLMinifyPlugin(Plugin):
    """
    The plugin class for HTMLMinify
    """

    def __init__(self, site):
        super(HTMLMinifyPlugin, self).__init__(site)

    def text_resource_complete(self, resource, text):
        """
        Minify all HTML
        """

        html_finder = re.compile(r"^\s*.*(?:.html)\s*$", re.MULTILINE)
        match = re.match(html_finder, resource.relative_deploy_path)
        if not match:
            return
    
        #remove white spaces between tags
        html_code = re.sub(r'>\s+<', r'><', text)
    
        #remove comments
        comments_regex = re.compile(r'<!--[^\[](.*?)-->', re.DOTALL)
        html_code = comments_regex.sub(r'', html_code) # .*? make it non greedy | won't remove downlevel-revealed or downlevel-hidden comments    
        
        #minimise white spaces between two tags (<xx> dfsd </yy>)
        html_code = re.sub(r'>\s+(.*?)\s+</', r'> \1 </', html_code)

        #remove line breaks - currently messes up <pre></pre>
        #html_code = re.sub(r'\n*','', html_code)
    
        return html_code
