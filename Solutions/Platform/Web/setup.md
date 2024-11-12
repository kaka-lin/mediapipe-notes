# Setup guide for web

## Supported platforms and versions

To create web applications with MediaPipe Tasks, your development environment requires the following:

- Chrome or Safari browser
- A web application that uses Node.js and NPM. Alternatively, you can use script tags to access MediaPipe Tasks through a content delivery network (CDN).

## MediaPipe Tasks dependencies

MediaPipe Tasks provides three prebuilt libraries for `vision`, `text`, `audio`. Depending on the MediaPipe Task used by the app, import the vision, text, or audio library into your development project.

### Generative AI tasks

The MediaPipe Tasks Generative AI module contains tasks that handle image or text generation. To import the MediaPipe Tasks Generative AI libraries, import the following dependencies into your development project.

#### LLM Inference API

The MediaPipe LLM Inference task is contained within the `tasks-genai` library.

```sh
$ npm install @mediapipe/tasks-genai
```

### Vision tasks

```sh
$ npm install @mediapipe/tasks-vision
```

### Text tasks

```sh
$ npm install @mediapipe/tasks-text
```

### Audio tasks

```sh
$ npm install @mediapipe/tasks-audio
```

## BaseOptions configutation

The BaseOptions allow for general configuration of `MediaPipe Task APIs`.

| Option name | Description | Accepted values |
| :--: | :--:| :--: |
| **modelAssetBuffer** | The model asset file contents as a **Uint8Array** typed array. | **Uint8Array**  |
| **modelAssetPath** | The path of the model asset to open and map into memory. | **TrustedResourceUrl** |
| **Delegate** | Enables hardware acceleration through a device delegate to run the MediaPipe pipeline. Default value: **`CPU`**. | [CPU, GPU]|
