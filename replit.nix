{ pkgs }: {
  deps = [
    pkgs.libopus.out
    pkgs.ffmpeg.bin
    pkgs.sudo
    pkgs.nodePackages.prettier
    pkgs.python38Full
    pkgs.replitPackages.prybar-python3
    pkgs.libuuid
  ];
  env = rec {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libopus.out
      # Needed for pandas / numpy
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      # Needed for pygame
      pkgs.glib
      # Needed for matplotlib
      pkgs.xorg.libX11
        
    ];
    PYTHONBIN = "${pkgs.python38Full}/bin/python3.8";
    OPUS_PATH = "${pkgs.libopus.out}/lib";
    LANG = "en_US.UTF-8";
  };
}