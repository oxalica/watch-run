{ writeScriptBin, python3 }:
let
  python = python3.withPackages (pkgs: with pkgs; [
    pyinotify
  ]);
in writeScriptBin "watch-run" ''
  #!${python}/bin/python
  ${builtins.readFile ./watch-run.py}
''
