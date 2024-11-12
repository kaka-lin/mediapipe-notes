# Setup guide for Python

## Supported platforms and versions

Building applications with MediaPipe Tasks requires the following development environment resources:

- Python: 3.9-3.12
- PIP: 20.3 以上
- For Macs using Apple silicon M1 and M2 chips, use the Rosetta Translation Environment. See the [Apple documentation](https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment/) for more information on Rosetta setup and usage.

## Developer environment setup

Install the `MediaPipe package`:

```bash
$ pip install install mediapipe
```

After installing the package, import it into your development project.

```python3
import mediapipe as mp
```

## MediaPipe Tasks dependencies

MediaPipe Tasks provides three prebuilt libraries for `vision`, `text`, `audio`. Depending on the MediaPipe Task used by the app, import the vision, text, or audio library into your development project.

### Vision tasks

```python
from mediapipe.tasks.python import vision
```

### Text tasks

```python
from mediapipe.tasks.python import text
```

### Audio tasks

```python
from mediapipe.tasks.python import audio
```

## BaseOptions configutation

The BaseOptions allow for general configuration of `MediaPipe Task APIs`.

| Option name | Description | Accepted values |
| :--: | :--:| :--: |
| **model_asset_buffer** | The model asset file contents. | Model content as a byte string |
| **model_asset_path** | The path of the model asset to open and map into memory. | File path as a string |

