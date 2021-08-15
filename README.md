## blenderseed [![Documentation Status](https://readthedocs.org/projects/appleseed-blenderseed/badge/?version=latest)](https://readthedocs.org/projects/appleseed-blenderseed/)

![Chair & Table](https://github.com/appleseedhq/appleseedhq.github.io/raw/master/img/renders/chair-and-table.png)

## Overview

blenderseed is an appleseed plugin for [Blender](https://www.blender.org/) 2.79b and 2.8-2.92 only.  2.93 and up are NOT SUPPORTED.

* [**Download** the latest release](https://github.com/appleseedhq/blenderseed/releases)
* [**Read** the documentation](https://appleseed-blenderseed.readthedocs.io/)
* [**Report** bugs and suggest features](https://github.com/appleseedhq/blenderseed/issues)

blenderseed includes support for the following features of appleseed:  
* Pinhole, thin lens (supports physically correct depth of field), and spherical camera models
* Camera, transformation and deformation motion blur
* Particle / instance motion blur
* Instancing (dupliverts / duplifaces)
* BSDF materials
* Volumetric material
* BSSDF materials
* OSL shading
* Normal / bump mapping
* Alpha mapping
* Mesh lights
* Point, directional, and sun lights
* Spot lights (supports textures)
* Physical sun/sky
* Gradient, constant, mirror ball map and latitude-longitude map environment models

blenderseed also supports:
* Node-based OSL material creation (with Blender's node editor)
* Export to appleseed scene files or rendering within Blender's image editor
* Selective geometry export (for faster re-export and re-rendering of scenes)
* Material preview rendering

## License

appleseed and its accompanying software is released under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).

© 2010-2018 The appleseedhq Organization
