.. _label_installation:

Installation
============

Download
	Download the .zip file of the latest `blenderseed release <https://github.com/appleseedhq/blenderseed/releases>`_ for your platform. Note that as of 0.8.0 you must use Blender 2.79 or higher.

	*Blender 2.8 is not yet supported*

Install
	From within Blender, open the User Preferences (usual hotkey is Ctrl+Alt+U) and navigate to the Addons tab. Click the button that says "Install From File". Using the file dialog, select the .zip file you downloaded, and click "Install From File..."

	**Alternative manual installation**

	Extract the blenderseed folder from the .zip file. Move or copy the blenderseed folder to your Blender installation's /scripts/addons directory. The addon relies on being able to find the blenderseed folder in one of a few conspicuous places, so be sure to install the folder under addons or addons_contrib.

Configure
	If the addon was installed successfully, you will see it among your addons under the "Render" category. Enable the addon, and click the small triangle to the left of the words "Render: appleseed". 

	Save your user preferences.

	Select "appleseed" from the render dropdown selector.

Using Development Versions of blenderseed
	If you want access to cutting edge features, you can also download directly from the master branch (or any other visible branches).  Any downloads will have a suffix of *'-branch name'* that needs to be removed before it will work.  Be aware that new or under development features may require an up to date build of appleseed itself, and this is not included with direct branch downloads.

Using Development Versions of appleseed
	While appleseed is packaged with all official releases, external versions of it may be used with blenderseed.  To do so, set the following environment variables before launching Blender (Windows only):
	
	- APPLESEED_PYTHON_PATH:
		Set to the Python27 directory in your appleseed build.

	- APPPLESEED_BIN_DIR:
		Set to the /bin folder of your appleseed build.