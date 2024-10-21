# Calculators: Introduction

> 2024/10/18 update:
>
> ```
> 每個計算工具都是圖表節點 (Each calculator is a node of a graph)。
> ```

MediaPipe 中的 計算器(Calculator) 是實現各種 data stream 處理功能的基本單元，每個計算器都將數據從一個或多個輸入流讀取，經過內部運算後再將結果寫入一個或多個輸出流中。

每個計算器都是 graph 中的一個節點(node)。 Graph 中的每一個節點都被實現為計算器，大部分 graph 執行發生在其計算器內部。計算器可以接收零個或多個 input stream and/or side packets 並產生零個或多個 output streams and/or side packets。

MediaPipe 的計算器通常是用 C++ 實現的，開發者可以通過繼承 `CalculatorBase` 並實現相應的處理函數和契約 (Contract) 來創建自己的計算器。

## CalculatorBase

在 MediaPipe 中，每個計算器都繼承自 `CalculatorBase` 類，該類定義了計算器的基本行為，包括:

- `GetContract()`: 返回計算器的輸入輸出契約，這個函數必須被實現。

    可以在 `GetContract()` 中指定計算器的預期輸入和輸出類型。 初始化圖形時，框架調用 static method 來驗證連接的輸入和輸出的 packets 類型是否與本規範中的一樣。

- `Open()`: 初始化計算器。

    After a graph starts, the framework calls `Open()`. The input side packets are available to the calculator at this point. `Open()` interprets the node configuration operations (see Graphs) and prepares the calculator's per-graph-run state. This function may also write packets to calculator outputs. An error during `Open()` can terminate the graph run.

- `Process()`: 這個函數會在有新的數據到達時被調用

    處理數據流。只要至少一個輸入流有可用 packet，框架就會重複調用 `Process()`。默認情況下，框架保證所有輸入都具有相同的 timestamp。

    Multiple `Process()` calls can be invoked simultaneously when parallel execution is enabled. If an error occurs during `Process()`, the framework calls Close() and the graph run terminates.

- `Close()`: 這個函數會在計算器銷毀時被調用

    清理計算器資源。在對 `Process()` 的所有調用完成後或所有輸入流關閉時，框架調用 `Close()`。 如果調用 `Open()` 並成功，則 always 調用此函數，即使圖形運行因錯誤而終止也是如此。 在 `Close()` 期間，任何輸入流都沒有可用的輸入，但它仍然可以訪問 input side packets，因此可以寫入輸出。

    After `Close()` returns, the calculator should be considered a dead node. The calculator object is destroyed as soon as the graph finishes running.

