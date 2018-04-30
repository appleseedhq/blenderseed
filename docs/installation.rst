.. _label_installation:

Installation
============

Download
	Download the latest `appleseed release <https://github.com/appleseedhq/appleseed/releases>`_ and unzip it to a location on your hard drive.

	Download the .zip file of the latest `blenderseed release <https://github.com/appleseedhq/blenderseed/releases>`_. [#f1]_ Note that as of 0.8 you must use Blender 2.79 or higher.

	*Blender 2.8 is not yet supported*

Install
	From within Blender, open the User Preferences (usual hotkey is Ctrl+Alt+U) and navigate to the Addons tab. Click the button that says "Install From File". Using the file dialog, select the .zip file you downloaded, and click "Install From File..."

	**Alternative manual installation**

	Extract the blenderseed folder from the .zip file. Move or copy the blenderseed folder to your Blender installation's /scripts/addons directory. The addon relies on being able to find the blenderseed folder in one of a few conspicuous places, so be sure to install the folder under addons or addons_contrib.

Configure
	If the addon was installed successfully, you will see it among your addons under the "Render" category. Enable the addon, and click the small triangle to the left of the words "Render: appleseed". You will see a text field with a file path selector next to the words "appleseed binary directory". Use the file path selector to point the addon to your appleseed installation's bin directory (the directory containing appleseed.cli.exe and appleseed.studio.exe).  You will need to restart Blender in order for the OSL features to be usable.

|

	.. image:: /_static/screenshots/blenderseed-addon-installation.png

	Blender User Preferences Dialog

|

	Save your user preferences.

	Select "appleseed" from the render dropdown selector.

.. rubric:: Footnotes:
.. [#f1] If you want access to cutting edge features, you can directly download the latest master branch from Github.  Be aware that the master branch may not be stable or complete and new features may require an up to date build of appleseed.  If you download the master branch, the folder will have a *-master* suffix that needs to be removed before the addon will be usable.