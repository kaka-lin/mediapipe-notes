# MediaPipe Solutions

`MediaPipe Solutions` 可以讓你快速的建立一個機器學習應用程式，他提供一些 pre-built 的 processing pipelines 使用，也可用 `Model Maker` 來客製化自己的 solution (transfer learning on default models)。

MediaPipe Solutions 整合了以下工具:

- [MediaPipe Legacy Solutions](https://google.github.io/mediapipe/solutions/solutions)
- [TensorFlow Lite Task Library](https://www.tensorflow.org/lite/inference_with_metadata/task_library/overview)
- [TensorFlow Lite Model Maker](https://www.tensorflow.org/lite/models/modify/model_maker)

且包含以下功能:

- `MediaPipe Tasks`: Low-code API to create and deploy advanced ML solutions across platforms.

- `MediaPipe Model Maker`: Low-code API to customize solutions using your own data.

- `MediaPipe Studio`: Visualize and benchmark solutions.

### Setup guide for Python

Building applications with MediaPipe Tasks requires the following development environment resources:

- Python 3.7-3.10
- PIP 19.0 or higher (>20.3 for macOS)
- For Macs using Apple silicon M1 and M2 chips, use the Rosetta Translation Environment. See the [Apple documentation](https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment/) for more information on Rosetta setup and usage.

Install the `MediaPipe package`:

```bash
$ pip install install mediapipe
```

After installing the package, import it into your development project.

```python3
import mediapipe as mp
```
