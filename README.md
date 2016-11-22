INKSCAPE EMBROIDERY EXTENSION
=============================

Inkscape is a natural tool for designing embroidery patterns; the only challenge is converting 
the Inkscape design to a stitch file. It can be used to design embroidery texts too.

INSTALLATION
============

Linux
-----

1. Acquire GEOS library by any means. In Ubuntu you can find it in repositories.

   ````bash
   $ apt-get install libgeos-dev
   ````
2. Install [shapely] library into python

   ````bash
   $ pip install shapely
   ````
3. Copy this extension into ~/.config/inkscape/extensions directory

Windows
-------

Windows users can experience troubles with [shapely] installation. Installation may be some tricky
It may be easier to use Linux inside the [Virtualbox]. If you still want to use Inkscape 
for Windows try following steps:

1. Install [python](http://python.org). (Windows XP users can use python 2.x version only)
2. Download shapely for windows with extension library installer from [http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely].
   File something like _Shapely-1.5.17-cp27-cp27m-win32.whl_. Install it with pip
   ````pip install Shapely-1.5.17-cp27-cp27m-win32.whl````
3. After installation copy directory \Python27\Lib\site-packages\shapely 
   into \Program Files\Inkscape\Lib\site-packages\shapely. Although Inkscape uses Python2.6 shapely works well.

USAGE
=====

Create svg drawing by any means (draw yourself, vectorize raster image, download etc). Prepare
every element of the image with **Params** module. Set needed generation sequense with **Reorder**
module. Generate stitches with **Embroider** module. Correct stitches if needed. Regenerate
corrected embroidery with **svg2emb** module.

Embroider module
-----------------

There are 3 types of stitch generation modes:

1. Zigzag fill for stroke lines. When stroke width < 0.5pt it geterates just running stitches across
path edge. When stroke width >= 0.5pt zigzag stitches are generated across such path.

2. Satin column. If you have two parallel (or not parallel) paths with the same number of points 
you can create zigzag filled area between these paths. Path must be combined.

3. Filled area generates parallel filling stitches (or zigzag stitches if hatching is enabled) 
inside filled zones.

Params module
-------------

Params module is used to set personal embroidery generation parameters for every node in the
image. It allows using different fill styles for every piece of your embroidery.

Reorder module
--------------

Embroidery is generated in the order pieces are present in the base file. Reorder module allows you
to set order of pieces you want. You just select all shapes in your own sequence and call reorder
module.

svg2emb module
--------------

After embroidery is generated one may need handmade corrections. You can add, remove or move nodes
and regenerate output embroidery file as is. This is done with svg2emb module.

CONVERSION TO MACHINE FORMAT
============================

Conversion to machine formats are not included in this extension. It generates rathe small number
of formats. But you can generate [Embroidermodder] CSV format and then convert this format into
needed machine format with **libembroidery-convert** wich is the part of [Embroidermodder]

[Embroidermodder]: https://github.com/Embroidermodder/Embroidermodder
[shapely]: https://pypi.python.org/pypi/Shapely
[Virtualbox]: https://www.virtualbox.org/