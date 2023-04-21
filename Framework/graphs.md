# Graphs

## Graph

A `CalculatorGraphConfig` proto 指定 MediaPipe graph 的拓墣結構 (topology) 和功能 (functionality)。圖中**每個節點代表一個特別的 calculator 或 subgraph**，並且指定並要的配置 (configurations)，例如:

- registered calculator/subgraph type
- inputs
- outputs
- optional fields:
  - node-specific options
  - input policy
  - executor

    > discussed in [Synchronization](https://developers.google.com/mediapipe/framework/framework_concepts/synchronization)

`CalculatorGraphConfig` has several other fields to configure global graph-level settings, like:

- graph executor configs,
- number of threads
- maximum queue size of input streams

其中一些 graph-level 的設置對於調整 graph 在不同平台上的性能很有用，例如:

- on mobile: attaching a heavy model-inference calculator to a separate executor can improve the performance of a real-time application since this enables thread locality.

下面是 `CalculatorGraphConfig` 的範例，其中有好幾個 `passthrough calculators`:

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

MediaPipe offers an alternative C++ representation, like:

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

## Subgraph

為了將 `CalculatorGraphConfig` 模組化為 sub-modules 並可以 re-use of perception solutions，可以將 MediaPipe graph 定義為 `Subgraph`。Subgraph 的 public interface 由一組 input 和 output stream 組成，類似於 calculator's public interface。然後可以將 `Subgraph` 包含在 `CalculatorGraphConfig` 中，就好像是他的一個 calculator 一樣。當從 `CalculatorGraphConfig` 加載 MediaPipe graph 時，每個 subgraph 節點就會替換成相對應的 calculator graph。因此 subgraph 的語義和性能與相應的 calculator graph 相同。

下面是如何創建名為 `TwoPassThroughSubgraph` 的 subgraph 的範例:

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

2. Register the subgraph using BUILD rule `mediapipe_simple_subgraph`. The parameter `register_as` defines the component name for the new subgraph.

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
