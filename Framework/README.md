# MediaPipe Framework

MediaPipe 是 Google 開源的一個 flow stream 處理框架，它支持在移動設備和桌面平台上實時進行影片、音訊、圖像等 data flow 的處理。

`MediaPipe Framework` is the **low-level component** used to build efficient on-device machine learning pipelines, similar to the premade [MediaPipe Solutions](https://developers.google.com/mediapipe/solutions/guide.md).

MediaPipe Framework support building application in C++, Android, and iOS.

> If you want to build Python application, you need to use [pybund11](https://pybind11.readthedocs.io/en/stable/index.html)

如果要更熟悉 MediaPipe Framework 可以看一下 `Framework concepts`:

- [Packets](./packets.md)
- [Graphs](./graphs.md)
- [Calculators](./calculators.md)

## Install MediaPipe Framework

在開始使用前我們須先安裝 MeidaPipe Framework，請參考: [install MediaPipe Framework](https://developers.google.com/mediapipe/framework/getting_started/install)

## Run the Hello World! C++ Example

為了更好的理解與學習 Mediapipe Framework，這邊我們 Fork 了一份並且從頭開始寫 example。

1. Clone the repo that I forked

    ```bash
    $ git clone https://github.com/kaka-lin/mediapipe.git
    ```

2. Run the Hello World! in C++ example

    ```bash
    $ export GLOG_logtostderr=1
    $ bazel run --define MEDIAPIPE_DISABLE_GPU=1 \
        mediapipe/kaka_examples/00_hello_world:hello_world
    ```

以下透過這個 Example Code 來學習 MediaPipe Framework，如下:

#### Step 1. Configure a Graph and Create MediaPipe Graph

首先要定義整個 MediaPipe 的 Topology (拓墣)。這個 Graph 是 protobuf 的格式，如下:

```proto
input_stream: "input"
output_stream: "output"
node {
  calculator: "PassThroughCalculator"
  input_stream: "input"
  output_stream: "output1"
}
node {
  calculator: "PassThroughCalculator"
  input_stream: "output1"
  output_stream: "output"
}
```

In C++

```c++
std::string proto = R"pbtxt(
  input_stream: "input"
  output_stream: "output"
  node {
    calculator: "PassThroughCalculator"
    input_stream: "input"
    output_stream: "output1"
  }
  node {
    calculator: "PassThroughCalculator"
    input_stream: "output1"
    output_stream: "output"
  }
)pbtxt";
```

再來我們需要 parse this string into [CalculatorGraphConfig](https://github.com/google/mediapipe/blob/master/mediapipe/framework/calculator.proto) object

```c++
CalculatorGraphConfig config =
  ParseTextProtoOrDie<CalculatorGraphConfig>(proto);
```

Create MediaPipe Graph and intialize it with config

```c++
CalculatorGraph graph;
MP_RETURN_IF_ERROR(graph.Initialize(config));
```

#### Step 2. Output Streams

在我們開始運行 Graph 之前，我們要如何接收整個 Graph 的 output，這邊有兩種方法:

1. `OutputStreamPoller`: synchronous logic
2. `ObserveOutputStream`: a callback, asynchronous logic

這邊範例使用 `OutputStreamPoller` 的方法來接收 Graph output，如下:

```c++
ASSIGN_OR_RETURN(OutputStreamPoller poller,
                 graph.AddOutputStreamPoller("output"));
```

#### Step 3. Run the Graph

運行 Graph

```c++
MP_RETURN_IF_ERROR(graph.StartRun({}));
```

Graph 啟動後，通常以平行執行緒 (parallel threads) 等待 input data

#### Step 4. Input Packets

使用 [MakePacket](https://github.com/google/mediapipe/blob/master/mediapipe/framework/packet.h) 來創造 packet，並使用 `AddPacketToInputStream` 將 input packet 發送到 input stream，如下:

```c++
for (int i = 0; i < 10; ++i) {
  MP_RETURN_IF_ERROR(graph.AddPacketToInputStream("input",
                     MakePacket<std::string>("Hello World!").At(Timestamp(i))));
}
```

再來就是關閉 input stream "input" 以完成圖形運行。 此時會向 MediaPipe 發出信號，表示不會再有 packets sent to input stream "input"。

```c++
MP_RETURN_IF_ERROR(graph.CloseInputStream("input"));
```

#### Step 5. Get the output packets

```c++
mediapipe::Packet packet;
while (poller.Next(&packet)) {
  std::cout << packet.Timestamp() << ": RECEIVED PACKET " << packet.Get<double>() << std::endl;
}
```

#### Step 6. Finish Graph

```c++
// Wait for the graph to finish, and return graph status
// = `MP_RETURN_IF_ERROR(graph.WaitUntilDone())` + `return mediapipe::OkStatus()`
return graph.WaitUntilDone();
```

## Reference

- [MediaPipe Framework | Google Developers](https://developers.google.com/mediapipe/framework)
