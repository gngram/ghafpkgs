# Copyright 2022-2025 TII (SSRC) and the Ghaf contributors
# SPDX-License-Identifier: Apache-2.0

{
  buildPythonApplication,
  setuptools,
  #wheel,
  gtk3,
  gtk4,
  gobject-introspection,
  libayatana-appindicator,
  wrapGAppsHook3,
  pygobject3,
}:

buildPythonApplication {
  pname = "ghaf_usb_applet";
  version = "0.1.0";
  src = ./ghaf_usb_applet;
  pyproject = true;

  nativeBuildInputs = [
    setuptools
    #wheel
    wrapGAppsHook3
    gobject-introspection
  ];

  buildInputs = [
    libayatana-appindicator
    gtk3
    gtk4
  ];
  propagatedBuildInputs = [
    pygobject3
  ];
}
