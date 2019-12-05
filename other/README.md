# MECHANICAL RIG TOOLKIT v.1.0
*Tim Coleman - tim.coleman.3d@gmail.com*


##
## Calling MEL scripts in your toolkit example
You may want to add MEL scripts that you or others have written to your own toolkit.  This is an example of one way to do it.  The important thing here is that you're using the command used in `renameTool.py`:

	os.path.dirname(__file__)

to find the path to where your MEL script resides so it can be sourced and called properly.

##
#### Example of how to call renameTool.mel from renameTool.py

	from mechRig_toolkit.other import renameTool
	reload(renameTool)
	renameTool.call_mel()




