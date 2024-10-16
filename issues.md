# MediaPipe Issues

## 1. Only Support OpenCV 3.x now

如果使用 OpenCV 4.x 運行程式會發生 `Segmentation fault`, 如: [mediapipe/issues/5656](https://github.com/google-ai-edge/mediapipe/issues/5655)。
又因:

1. macOS `brew install opencv` 已經升版至 4.x
2. `brew install opencv@3` already disabled/deprecated.

所以必須 install opencv from source 如下:


- 安裝 CMake 和其他 library

    ```sh
    $ brew install cmake pkg-config
    $ brew install jpeg libpng libtiff openexr
    $ brew install eigen tbb
    ```
- Install OpenCV 3.x from source

    ```sh
    $ git clone https://github.com/opencv/opencv.git
    $ cd opencv
    $ git checkout 3.4.16
    $ mkdir build && cd build
    $ cmake -D CMAKE_BUILD_TYPE=Release \
            -D CMAKE_INSTALL_PREFIX=/opt/opencv ..
    $ make -j4
    $ sudo make install
    ```

- 更新環境變數

    ```sh
    # pkg-config
    export PKG_CONFIG_PATH=/opt/opencv/lib/pkgconfig:$PKG_CONFIG_PATH

    # OpenCV 動態 library
    export DYLD_LIBRARY_PATH=/opt/opencv/lib:$DYLD_LIBRARY_PATH
    ```
