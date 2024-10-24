# Custom Calculator

Detail code please see [mediapipe/kaka_examples/12_custom_calculator/](https://github.com/kaka-lin/mediapipe/blob/kaka/mediapipe/kaka_examples/12_custom_calculator/)

Usage:

```bash
$ bazel run --define MEDIAPIPE_DISABLE_GPU=1 \
    mediapipe/kaka_examples/12_custom_calculator:custom_calculator
```

## Step 1. Starting Create our Custom Calculator

在 MediaPipe 中，每個計算器都繼承自 `CalculatorBase` 類，該類定義了計算器的基本行為，包括:

- `GetContract()`: 返回計算器的輸入輸出契約，這個函數必須被實現。
- `Open()`: 初始化計算器。圖啟動後，框架會調用。
- `Process()`: 這個函數會在有新的數據到達時被調用。
- `Close()`: 這個函數會在計算器銷毀時被調用。

所以我們的 Calculator Class 必須繼承 `CalculatorBase`，並實現上面的行為函式。且實現完計算器後必須使用 `REGISTER_CALCULATOR` 註冊後才可以被使用。

以下我們實現了一個名為 `GoblinCalculator` 的計算器，它的功能是將輸入的整數乘以 2，並輸出結果，如下所示:

```cpp
#include "mediapipe/framework/calculator_framework.h"

namespace mediapipe {
  class GoblinCalculator : public CalculatorBase {
   public:
    // 計算器的 GetContract() 函數，定義計算器的輸入輸出契約
    static Status GetContract(CalculatorContract* cc) {
      // specify a calculator with 1 input, 1 output, both of type double
      cc->Inputs().Index(0).Set<double>();
      cc->Outputs().Index(0).Set<double>();
      return absl::OkStatus(); // Never forget to say "OK"!
    }

    // 計算器的處理函數，將輸入加上常數並輸出結果
    Status Process(CalculatorContext* cc) override {
      // Receive the input packet
      Packet p_in = cc->Inputs().Index(0).Value();

      // Extract the double number
      // A Packet is immutable, so we cannot edit it!
      double x = p_in.Get<double>();
      // Process the number
      double y = x * 2;

      // Create the output packet, with the input timestamp
      Packet p_out = MakePacket<double>(y).At(cc->InputTimestamp());
      // Send it to the output stream
      cc->Outputs().Index(0).AddPacket(p_out);
    }
  };

  // We must register our calculator with MP,
  // so that it can be used in graphs
  REGISTER_CALCULATOR(GoblinCalculator);
}  // namespace mediapipe
```

## Step 2. Configure a Graph and Create MediaPipe Graph

Configures a graph, which has one custom calculator GoblinCalculator.

```cpp
std::string k_proto = R"pbtxt(
    input_stream: "input"
    output_stream: "output"
    node {
      calculator: "GoblinCalculator"
      input_stream: "input"
      output_stream: "output"
    }
  )pb";
```

Next, parse this string into a protobuf CalculatorGraphConfig object

```cpp
CalculatorGraphConfig config;
  if (!ParseTextProto<CalculatorGraphConfig>(k_proto, &config)) {
    // mediapipe::Status is actually absl::Status (at least in the current mediapipe)
    // So we can create BAD statuses like this
    return absl::InternalError("Cannot parse the graph config !");
  }
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
