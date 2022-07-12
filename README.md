# PlayStation RSD exporter for Blender 3.2.1+
This plugin will export your model in the RSD model format for use with the PSX PsyQ SDK. It supports exporting smooth and flat shaded polygons, Textured polygons, and vertex colors.

This works with Blender 3.2.1 and should work with future versions.

# Installation
Go to "Edit --> Preferences --> Add-ons" and click the "Install" button. Browse for the "Playstation RSD Exporter.py" file.

# How To Use
Make sure to select the object you want to export. Then Go to "File --> Export --> RSD (PlayStation) Export" and save your RSD model file wherever you like.

For textured models you should only use one texture per material. Since the playstation doesn't support complex shader properties all you need is a shader with an image attached to the base color, then just UV map your model like you normally would.

For Smooth and Flat shaded polygons, at the moment auto-smoothing is not supported. In edit mode, select the faces you would like to shade and go to "Face --> Shade Smooth" or "Face --> Shade Flat"
