{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  packages = with pkgs; [
    python313
    python313Packages.pygobject3
    python313Packages.virtualenv
    gtk3
    gobject-introspection
    wayland
    vim
   # Libadwaita for modern GTK4 styling conventions (good practice to include).
    adwaita-icon-theme # Provides standard icons
    libadwaita

    # The Ayatana AppIndicator library and its GObject Introspection data.
    libayatana-appindicator
    libappindicator
    ];

  shellHook = ''
    VENV_DIR=".venv"

    if [ ! -d "$VENV_DIR" ]; then
      echo "Creating Python venv in $VENV_DIR..."
      python -m venv $VENV_DIR
    fi

    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate

    echo "Python version: $(python --version)"
    echo "Pip version: $(pip --version)"
  '';
}
