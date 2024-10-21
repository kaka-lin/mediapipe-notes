# 使用 C++ 建構圖表 (Building Graphs in C++)

C++ 圖表建構工具 (graph builder) 是一款強大的工具，適用於:

- 建構複雜的圖表 (Building complex graphs)
- 參數化圖表，例如:
  - 在 InferenceCalculator 上設定`委派代表 (delegate)`
  - 啟用/停用部分圖表
- 刪除重複的圖表 (Deduplicating graphs)，例如:
  - 使用單一程式碼來建立所需的圖，取代 `pbtxt` 中的 CPU 和 GPU 的 專屬 (dedicated) 圖表，如:
    - detection_mobile_cpu.pbtxt
    - detection_mobile_gpu.pbtxt

    且盡可能的共用。

- 支援選用圖形輸入/輸出 (Supporting optional graph inputs/outputs)
- 依平台自訂圖表 (Customizing graphs per platform)

## 基本用法 (Basic Usage)

以下是 C++ 圖表建構工具如何用於簡單的圖表的範例:

```proto
# Graph inputs.
input_stream: "input_tensors"
input_side_packet: "model"

# Graph outputs.
output_stream: "output_tensors"

node {
  calculator: "InferenceCalculator"
  input_stream: "TENSORS:input_tensors"
  input_side_packet: "MODEL:model"
  output_stream: "TENSORS:output_tensors"
  options: {
    [drishti.InferenceCalculatorOptions.ext] {
      # Requesting GPU delegate.
      delegate { gpu {} }
    }
  }
}
```

建構上述 `CalculatorGraphConfig` 的函式可能如下所示:

```cpp
CalculatorGraphConfig BuildGraph() {
  Graph graph;

  // Graph inputs.
  Stream<std::vector<Tensor>> input_tensors =
      graph.In(0).SetName("input_tensors").Cast<std::vector<Tensor>>();
  SidePacket<TfLiteModelPtr> model =
      graph.SideIn(0).SetName("model").Cast<TfLiteModelPtr>();

  // inference node
  auto& inference_node = graph.AddNode("InferenceCalculator");
  auto& inference_opts =
      inference_node.GetOptions<InferenceCalculatorOptions>();

  // Requesting GPU delegate.
  inference_opts.mutable_delegate()->mutable_gpu();
  input_tensors.ConnectTo(inference_node.In("TENSORS"));
  model.ConnectTo(inference_node.SideIn("MODEL"));

  // Get mode's output from inference node
  Stream<std::vector<Tensor>> output_tensors =
      inference_node.Out("TENSORS").Cast<std::vector<Tensor>>();

  // Graph outputs.
  output_tensors.SetName("output_tensors").ConnectTo(graph.Out(0));

  // Get `CalculatorGraphConfig` to pass it into `CalculatorGraph`
  return graph.GetConfig();
}
```

- `Graph::In/SideIn`: get graph inputs as `Stream/SidePacket`

- `Node::Out/SideOut`: get node outputs as `Stream/SidePacket`

- `Stream/SidePacket::ConnectTo`: 將 streams 和 side packets 連接至 node inputs (`Node::In/SideIn`) 和 graph outputs (`Graph::Out/SideOut`)

  - There's a "shortcut" operator `>>`，可用於取代 `ConnectTo` 函式 (例如 `x >> node.In("IN")`)。
- `Stream/SidePacket::Cast`: 型態轉換

## 進階用法 (Advanced Usage)

### 公用函式 (Utility Functions)

讓我們將`推理建構程式碼 (Inference)` 提取到專屬的公用函式中，以幫助提高可讀性和程式碼重複使用:

```cpp
Stream<std::vector<Tensor>> RunInference(
    Stream<std::vector<Tensor>> tensors, SidePacket<TfLiteModelPtr> model,
    const InferenceCalculatorOptions::Delegate& delegate, Graph& graph) {

  // inference node
  auto& inference_node = graph.AddNode("InferenceCalculator");
  auto& inference_opts =
      inference_node.GetOptions<InferenceCalculatorOptions>();

  // Requesting GPU delegate.
  *inference_opts.mutable_delegate() = delegate;
  tensors.ConnectTo(inference_node.In("TENSORS"));
  model.ConnectTo(inference_node.SideIn("MODEL"));

  // return mode's output from inference node
  return inference_node.Out("TENSORS").Cast<std::vector<Tensor>>();
}


CalculatorGraphConfig BuildGraph() {
  Graph graph;

  // Graph inputs.
  Stream<std::vector<Tensor>> input_tensors =
      graph.In(0).SetName("input_tensors").Cast<std::vector<Tensor>>();
  SidePacket<TfLiteModelPtr> model =
      graph.SideIn(0).SetName("model").Cast<TfLiteModelPtr>();

  // Inferenece method
  InferenceCalculatorOptions::Delegate delegate;
  delegate.mutable_gpu();
  Stream<std::vector<Tensor>> output_tensors =
      RunInference(input_tensors, model, delegate, graph);

  // Graph outputs.
  output_tensors.SetName("output_tensors").ConnectTo(graph.Out(0));

  // Get `CalculatorGraphConfig` to pass it into `CalculatorGraph`
  return graph.GetConfig();
}
```

