.. _label_installation:

Installation
============

Version
    As of version 2.0, blenderseed is intended to be used with Blender 2.8.  We do have a maintenance branch for the Blender 2.79 exporter, but it is not actively developed and will likely be missing features that are present in the main branch.

Download
	Download the .zip file of the latest `blenderseed release <https://github.com/appleseedhq/blenderseed/releases>`_ for your platform and Blender version. appleseed itself is bundled with the addon, so no additional downloads are needed.  Please note that the 2.79 version **requires** Blender 2.79b or later.  It will not work with earlier versions.

Install
	From within Blender, open the User Preferences and navigate to the Addons tab. Click the button that says "Install From File". Using the file dialog, select the .zip file you downloaded, and click "Install From File..."

	**Alternative manual installation**

	Extract the blenderseed folder from the .zip file. Move or copy the blenderseed folder to your Blender installation's /scripts/addons directory. The addon relies on being able to find the blenderseed folder in one of a few conspicuous places, so be sure to install the folder under addons or addons_contrib.

Configure
	If the addon was installed successfully, you will see it among your addons under the "Render" category. Enable the addon, and click the small triangle to the left of the words "Render: appleseed". 

	Save your user preferences.

	Select "appleseed" from the render dropdown selector.

Adding Additional Search Paths
    New in 2.0 is the ability to add resource search paths in the addon preferences panel.  If a path is added here, the addon will prompt you to restart Blender for the change to take effect.  When the reload occurs the new search path will be parsed for OSL shaders.

Using Development Versions of blenderseed
	If you want access to cutting edge features, you can also download directly from the master branch (or any other visible branches).  Any downloads will have a suffix of *'-branch name'* that needs to be removed before it will work.  Be aware that new or under development features may require an up to date build of appleseed itself, and this is not included with direct branch downloads. [#f1]_ [#f2]_

Using Development Versions of appleseed
	While appleseed is packaged with all official releases, external versions of it may be used with blenderseed.  To do so, set the following environment variables before launching Blender (Windows only):
	
	- APPLESEED_PYTHON_DIR:
		Set to the Python directory in your appleseed build's sandbox/lib folder.

	- APPPLESEED_BIN_DIR:
		Set to the folder of your appleseed build's sandbox/bin folder that contains the main appleseed library.

.. rubric:: Footnotes:

.. [#f1] If you are compiling applessed for use with blenderseed, you will need to compile appleseed with the Python 3 bindings enabled.  Please see the `build instructions <https://github.com/appleseedhq/appleseed/wiki/Building-appleseed>`_.
.. [#f2] You must also compile with the same version of Python 3 that is used by your Blender install.  Blender 2.79b official uses Python 3.5.  Current 2.79 branches and Blender 2.8 uses Python 3.7.