The following are code snippets from [CalculatorBase.h](https://github.com/google/mediapipe/blob/master/mediapipe/framework/calculator_base.h).

```cpp
class CalculatorBase {
 public:
  ...

  // The subclasses of CalculatorBase must implement GetContract.
  static absl::Status GetContract(CalculatorContract* cc);

  // Open is called before any Process() calls, on a freshly constructed
  // calculator.  Subclasses may override this method to perform necessary
  // setup, and possibly output Packets and/or set output streams' headers.
  virtual absl::Status Open(CalculatorContext* cc) {
    return absl::OkStatus();
  }

  // Processes the incoming inputs. May call the methods on cc to access
  // inputs and produce outputs.
  virtual absl::Status Process(CalculatorContext* cc) = 0;

  // Is called if Open() was called and succeeded.  Is called either
  // immediately after processing is complete or after a graph run has ended
  // (if an error occurred in the graph).
  virtual absl::Status Close(CalculatorContext* cc) {
    return absl::OkStatus();
  }

  ...
};
```

## Example calculator

這個範例實現了一個名為 `AddConstantCalculator` 的計算器，它的功能是將輸入的整數加上一個常數，並輸出結果，如下所示:

```cpp
#include "mediapipe/framework/calculator_framework.h"

namespace mediapipe {

// 自定義計算器，實現將輸入的整數加上一個常數的功能
class AddConstantCalculator : public CalculatorBase {
 public:
  // 計算器的輸入和輸出流
  static constexpr char kInputTag[] = "INPUT";
  static constexpr char kOutputTag[] = "OUTPUT";

  // 計算器的參數
  static constexpr char kConstantTag[] = "CONSTANT";
  int constant_;

  // 計算器的 GetContract() 函數，定義計算器的輸入輸出契約
  static Status GetContract(CalculatorContract* cc) {
    // specify a calculator with 1 input, 1 output, both of type double
    cc->Inputs().Tag(kInputTag).Set<int>();
    cc->Outputs().Tag(kOutputTag).Set<int>();
    return absl::OkStatus(); // Never forget to say "OK"!
  }

  // 計算器的初始化函數
  absl::Status Open(CalculatorContext* cc) override {
    // 從參數中讀取常數
    auto options = cc->Options<AddConstantCalculatorOptions>();
    constant_ = options.constant();
    return absl::OkStatus();
  }

  // 計算器的處理函數，將輸入加上常數並輸出結果
  absl::Status Process(CalculatorContext* cc) override {
    if (cc->Inputs().Tag(kInputTag).IsEmpty()) {
      return absl::OkStatus();
    }
    const int input = cc->Inputs().Tag(kInputTag).Get<int>();
    const int output = input + constant_;
    Packet p_out = MakePacket<int>(output).At(cc->InputTimestamp());
    cc->Outputs().Tag(kOutputTag).AddPacket(p_out);
    return absl::OkStatus();
  }
};

REGISTER_CALCULATOR(AddConstantCalculator);

}  // namespace mediapipe
```

如上所示，它的功能是將輸入的整數加上一個常數，並輸出結果。

- 這個計算器包含一個整數類型的參數`constant_`，用來存儲常數的值。
- 在 `GetContract()` 中，使用:
  - `cc->Inputs().Tag(kInputTag).Set<int>()` 指定了輸入流的格式，它必須是整數類型
  - `cc->Outputs().Tag(kOutputTag).Set<int>()` 指定了輸出流的格式，它也必須是整數類型
- 在初始化函數 `Open()` 中，從參數中讀取常數的值。
- 在處理函數`Process()` 中，將輸入加上常數，並通過輸出流輸出結果。

要使用這個計算器，您可以在 MediaPipe `CalculatorGraphConfig` 文件中添加以下:

```proto
node {
  calculator: "AddConstantCalculator"
  input_stream: "INPUT:input"
  output_stream: "OUTPUT:output"
  options {
    [mediapipe.AddConstantCalculatorOptions.ext] {
      constant: 10
    }
  }
}
```

詳細請看這: [mediapipe/kaka_examples/12_custom_calculator_2/custom_calculator.cc](https://github.com/kaka-lin/mediapipe/blob/kaka/mediapipe/kaka_examples/12_custom_calculator_2/custom_calculator.cc)

如果要執行的話:

1. Clone repo

    ```sh
    $ git clone https://github.com/kaka-lin/mediapipe.git
    $ cd mediapipe
    ```

2. Run the command as below:

    ```sh
    $ bazel run --define MEDIAPIPE_DISABLE_GPU=1 \
        mediapipe/kaka_examples/12_custom_calculator_2:custom_calculator
    ```

    Output

    ```sh
    Example 1.2.2 : Custom calculator...
    0: RECEIVED PACKET 10
    1: RECEIVED PACKET 11
    2: RECEIVED PACKET 12
    3: RECEIVED PACKET 13
    4: RECEIVED PACKET 14
    5: RECEIVED PACKET 15
    6: RECEIVED PACKET 16
    7: RECEIVED PACKET 17
    8: RECEIVED PACKET 18
    9: RECEIVED PACKET 19
    10: RECEIVED PACKET 20
    11: RECEIVED PACKET 21
    12: RECEIVED PACKET 22
    ```
