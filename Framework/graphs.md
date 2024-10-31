# Graphs

## Graph

`CalculatorGraphConfig` proto 會指定 MediaPipe graph 的拓墣結構 (topology) 和功能 (functionality)。圖中**每個節點代表一個特別的 calculator 或 subgraph**，並且指定並要的配置 (configurations)，例如:

- registered calculator/subgraph type (計算機/子圖表類型)
- inputs
- outputs
- optional fields:
  - node-specific options (節點專屬選項)
  - input policy (輸入政策)
  - executor (執行程式)

    > discussed in [Synchronization](https://developers.google.com/mediapipe/framework/framework_concepts/synchronization)

`CalculatorGraphConfig` 還有其他幾個欄位可用於設定全域圖表層級，如：

- graph executor configs (圖形執行器設)
- number of threads (執行緒數量)
- maximum queue size of input streams (輸入串流的佇列大小上限)

你可以運用幾種圖表層級設定來調整圖表在不同平台上 (例如桌機和行動裝置) 的成效。如以行動裝置為例:

- attaching a heavy model-inference calculator to a separate executor can improve the performance of a real-time application since this enables thread locality.

下面是簡單的 `CalculatorGraphConfig` 的範例，其中有好幾個 `passthrough calculators`:

```proto
# This graph named main_pass_throughcals_nosubgraph.pbtxt
# contains 4 passthrough calculators.
input_stream: "in"
output_stream: "out"
node {
    calculator: "PassThroughCalculator"
    input_stream: "in"
    output_stream: "out1"
}
node {
    calculator: "PassThroughCalculator"
    input_stream: "out1"
    output_stream: "out2"
}
node {
    calculator: "PassThroughCalculator"
    input_stream: "out2"
    output_stream: "out3"
}
node {
    calculator: "PassThroughCalculator"
    input_stream: "out3"
    output_stream: "out"
}
```

MediaPipe 可為複雜圖表提供替代的 `C++` 表示法，例如: 機器學習管道 (ML pipelines)、處理模型中繼資料 (handling model metadata) 和選用節點 (optional nodes) 等。上圖看起來可能像這樣：

```cpp
CalculatorGraphConfig BuildGraphConfig() {
  Graph graph;

  // Graph inputs
  Stream<AnyType> in = graph.In(0).SetName("in");

  auto pass_through_fn = [](Stream<AnyType> in,
                            Graph& graph) -> Stream<AnyType> {
    auto& node = graph.AddNode("PassThroughCalculator");
    in.ConnectTo(node.In(0));
    return node.Out(0);
  };

  Stream<AnyType> out1 = pass_through_fn(in, graph);
  Stream<AnyType> out2 = pass_through_fn(out1, graph);
  Stream<AnyType> out3 = pass_through_fn(out2, graph);
  Stream<AnyType> out4 = pass_through_fn(out3, graph);

  // Graph outputs
  out4.SetName("out").ConnectTo(graph.Out(0));

  return graph.GetConfig();
}
```

詳情請參閱在 [C++ 中建構圖表](./graphs_cplusplus.md)。

## Subgraph (子圖表)

為了將 `CalculatorGraphConfig` 模組化模組化為子模組，並可以重複使用的觀感解決方案，可以將 MediaPipe graph 定義為 `Subgraph`。Subgraph 的 public interface 由一組 input 和 output stream 組成，類似於 calculator's public interface。然後可以將 `Subgraph` 加入 `CalculatorGraphConfig` 中，就像計算機 (calculators) 一樣。當從 `CalculatorGraphConfig` 加載 MediaPipe graph 時，每個 subgraph 節點就會替換成相對應的 calculator graph。因此 subgraph 的語義和性能與相應的 calculator graph 相同。

以下範例說明如何建立名為 `TwoPassThroughSubgraph` 的子圖表。

1. Defining the subgraph.

    ```proto
    # This subgraph is defined in two_pass_through_subgraph.pbtxt
    # and is registered as "TwoPassThroughSubgraph"

    type: "TwoPassThroughSubgraph"
    input_stream: "out1"
    output_stream: "out3"

    node {
        calculator: "PassThroughCalculator"
        input_stream: "out1"
        output_stream: "out2"
    }
    node {
        calculator: "PassThroughCalculator"
        input_stream: "out2"
        output_stream: "out3"
    }
    ```

    The public interface to the subgraph consists of:

    - Graph input streams
    - Graph output streams
    - Graph input side packets
    - Graph output side packets

2. 使用 BUILD 規則 `mediapipe_simple_subgraph` 註冊子圖表。 `register_as` 參數會定義新子圖表的元件名稱

    ```proto
    # Small section of BUILD file for registering the "TwoPassThroughSubgraph"
    # subgraph for use by main graph main_pass_throughcals.pbtxt

    mediapipe_simple_subgraph(
        name = "twopassthrough_subgraph",
        graph = "twopassthrough_subgraph.pbtxt",
        register_as = "TwoPassThroughSubgraph",
        deps = [
                "//mediapipe/calculators/core:pass_through_calculator",
                "//mediapipe/framework:calculator_graph",
        ],
    )
    ```

3.  Use the subgraph in the main graph.

    ```proto
    # This main graph is defined in main_pass_throughcals.pbtxt
    # using subgraph called "TwoPassThroughSubgraph"

    input_stream: "in"
    node {
        calculator: "PassThroughCalculator"
        input_stream: "in"
        output_stream: "out1"
    }
    node {
        calculator: "TwoPassThroughSubgraph"
        input_stream: "out1"
        output_stream: "out3"
    }
    node {
        calculator: "PassThroughCalculator"
        input_stream: "out3"
        output_stream: "out4"
    }
    ```

### Build subgraph in C++

```cpp
class TwoPassThroughSubgraph : public Subgraph {
 public:
  absl::StatusOr<CalculatorGraphConfig> GetConfig(
      SubgraphContext* context) override {
    // 使用 Graph Builder API 構建子圖
    Graph graph;

    // Graph inputs
    auto in = graph.In(0).SetName("out1");

    // 定義第一個 PassThroughCalculator
    auto& node1 = graph.AddNode("PassThroughCalculator");
    in >> node1.In(0);
    auto out2 = node1.Out(0);

    // 定義第二個 PassThroughCalculator
    auto& node2 = graph.AddNode("PassThroughCalculator");
    out2 >> node2.In(0);
    node2.Out(0).SetName("out3") >> graph.Out(0);

    return graph.GetConfig();
  }
};
REGISTER_MEDIAPIPE_GRAPH(TwoPassThroughSubgraph);

CalculatorGraphConfig BuildGraphConfig() {
    // 使用 Graph Builder API
    Graph graph;

    // Graph inputs
    auto in= graph.In(0).SetName("in");

    // 添加四個 PassThroughCalculator 並連接
    auto& node1 = graph.AddNode("PassThroughCalculator");
    in >> node1.In(0);
    auto out1 = node1.Out(0);

    auto& node2 = graph.AddNode("TwoPassThroughSubgraph");
    out1 >> node2.In(0);
    auto out3 = node2.Out(0);

    auto& node4 = graph.AddNode("PassThroughCalculator");
    out3 >> node4.In(0);
    node4.Out(0).SetName("out") >> graph.Out(0);

    return graph.GetConfig();
}
```

## Graph Options (圖表選項)

It is possible to specify a `"graph options" `protobuf for a MediaPipe graph similar to the [Calculator Options](https://ai.google.dev/edge/mediapipe/framework/framework_concepts/calculators#calculator_options) protobuf specified for a MediaPipe calculator. These `"graph options"` can be specified where a graph is invoked, and used to populate `calculator options` and `subgraph options` within the graph.

在 `CalculatorGraphConfig` 中，可以指定子圖表的 graph option，其與 calculator option 完全相同，如下所示：

```proto
node {
  calculator: "FlowLimiterCalculator"
  input_stream: "image"
  output_stream: "throttled_image"
  node_options: {
    [type.googleapis.com/mediapipe.FlowLimiterCalculatorOptions] {
      max_in_flight: 1
    }
  }
}

node {
  calculator: "FaceDetectionSubgraph"
  input_stream: "IMAGE:throttled_image"
  node_options: {
    [type.googleapis.com/mediapipe.FaceDetectionOptions] {
      tensor_width: 192
      tensor_height: 192
    }
  }
}
```

In a `CalculatorGraphConfig`, `graph options` can be accepted and used to populate calculator options, as shown below:

```proto
graph_options: {
  [type.googleapis.com/mediapipe.FaceDetectionOptions] {}
}

node: {
  calculator: "ImageToTensorCalculator"
  input_stream: "IMAGE:image"
  node_options: {
    [type.googleapis.com/mediapipe.ImageToTensorCalculatorOptions] {
        keep_aspect_ratio: true
        border_mode: BORDER_ZERO
    }
  }
  option_value: "output_tensor_width:options/tensor_width"
  option_value: "output_tensor_height:options/tensor_height"
}


node {
  calculator: "InferenceCalculator"
  node_options: {
    [type.googleapis.com/mediapipe.InferenceCalculatorOptions] {}
  }
  option_value: "delegate:options/delegate"
  option_value: "model_path:options/model_path"
}
```

In this example, the `FaceDetectionSubgraph` accepts graph option protobuf `FaceDetectionOptions`. The `FaceDetectionOption`s is used to define some field values in the calculator options `ImageToTensorCalculatorOptions` and some field values in the subgraph options `InferenceCalculatorOptions`. The field values are defined using the `option_value`: syntax.
