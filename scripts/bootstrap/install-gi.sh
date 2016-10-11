PYCAIRO_VERSION="1.10.0"
PYCAIRO_URL="https://cairographics.org/releases/pycairo-$PYCAIRO_VERSION.tar.bz2"

PYGOBJECT_VERSION="3.12.2"
PYGOBJECT_URL="http://ftp.gnome.org/pub/GNOME/sources/pygobject/3.12/pygobject-$PYGOBJECT_VERSION.tar.xz"

export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig"


##
# Downloads an unpacks pycairo.
cairo_download() {
    curl \
        --location \
        "$PYCAIRO_URL" | tar xj
}


##
# Builds pycairo.
cairo_build() {
    # We need to be inside the pycairo download directory
    cd "pycairo-$PYCAIRO_VERSION"

    # Ensure that only one directory matching .waf3-* exists; it will be created
    # below
    rm -rf .waf3-*

    # This will fail; bufix: https://bugs.freedesktop.org/show_bug.cgi?id=76759
    python waf configure --prefix="$PREFIX" || true
    sed -i '154s/data={}/return/' .waf3-*/waflib/Build.py

    # Now it should configure
    python waf configure --prefix="$PREFIX"
    python waf build
    python waf install

    cd ..
}


##
# Downloads and unpacks pygobject.
pygobject_download() {
    curl \
        --location \
        "$PYGOBJECT_URL" | tar xJ
}


##
# Builds pygobject
pygobject_build() {
    # We need to be inside the pygobject download directory
    cd "pygobject-$PYGOBJECT_VERSION"

    # Configure, build and install
    ./configure CFLAGS="-I$PREFIX/include" --prefix=$PREFIX
    make
    make install

    cd ..
}


echo "Downloading pycairo..."
cairo_download 1>/dev/null 2>&1

echo "Building pycairo..."
cairo_build 1>/dev/null

echo "Downloading pygobject..."
pygobject_download 1>/dev/null 2>&1

echo "Building pygobject..."
pygobject_build
