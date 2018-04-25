@echo off

set zipcmd="%~dp0\tools\7z\7z.exe"

pushd %~dp0\..\..
%zipcmd% a -r -x!scripts -xr!.* -x!__pycache__ -x!docs -x!README.md blenderseed-x.x.x.zip blenderseed
popd

move ..\..\blenderseed-x.x.x.zip .

pause
