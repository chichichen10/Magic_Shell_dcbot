{ pkgs }: {
  deps = [
    pkgs.libsodium
    pkgs.ffmpeg-full
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.openjpeg
    pkgs.libxcrypt
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.freetype
      pkgs.ffmpeg.bin
  ];
  env = rec {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libsodium
      pkgs.tk
      pkgs.tcl
      pkgs.openjpeg
      pkgs.libxcrypt
      pkgs.libwebp
      pkgs.libimagequant
      pkgs.freetype
      pkgs.libopus.out
      # Needed for pandas / numpy
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      # Needed for pygame
      pkgs.glib
      # Needed for matplotlib
      pkgs.xorg.libX11

    ];
    OPUS_PATH = "${pkgs.libopus.out}/lib";
    LANG = "en_US.UTF-8";
  };

}
