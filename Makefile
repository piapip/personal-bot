initiate-virtual-env:
  py -m venv "path-to-current-directory"

activate-virtual-environment:
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
  & .\Scripts\Activate.ps1

deactivate-virtual-environment:
  deactivate
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Restricted

install-dependency:
  py -m pip install -r ./requirements.txt

run:
  py .\__main__.py

install-exe-builder:
  py -m pip install pyinstaller

build-exe:
  # png to icon converter:
  #   https://convertio.co/
  cd ./exe
  pyinstaller.exe --onefile --icon="rpa_icon.ico" ../__main__.py
