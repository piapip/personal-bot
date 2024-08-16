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
