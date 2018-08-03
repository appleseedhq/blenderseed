@echo off

set /p appleseed_path=Enter Appleseed Package Directory:

set /p output_name=Set Version Number:

set APPLESEED=%appleseed_path%

blenderseed.package.py

set zipcmd="%~dp0\tools\7z\7z.exe"

pushd %~dp0\..\..
%zipcmd% a -r -x!scripts -xr!.* -x!__pycache__ -x!deploy -x!tests -x!docs -x!README.md blenderseed-%output_name%.zip blenderseed
popd

move ..\..\blenderseed-%output_name%.zip .

set /p delete_appleseed=Delete Appleseed Files? y/n:

if %delete_appleseed%==y goto :delete_directory
if %delete_appleseed%==n goto :keep_directory

:delete_directory
cd ../
rmdir /S appleseed

:keep_directory

pause