### 公用程式類別 (Utility Classes)

And surely, it's not only about functions, in some cases it's beneficial to introduce `utility classes` which can help making your graph construction code `more readable and less error prone`.

MediaPipe offers `PassThroughCalculator` calculator, which is simply passing through its inputs:

```proto
input_stream: "float_value"
input_stream: "int_value"
input_stream: "bool_value"

output_stream: "passed_float_value"
output_stream: "passed_int_value"
output_stream: "passed_bool_value"

node {
  calculator: "PassThroughCalculator"
  input_stream: "float_value"
  input_stream: "int_value"
  input_stream: "bool_value"
  # The order must be the same as for inputs (or you can use explicit indexes)
  output_stream: "passed_float_value"
  output_stream: "passed_int_value"
  output_stream: "passed_bool_value"
}
```

我們來看看建立上方圖表的簡單 C++ 建構程式碼:

```cpp
CalculatorGraphConfig BuildGraph() {
  Graph graph;

  // Graph inputs.
  Stream<float> float_value = graph.In(0).SetName("float_value").Cast<float>();
  Stream<int> int_value = graph.In(1).SetName("int_value").Cast<int>();
  Stream<bool> bool_value = graph.In(2).SetName("bool_value").Cast<bool>();

  auto& pass_node = graph.AddNode("PassThroughCalculator");
  float_value.ConnectTo(pass_node.In("")[0]);
  int_value.ConnectTo(pass_node.In("")[1]);
  bool_value.ConnectTo(pass_node.In("")[2]);
  Stream<float> passed_float_value = pass_node.Out("")[0].Cast<float>();
  Stream<int> passed_int_value = pass_node.Out("")[1].Cast<int>();
  Stream<bool> passed_bool_value = pass_node.Out("")[2].Cast<bool>();

  // Graph outputs.
  passed_float_value.SetName("passed_float_value").ConnectTo(graph.Out(0));
  passed_int_value.SetName("passed_int_value").ConnectTo(graph.Out(1));
  passed_bool_value.SetName("passed_bool_value").ConnectTo(graph.Out(2));

  // Get `CalculatorGraphConfig` to pass it into `CalculatorGraph`
  return graph.GetConfig();
}
```

雖然 `pbtxt` 表示法可能很容易出錯 (如果有多項輸入內容要傳遞 )，但 C++ 程式碼看起來則更糟：

1. 重複的空白標記
2. Cast 呼叫。

以下讓我們了解可以如何改進，只要導入 `PassThroughNodeBuilder`：

```cpp
class PassThroughNodeBuilder {
 public:
  explicit PassThroughNodeBuilder(Graph& graph)
      : node_(graph.AddMode("PassThroughCalculator")) {}

  template <typename T>
  Stream<T> PassThrough(Stream<T> stream) {
    stream.ConnectTo(node_.In(index_));
    return node_.Out(index_++).Cast<T>();
  }

 private:
  int index_ = 0;
  GenericNode& node_;
};
```

現在，圖形建構程式碼看起來會像這樣：

```cpp
CalculatorGraphConfig BuildGraph() {
  Graph graph;

  // Graph inputs.
  Stream<float> float_value = graph.In(0).SetName("float_value").Cast<float>();
  Stream<int> int_value = graph.In(1).SetName("int_value").Cast<int>();
  Stream<bool> bool_value = graph.In(2).SetName("bool_value").Cast<bool>();

  PassThroughNodeBuilder pass_node_builder(graph);
  Stream<float> passed_float_value = pass_node_builder.PassThrough(float_value);
  Stream<int> passed_int_value = pass_node_builder.PassThrough(int_value);
  Stream<bool> passed_bool_value = pass_node_builder.PassThrough(bool_value);

  // Graph outputs.
  passed_float_value.SetName("passed_float_value").ConnectTo(graph.Out(0));
  passed_int_value.SetName("passed_int_value").ConnectTo(graph.Out(1));
  passed_bool_value.SetName("passed_bool_value").ConnectTo(graph.Out(2));

  // Get `CalculatorGraphConfig` to pass it into `CalculatorGraph`
  return graph.GetConfig();
}
```
