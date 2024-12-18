# 在 C++ 中建構圖表的傳統方式

## Example 1: Simple Pipeline

> 實際運行請至: [mediapipe/kaka_examples/graph_in_cpp/11_simple_pipeline](https://github.com/kaka-lin/mediapipe/tree/kaka/mediapipe/kaka_examples/graph_in_cpp/11_simple_pipeline)

以下介紹 `CalculatorGraphConfig` 的寫法，並附上相對的 `Graph Builder API` 的寫法。

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

### 1. 使用 CalculatorGraphConfig 的範例

```cpp
#include "mediapipe/framework/calculator_framework.h"

mediapipe::CalculatorGraphConfig BuildGraphConfig() {
    mediapipe::CalculatorGraphConfig config;

    // 定義輸入和輸出流
    config.add_input_stream("in");
    config.add_output_stream("out");

    // 第一個 PassThroughCalculator 節點
    auto* node1 = config.add_node();
    node1->set_calculator("PassThroughCalculator");
    node1->add_input_stream("in");
    node1->add_output_stream("out1");

    // 第二個 PassThroughCalculator 節點
    auto* node2 = config.add_node();
    node2->set_calculator("PassThroughCalculator");
    node2->add_input_stream("out1");
    node2->add_output_stream("out2");

    // 第三個 PassThroughCalculator 節點
    auto* node3 = config.add_node();
    node3->set_calculator("PassThroughCalculator");
    node3->add_input_stream("out2");
    node3->add_output_stream("out3");

    // 第四個 PassThroughCalculator 節點
    auto* node4 = config.add_node();
    node4->set_calculator("PassThroughCalculator");
    node4->add_input_stream("out3");
    node4->add_output_stream("out");

    return config;
}
```

### 2. 使用 Graph Builder API 的範例

有兩種寫法。

#### 寫法 1: 使用 Stream 類型

```cpp
#include "mediapipe/framework/calculator_framework.h"
#include "mediapipe/framework/api2/builder.h"

using ::mediapipe::api2::Input;
using ::mediapipe::api2::Output;
using ::mediapipe::api2::builder::Graph;

CalculatorGraphConfig BuildGraphConfig() {
    // 使用 Graph Builder API
    Graph graph;

    // 定義輸入和輸出流
    auto in= graph.In(0).SetName("in");
    auto out= graph.Out(0);

    // 添加四個 PassThroughCalculator 並連接
    auto& node1 = graph.AddNode("PassThroughCalculator");
    in >> node1.In(0);
    auto out1 = node1.Out(0);

    auto& node2 = graph.AddNode("PassThroughCalculator");
    out1 >> node2.In(0);
    auto out2 = node2.Out(0);

    auto& node3 = graph.AddNode("PassThroughCalculator");
    out2 >> node3.In(0);
    auto out3 = node3.Out(0);

    auto& node4 = graph.AddNode("PassThroughCalculator");
    out3 >> node4.In(0);
    node4.Out(0).SetName("out") >> out;

    return graph.GetConfig();
}
```

#### 寫法 2: 使用函數

```cpp
#include "mediapipe/framework/calculator_framework.h"
#include "mediapipe/framework/api2/builder.h"

using ::mediapipe::api2::Input;
using ::mediapipe::api2::Output;
using ::mediapipe::api2::builder::Graph;
using ::mediapipe::api2::builder::Stream;
using ::mediapipe::api2::AnyType;

CalculatorGraphConfig BuildGraphConfig() {
    // 使用 Graph Builder API
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

## Example 2: Subgraph

> 實際運行請至: [mediapipe/kaka_examples/graph_in_cpp/12_subgraph](https://github.com/kaka-lin/mediapipe/tree/kaka/mediapipe/kaka_examples/graph_in_cpp/12_subgraph)

子圖表

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

在主圖中使用子圖表

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

### 1. 使用 CalculatorGraphConfig 的範例

```cpp
#include "mediapipe/framework/calculator_framework.h"

class TwoPassThroughSubgraph : public Subgraph {
 public:
  absl::StatusOr<CalculatorGraphConfig> GetConfig(
      SubgraphContext* context) override {
    CalculatorGraphConfig config;

    // 定義輸入和輸出標籤
    config.add_input_stream("out1");
    config.add_output_stream("out3");

    // 定義第一個 PassThroughCalculator 節點
    auto* node1 = config.add_node();
    node1->set_calculator("PassThroughCalculator");
    node1->add_input_stream("out1");
    node1->add_output_stream("out2");

    // 定義第二個 PassThroughCalculator 節點
    auto* node2 = config.add_node();
    node2->set_calculator("PassThroughCalculator");
    node2->add_input_stream("out2");
    node2->add_output_stream("out3");

    return config;
  }
};
REGISTER_MEDIAPIPE_GRAPH(TwoPassThroughSubgraph);

CalculatorGraphConfig BuildGraphConfig() {
    mediapipe::CalculatorGraphConfig config;

    // 定義輸入和輸出流
    config.add_input_stream("in");
    config.add_output_stream("out");

    // 第一個 PassThroughCalculator 節點
    auto* node1 = config.add_node();
    node1->set_calculator("PassThroughCalculator");
    node1->add_input_stream("in");
    node1->add_output_stream("out1");

    // 使用 TwoPassThroughSubgraph 子圖
    auto* subgraph_node = config.add_node();
    subgraph_node->set_calculator("TwoPassThroughSubgraph");
    subgraph_node->add_input_stream("out1");
    subgraph_node->add_output_stream("out3");

    // 第三個 PassThroughCalculator 節點
    auto* node4 = config.add_node();
    node4->set_calculator("PassThroughCalculator");
    node4->add_input_stream("out3");
    node4->add_output_stream("out");

    return config;
}
```

### 2. 使用 Graph Builder API 的範例

```cpp
#include "mediapipe/framework/calculator_framework.h"
#include "mediapipe/framework/api2/builder.h"

using ::mediapipe::api2::Input;
using ::mediapipe::api2::Output;
using ::mediapipe::api2::builder::Graph;

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
