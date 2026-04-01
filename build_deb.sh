#!/bin/bash
set -e
PKG="countdown-timer"
VER="1.0"
ARCH="all"
BUILD_DIR="/tmp/${PKG}_${VER}_${ARCH}"
OUT_DEB="${PKG}_${VER}_${ARCH}.deb"
echo "=== Building ${PKG}_${VER}.deb ==="
if [ ! -f "countdown.py" ]; then echo "ERROR: countdown.py not found"; exit 1; fi
if [ ! -f "countdown.png" ]; then HAS_ICON=false; else echo "Found countdown.png"; HAS_ICON=true; fi
if ! command -v dpkg-deb &>/dev/null; then sudo apt-get install -y dpkg-dev; fi
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/countdown_timer"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"
cp countdown.py "$BUILD_DIR/opt/countdown_timer/countdown.py"
if [ "$HAS_ICON" = true ]; then cp countdown.png "$BUILD_DIR/usr/share/pixmaps/countdown-timer.png"; ICON_LINE="Icon=/usr/share/pixmaps/countdown-timer.png"; else ICON_LINE="Icon=appointment-soon"; fi
cat > "$BUILD_DIR/usr/share/applications/countdown-timer.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Countdown Timer
Comment=Always-on-top circular countdown timer
Exec=python3 /opt/countdown_timer/countdown.py
${ICON_LINE}
Terminal=false
Categories=Utility;
StartupNotify=false
EOF
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: ${PKG}
Version: ${VER}
Architecture: ${ARCH}
Maintainer: Your Name <your@email.com>
Depends: python3 (>= 3.8), python3-tk
Description: Circular Countdown Timer
 A floating always-on-top countdown timer with circular progress ring.
EOF
printf '#!/bin/bash\nchmod +x /opt/countdown_timer/countdown.py\nupdate-desktop-database /usr/share/applications/ 2>/dev/null || true\n' > "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
printf '#!/bin/bash\nrm -rf /opt/countdown_timer\nupdate-desktop-database /usr/share/applications/ 2>/dev/null || true\n' > "$BUILD_DIR/DEBIAN/postrm"
chmod 755 "$BUILD_DIR/DEBIAN/postrm"
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$OUT_DEB"
echo ""
echo "SUCCESS: ${OUT_DEB} created in $(pwd)"
