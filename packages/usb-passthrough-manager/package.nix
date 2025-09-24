# Copyright 2022-2025 TII (SSRC) and the Ghaf contributors
# SPDX-License-Identifier: Apache-2.0

{
  buildPythonApplication,
  setuptools,
  wheel,
  gtk4,
  gobject-introspection,
  wrapGAppsHook,
  gsettings-desktop-schemas,
  pygobject3,
  vsock-bridge,
  vhotplug-schemas,
}:

buildPythonApplication {
  pname = "usb_passthrough_manager";
  version = "0.1.0";
  src = ./usb_passthrough_manager;
  pyproject = true;

  nativeBuildInputs = [
    setuptools
    wheel
    gobject-introspection
    wrapGAppsHook
  ];

  propagatedBuildInputs = [
    pygobject3
    vsock-bridge
  ];

  buildInputs = [
    gtk4
    gsettings-desktop-schemas
  ];
}
