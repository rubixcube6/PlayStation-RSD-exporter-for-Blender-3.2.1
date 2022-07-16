# PlayStation RSD exporter for Blender 3.2.1+!
[Example Project](https://user-images.githubusercontent.com/11562971/179373557-aca8542b-cd5b-4830-81e7-608cf237dae6.png)

This plugin will export your model in the RSD model format for use with the PSX PsyQ SDK. It supports exporting lit and unlit polygons, smooth and flat shaded polygons, Textured polygons, and vertex colors.

This works with Blender 3.2.1 and should work with future versions.

# Installation
Go to "Edit --> Preferences --> Add-ons" and click the "Install" button. Browse for the "Playstation RSD Exporter.py" file and make sure the checkbox for this add-on is checked.

# How To Use
Select the object (in "Object Mode") you want to export. Then Go to "File --> Export --> RSD (PlayStation) Export" and save your RSD model file wherever you like.

For textured models you should only use one texture per material. Since the playstation doesn't support complex shader properties all you need is a shader with an image attached to the base color, then just UV map your model like you normally would. Polygons with an "Emission" shader will be exported as unlit.

For Smooth and Flat shaded polygons, at the moment auto-smoothing is not supported. In edit mode, select the faces you would like to shade and go to "Face --> Shade Smooth" or "Face --> Shade Flat"

# Latest Updates
v1.1: 
This update is a big one! After a lot of stress testing a few bugs were fixed and some new features were added
- All different types and variations of a polygon "Shading (smooth and flat), Lit and unlit, vertex color (smooth and flat), and Textured/not textured" have now been tested working and interacting with each other. 
- You can now have lighting on vertex colored faces. however, vertex colored faces with a texture will always be unlit.
- You can now export all of the above types of polygons in one mesh.
- It now forces polygons to be unlit if it sees an emission shader in that face's material
- You now have the option in the export window to force the entire mesh to be unlit.
