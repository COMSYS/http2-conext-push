#!/usr/bin/env python

"""
Generate a random image using PIL.
"""
import argparse
import math
import random

from PIL import Image, ImageColor

import random
import string

def generateRandomString(length=1024, charset=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(charset) for x in range(length))


def generateJavascript(length, nextFile=None, sleep=None):
    """
    If nextFile is specified, insert a document write at then end
    """

    header = '/*'

    footer = '*/'

    if sleep is not None:
        footer += """function pausecomp(millis)
        {
            var date = new Date();
            var curDate = null;
            do { curDate = new Date(); }
            while(curDate-date < millis);
        } pausecomp("""+str(int(sleep))+");"


    if nextFile is not None:
        footer += """document.write('<script src="{}" type="text/javascript"></script>');""".format(nextFile)


    remainderSize = length - len(header) - len(footer)

    if remainderSize < 0:
        raise ValueError("Size is too small to fit required contents")

    remainder = generateRandomString(length=remainderSize)

    javascript = header + remainder + footer

    return javascript

def generateCss(length,nextFile=None):
    header = '/*'

    footer = '*/'


    preheader = ""
    if nextFile is not None:
        preheader += """@import url("{}");""".format(nextFile)


    remainderSize = length -len(preheader) - len(header) - len(footer)

    if remainderSize < 0:
        raise ValueError("Size is too small to fit required contents")

    remainder = generateRandomString(length=remainderSize)

    css = preheader + header + remainder + footer

    return css


def generateHTMLComment(length):
    """
    If nextFile is specified, insert a document write at then end
    """

    header = '<!--'

    footer = '-->'


    remainderSize = length - len(header) - len(footer)

    if remainderSize < 0:
        raise ValueError("Size is too smal to fit. required contents")

    remainder = generateRandomString(length=remainderSize)

    comment = header + remainder + footer

    return comment



def generateHtml(length=1024,title="Synthetic Page", linked_subresources=[],headcontent="",bodycontent=""):


    header_resources = []
    body_resources = []

    for resource in linked_subresources:
        html = None
        if resource['url'].endswith('js'):
            html = '<script src="{}" type="text/javascript"></script>'.format(resource['url'])
        elif resource['url'].endswith('bmp') or resource['url'].endswith('jpg') or resource['url'].endswith('gif') or resource['url'].endswith('png'):
            html = '<img src="{}" alt="a foo"/>'.format(resource['url'])
        elif resource['url'].endswith('css'):
            html = '<link rel="stylesheet" type="text/css" href="{}">'.format(resource['url'])


        if resource['where'] == 'head':
            header_resources.append(html)
        elif resource['where'] == 'body':
            body_resources.append(html)




    headertemplate = """<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>{}</title>""".format(title)

    for res in header_resources:
        headertemplate += res
    
    headertemplate += headcontent
    headertemplate += "</head>"


    bodytemplate = "<body>{}".format(generateHTMLComment(length))
    for res in body_resources:
        bodytemplate += res
    bodytemplate += bodycontent
    bodytemplate += "you are seeing a synthetic page.</body></html>"

    return headertemplate+bodytemplate



def get_dimensions(requested_size_in_bytes):
    """
    Figure dimensions for given requested size.
    Formula: target_size_in_bytes = height * width * 3
    For a (mostly) square image, axis = sqrt(bytes/3)
    """
    axis = long(math.sqrt(requested_size_in_bytes/3))
    # figure out how many pixels fit within this grid,
    # since we rounded the figures
    total_pixels = (axis * axis)

    return dict(size_in_bytes=requested_size_in_bytes,
                axis_x=axis,
                axis_y=axis,
                total_pixels=total_pixels
                )

def generate_image_by_output_size(requested_size_in_bytes):
    """
    Generate a random bitmap by requested file size.
    Secret formula: 3 * HEIGHT * WIDTH == ~OUTPUT_SIZE_IN_BYTES
    """
    dimensions = get_dimensions(requested_size_in_bytes)
    size = (dimensions['axis_x'], dimensions['axis_y'])
    color = (255, 0, 0)
    img = Image.new("RGB", size, color)
    return img

def generate_random_image_by_size(requested_size_in_bytes, monochrome=False):
    """
    Generate a random image by size, optionally in monochrome
    """
    img_data = []
    pixel_color = ""
    monochrome_colors = ("white", "black", )
    #for pixel in img.getdata():
    dimensions = get_dimensions(requested_size_in_bytes)
    for x in xrange(0, dimensions['total_pixels']):
        if monochrome:
            pixel_color = random.choice(monochrome_colors)
            img_data.append(ImageColor.getrgb(pixel_color))
        else:
            # randomize indices between 0 & 255
            img_data.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255),))

    randomized_image = Image.new("RGB", size=(dimensions['axis_x'], dimensions['axis_y']))
    randomized_image.putdata(img_data)
    return randomized_image

def save_image(img, file_path, image_type=None):
    """
    Helper to save Image object to file, with optional explicit type.
    """
    if image_type:
        img.save(file_path, image_type)
    else:
        img.save(file_path)

def generateImageByte(requested_size_bytes,path,randomize=False,monochrome=False):
    if randomize:
        img = generate_random_image_by_size(requested_size_bytes, monochrome=monochrome)
    else:
        img = generate_image_by_output_size(requested_size_bytes)
    
    save_image(img, path)




def generateHtmlWithJavascriptInclude(num_js,js_prefix='js/js_',js_suffix='.js',length=1024,title="Synthetic Page"):


    header_resources = []
    body_resources = []


    headertemplate = """<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>{}</title>""".format(title)

    for res in header_resources:
        headertemplate += res
    headertemplate += "</head>"


    bodytemplate = "<body>{}".format(generateHTMLComment(length))
    for res in body_resources:
        bodytemplate += res

    js_path = js_prefix+"""'+i+'"""+js_suffix

    bodytemplate += """<script type="text/javascript">for(var i = 0;i<"""+str(num_js)+""";i++){document.write('<script type="text/javascript" """+'src="'+js_path+'"'+"""><\/script>');}</script>"""
    bodytemplate += "you are seeing a synthetic page.</body></html>"

    return headertemplate+bodytemplate