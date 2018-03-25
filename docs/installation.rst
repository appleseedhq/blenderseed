Installation
++++++++++++

Download
	Download the .zip file of the latest release for your platform from the releases page. Note that only Blender 2.79 and later versions are supported.

Install
	From within Blender, open the User Preferences (usual hotkey is Ctrl+Alt+U) and navigate to the Addons tab. Click the button that says "Install From File". Using the file dialog, select the .zip file you downloaded, and click "Install From File..."

	**Alternative manual installation:**

	Extract the blenderseed folder from the .zip file. Move or copy the blenderseed folder to your Blender installation's /scripts/addons directory. The addon relies on being able to find the blenderseed folder in one of a few conspicuous places, so be sure to install the folder under addons or addons_contrib.

	Note: The addon depends on the folder being named correctly as blenderseed.  If you download the latest master branch, the folder will have a *-master* suffix that needs to be removed.

Configure
	If the addon was installed successfully, you will see it among your addons under the "Render" category. Enable the addon, and click the small triangle to the left of the words "Render: appleseed". You will see a text field with a file path selector next to the words "appleseed binary directory". Use the file path selector to point the addon to your appleseed installation's bin directory (the directory containing appleseed.cli.exe and appleseed.studio.exe).

	.. image:: \\_static\\screenshots\\blenderseed-addon-installation.png



	Blender User Preferences Dialog

	


	Save your user preferences.

	Select "appleseed" from the render dropdown selector.