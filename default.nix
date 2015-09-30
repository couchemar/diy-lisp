{
  pkgs ? import <nixpkgs> {},
  pythonPackages ? pkgs.pythonPackages
}:
  pythonPackages.buildPythonPackage rec {
      name = "diy-lisp";
      propagatedBuildInputs = with pythonPackages; [ nose ipdb readline ];
  }
