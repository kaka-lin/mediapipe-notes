# Simplest mediapipe pipeline

This is similar to the "C++ Hello World example".

Detail code please see [mediapipe/kaka_examples/11_simple_pipeline](https://github.com/kaka-lin/mediapipe/tree/kaka/mediapipe/kaka_examples/11_simple_pipeline)

Usage:

```bash
$ bazel run --define MEDIAPIPE_DISABLE_GPU=1 \
    mediapipe/kaka_examples/11_simple_pipeline:simple_pipeline
```

## Step 1. Configure a Graph and Create MediaPipe Graph

Configures a graph, which concatenates 2 `PassThroughCalculators`. First, we have to create MediePipe graph as protobuf text format

```cpp
std::string k_proto = R"pbtxt(
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

Next, parse this string into a protobuf CalculatorGraphConfig object

```cpp
CalculatorGraphConfig config =
  ParseTextProtoOrDie<CalculatorGraphConfig>(k_proto);
```

Create MediaPipe Graph and intialize it with config

```cpp
CalculatorGraph graph;
MP_RETURN_IF_ERROR(graph.Initialize(config));
```

## Step 2. Output Streams

這邊範例使用 `OutputStreamPoller` 的方法來接收 Graph output，如下:

```cpp
// old version
// ASSIGN_OR_RETURN(OutputStreamPoller poller,
//                  graph.AddOutputStreamPoller("output"));

// new api version
MP_ASSIGN_OR_RETURN(OutputStreamPoller poller,
                   graph.AddOutputStreamPoller("output"));
```

## Step 3. Run the graph

Run the graph with `StartRun`.

```cpp
MP_RETURN_IF_ERROR(graph.StartRun({}));
```

Graph 啟動後，通常以平行執行緒 (parallel threads) 等待 input data

## Step 4. Input Packets

使用 [MakePacket](https://github.com/google/mediapipe/blob/master/mediapipe/framework/packet.h) 來創造 packet，並使用 `AddPacketToInputStream` 將 input packet 發送到 input stream，如下:

```cpp
for (int i = 0; i < 13; ++i) {
  MP_RETURN_IF_ERROR(graph.AddPacketToInputStream("input",
                     MakePacket<double>(i*0.1).At(Timestamp(i))));
}
```

再來就是關閉 input stream "input" 以完成圖形運行。 此時會向 MediaPipe 發出信號，表示不會再有 packets sent to input stream "input"。

```cpp
MP_RETURN_IF_ERROR(graph.CloseInputStream("input"));
```

## Step 5. Get the output packets

```cpp
mediapipe::Packet packet;
while (poller.Next(&packet)) {
  std::cout << packet.Timestamp() << ": RECEIVED PACKET " << packet.Get<double>() << std::endl;
}
```

## Step 6. Finish graph

Wait for the graph to finish, and return graph status

```cpp
// = `MP_RETURN_IF_ERROR(graph.WaitUntilDone())`
// + `return mediapipe::OkStatus()`
return graph.WaitUntilDone();
```

## Reference

- [agrechnev/first_steps_mediapipe](https://github.com/agrechnev/first_steps_mediapipe/tree/master/first_steps)
