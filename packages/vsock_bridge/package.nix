# Copyright 2022-2025 TII (SSRC) and the Ghaf contributors
# SPDX-License-Identifier: Apache-2.0

{
  buildPythonPackage,
  setuptools,
  wheel,
}:

buildPythonPackage {
  pname = "vsock-bridge";
  version = "0.0.1";
  src = ./vsock-bridge;
  pyproject = true;

  nativeBuildInputs = [
    setuptools
    wheel
  ];
}
