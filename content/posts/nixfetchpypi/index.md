+++
date = '2024-12-12T00:19:41+08:00'
draft = false
title = 'Nix fetchPypi'
+++

Seriously, nix doc is so hard to find...
<!--more-->

I needed to fetch specific versions of python packages, and after searching, they told me to use `fetchPypi`. But I just couldn't find any documentation about what it ACTUALLLY is. So I had to dig inside [nixpkgs](https://github.com/NixOS/nixpkgs) to figure what exactly is going on.

# fetchPypi
So here's the source for those who are not patient enough: 
[fetchPypi](https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/fetchpypi/default.nix).
Here's what's inside(I literally copy pasted it):
```nix
# `fetchPypi` function for fetching artifacts from PyPI.
{ fetchurl
, makeOverridable
}:

let
  computeUrl = {format ? "setuptools", ... } @attrs: let
    computeWheelUrl = {pname, version, dist ? "py2.py3", python ? "py2.py3", abi ? "none", platform ? "any"}:
    # Fetch a wheel. By default we fetch an universal wheel.
    # See https://www.python.org/dev/peps/pep-0427/#file-name-convention for details regarding the optional arguments.
      "https://files.pythonhosted.org/packages/${dist}/${builtins.substring 0 1 pname}/${pname}/${pname}-${version}-${python}-${abi}-${platform}.whl";

    computeSourceUrl = {pname, version, extension ? "tar.gz"}:
    # Fetch a source tarball.
      "mirror://pypi/${builtins.substring 0 1 pname}/${pname}/${pname}-${version}.${extension}";

    compute = (if format == "wheel" then computeWheelUrl
      else if format == "setuptools" then computeSourceUrl
      else throw "Unsupported format ${format}");

  in compute (builtins.removeAttrs attrs ["format"]);

in makeOverridable( {format ? "setuptools", sha256 ? "", hash ? "", ... } @attrs:
  let
    url = computeUrl (builtins.removeAttrs attrs ["sha256" "hash"]) ;
  in fetchurl {
    inherit url sha256 hash;
  })
```
Great, now let's read it a bit and figure out what's going on. 

# makeOverridable
You'll see `makeOverridable` at the end, here's its signature([link](https://github.com/NixOS/nixpkgs/blob/204afb3d25f51a296b5d4c0ae9d39d5c1e9bdee2/lib/customisation.nix#L93)):
```nix
makeOverridable :: (AttrSet -> a) -> AttrSet -> a
```
There's also examples in the link, but basically here's what happens:
It takes a function, that takes an attribute set and returns a value, and an attribute set as arguments. It then returns the result attribute set with the argument attribute set used as the argument for the function. 
You can choose to override the argument attribute set by using `.override { key = val; }` syntax. If you don't, the default value will be used.

Here's an example:
```nix
{
  f = { a, b }: { result = a+b; };
  c = lib.makeOverridable f { a = 1; b = 2; };
}
```
In this example the value of
`(c.override { a = 4; }).result` is 6.

# arguments for fetchPypi
Okay, you want a python package. You know where it is on pypi, you want the derivation for it. `fetchPypi` can do it. 
Its signature:
```nix
fetchPypi :: AttrSet -> Derivation
```
It needs:
- `pname`: package name
- `version`: version of the package
- `format`: (optional) "wheel" or "setuptools". Default is "setuptools". "setuptools" just means source.
- `sha256`: sha256 hash of the file.
- `hash`: hash of the file.
Really that's all it needs. Here's what it does with your inputs:

## for wheels:
First it constructs a url like this:
```
https://files.pythonhosted.org/packages/${dist}/${builtins.substring 0 1 pname}/${pname}/${pname}-${version}-${python}-${abi}-${platform}.whl";
```
The following arguments are customizable, just put it in the attribute set:
- `dist`: "py2.py3" by default
- `python`: "py2.py3" by default
- `abi`: "none" by default
- `platform`: "any" by default

Example:
```nix
fetchPypi {
  pname = "xxx";
  version = "y.zz";
  # sha256 and hash are just passed to `fetchurl`. If I'm not mistaken, sha256 is legacy, 
  # and using hash is sufficient.
  sha256 = "somehash";
  hash = "somehash";
  format = "wheel";

  # rest are optional
  dist = "somedist";
  python = "somepython";
  abi = "someabi";
  platform = "someplatform";
}
```
And it calls `fetchurl`, and return the derivation.

## for source:
It constructs a url like this:
```
mirror://pypi/${builtins.substring 0 1 pname}/${pname}/${pname}-${version}.${extension}";
```
The following arguments are customizable, just put it in the attribute set:
- `extension`: "tar.gz" by default

Example:
```nix
fetchPypi {
  pname = "xxx";
  version = "y.zz";
  # sha256 and hash are just passed to `fetchurl`. If I'm not mistaken, sha256 is legacy, 
  # and using hash is sufficient.
  sha256 = "somehash";
  hash = "somehash";

  # rest are optional
  format = "setuptools";
  extension = "someextension";
}
```
And it calls `fetchurl`, and return the derivation.
