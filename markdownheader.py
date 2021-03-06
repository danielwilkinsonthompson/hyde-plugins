# -*- coding: utf-8 -*-
"""
A plugin class for transforming markdown headers to jinja headers
"""

from hyde.plugin import Plugin
from fswrap import File
from hyde.ext.plugins.meta import MetaPlugin
import re

class MarkdownHeaderPlugin(Plugin):
    """
    The plugin class for transforming markdown headers to jinja headers
    """
    
    def __init__(self, site):
        super(MarkdownHeaderPlugin, self).__init__(site)

    def begin_site(self):
        """
        Find all the md files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if resource.source_file.kind == 'md':
                new_name = resource.source_file.name_without_extension + ".html"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)
                md_hdr = self.__resource_meta__(resource, resource.source_file.read_all())
                # Have to call metaplugin to update metadata
                if hasattr(resource, 'meta'):        
                    resource.meta.update(md_hdr)
                  
    def begin_text_resource(self, resource, text):
        """
        Update all identified md files.
        """
        return self.__update_resource_excerpts__(resource, text)      

    # Have to run this as the site is generated, otherwise listing pages get all screwy
    def __resource_meta__(self, resource, text):
        """
        Replace md headers with jinja headers.
        """
        if not resource.source_file.kind == 'md':
            return text      
        
        # Separate out any existing Jinja headers
        md = re.sub(r"^\s*(---|===)\s*$", '', text, flags=re.MULTILINE)
        
        # Split entire article into an array of paragraphs
        md_by_paragraph = re.split('\n\s*\n',md)         
        
        # The header is the first paragraph
        md_hdr = md_by_paragraph[0]
         
        # Replace any '# This is an H1 #' or '# This is an H1' markdown headers with 'title: This is an H1'
        md_hdr = re.sub('^#{1}([^#].*).#*$', 'title:\\1', md_hdr, flags=re.MULTILINE)
        
        # Replace 'date: YYYY-MM-DD' with "created: !!timestamp 'YYY-MM-DD'"
        md_hdr = re.sub('^date:\s(.*)$', 'created: !!timestamp \'\\1\'', md_hdr, flags=re.MULTILINE|re.IGNORECASE)
        
        
        text = '\n\n'.join(md_by_paragraph[1::]) 
        
        #This seems to fire for tagged posts, need to run only body, not header
        # Code: (four spaces at line start), --> Add code: true to metadata
        md_code = re.compile("^    .+", re.UNICODE|re.MULTILINE)
        html_code = re.compile("<code>.*</code>", re.UNICODE|re.MULTILINE)
        if md_code.search(text):
          md_hdr = 'code: true\n' + md_hdr
        else:
          if html_code.search(text):
            md_hdr = 'code: true\n' + md_hdr
            
        # Gallery !{![]()[]()}, --> Add gallery: true to metadata          
        md_gallery = re.compile("\!\{(\!*\[.*?\]\(.+?\))+\}", re.UNICODE|re.MULTILINE)
        if md_gallery.search(text):
          md_hdr = 'gallery: true\n' + md_hdr 
       
        # Math: $$...$$, \\[...\\], \\(...\\) --> Add math: true to metadata
        md_math = re.compile("[$][$].+[$][$]|\\\\\[.+\\\\\]|\\\\\(.+\\\\\)", re.UNICODE|re.MULTILINE)
        if md_math.search(text):
          md_hdr = 'math: true\n' + md_hdr
          
        # Image: ![]() or index.html --> Add image: true to metadata  
        md_image = re.compile("\!\[(.*)\]\((.*)\)", re.UNICODE|re.MULTILINE)
        md_index = re.compile("index[.]html$",re.UNICODE)
        if md_image.search(text):
          md_hdr = 'image: true\n' + md_hdr
        else:  
          if md_index.search(resource.relative_deploy_path):
            md_hdr = 'image: true\n' + md_hdr
  
        return md_hdr
        
    def __update_resource_excerpts__(self, resource, md):
        """
        Insert excerpt markers.
        """
        if not resource.source_file.kind == 'md':
            return md

        text_excerpt_start = "{% mark excerpt %}"
        image_excerpt_start = "{% mark image %}"
        excerpt_end = "{% endmark %}"

        md = re.sub(r"\{%-*\s*mark\s*excerpt\s*-*%\}", '', md, flags=re.MULTILINE)
        md = re.sub(r"\{%-*\s*mark\s*image\s*-*%\}", '', md, flags=re.MULTILINE)
        md = re.sub(r"\{%-*\s*endmark\s*-*%\}", '', md, flags=re.MULTILINE)
        
        # First, find gallery string
        md_gallery = re.compile("\!\{.+?\}", re.UNICODE|re.MULTILINE)
        gallery = md_gallery.search(md)
        
        if gallery:
          
          # Search and replace all images with gallery tagging
          md_gallery_image = re.compile("\!\[(.*?)\]\((.+?)\)", re.UNICODE|re.MULTILINE)
          md_gallery_contents = md_gallery_image.sub("<a class=\"fancybox\" rel=\"group\" href=\"{{ media_url('images/" + resource.meta.created.strftime('%Y') + "/\\2') }}\" title=\"\\1\" alt=\"\\1\">~~~\\1~~~{\\2}</a>",gallery.group())
          
          # Search and replace all links with gallery tagging
          md_gallery_item = re.compile("(?:\[(.*?)\]\((.+?)\))", re.UNICODE|re.MULTILINE)
          md_gallery_contents = md_gallery_item.sub("<a class=\"fancybox\" rel=\"group\" href=\"{{ media_url('images/" + resource.meta.created.strftime('%Y') + "/\\2') }}\" title=\"\\1\" alt=\"\\1\"></a>",md_gallery_contents)
          
          # Remove gallery markup !{}
          md_gallery_contents = re.sub("\!\{(.*)\}","\\1",md_gallery_contents)          
          
          # Correct image tagging so that it is formatted as markdown image
          md_gallery_contents = re.sub("~~~(.*?)~~~\{(.+?)\}","![\\1](\\2)", md_gallery_contents)

          # Find gallery string in text again, but substitue for md_gallery_contents
          md = re.sub("\!\{.+?\}",md_gallery_contents ,md)
          
        
        # Replace all images
        md_image = re.compile("\!\[(.*?)\]\((.+?)\)", re.UNICODE|re.MULTILINE)
        md = md_image.sub("<figure>" + image_excerpt_start + "<img src=\"{{ media_url('images/" + resource.meta.created.strftime('%Y') + "/\\2') }}\" alt='\\1' title='\\1' width=100%/>" + excerpt_end + "<figcaption>\\1</figcaption></figure>",md) 
        
        md = md_image.sub("<figure><img src=\"{{ media_url('images/\\2') }}\" alt='\\1' title='\\1' width=100%/><figcaption>\\1</figcaption></figure>",md)              
        
        # Handle local page links
#         md_local_link = re.compile("\[(|.*)\]\((?!.+://.+)(.+\))", re.UNICODE|re.MULTILINE)
#         md = md_local_link.sub("<a href=\"{{ content_url('\\2') }}\" title=\"\\1\" alt=\"\\1\">\\1</a>", md)
                
        md_excerpt = ''
        md_body = ''
        starting_paragraph = 1
        head_img = ''

        # Split entire article into an array of paragraphs
        md_by_paragraph = re.split('\n\s*\n', md)         

        if len(md_by_paragraph) > starting_paragraph:
          img_first = re.compile(image_excerpt_start, re.UNICODE|re.MULTILINE)
          img_first_match = img_first.search(md_by_paragraph[1])
                  
          if img_first_match:
            starting_paragraph = 2
            head_img = md_by_paragraph[1]
          
        if len(md_by_paragraph) > starting_paragraph:  
          md_excerpt = text_excerpt_start + '\n' + md_by_paragraph[starting_paragraph] + '\n' + excerpt_end + '\n'
        
        # The body of the article contains all remaining paragraphs
        if len(md_by_paragraph) > (starting_paragraph+1):
          md_body = md_by_paragraph[(starting_paragraph+1)::]
                                            
        # The final article is the header, excerpt, and body
        text = head_img + '\n\n' + md_excerpt + '\n\n' + '\n\n'.join(md_body[0::])                  
        
        return text         