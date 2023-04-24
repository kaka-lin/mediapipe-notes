# Packets

基本 data flow 單元。一個 packet 由以下兩資料組成:

- 時間戳記 (numeric timestamp)
- 指向不可變 payload 的共享指標 (a shared pointer to an immutable payload)
  - payload: can be of any C++ type,like:
    - a single frame of video
    - a single integer detection count.

    > Payload 的類型也是 Packet 的類型

Packets are value classes and can be copied cheaply. Each copy shares ownership of the payload, with reference-counting semantics. Each copy has its own timestamp.

`Calculators` 通過發送和接收 `packets` 進行通信。 通常在每個 input timestamp 處沿著每個 input stream 發送 single packet。

## Stream packets (Streams)

A stream 是用來連接兩個 nosed 且攜帶 a sequence of packets，且 `timestamps 必須單調遞增 (monotonically increasing)`。因為 MediaPipe 主要處理 data flow，因此 Strams 是十分重要的概念。

```
InputStream 會從其對應的 OutputStream copy data 並會對該 Node 如何處理 data 進行管理。
```

> 相對另一個 packets 為 Side packets

## Side packets

Side packets 用來連接 nodes 但只攜帶 signal packet，且`無需設定 timestamp`，可用於提供一些保持不變的資料，可以理解為是`靜態/常數`資料，在 graph 建立之後就不會改變的資料。

> 相對另一個 packets 為 stream packets

## Creating a packet

Packets are generally created with `mediapipe::MakePacket<T>()` or `mediapipe::Adopt()` (from [packet.h](https://github.com/google/mediapipe/blob/master/mediapipe/framework/packet.h)).

```cpp
// Create a packet containing some new data.
Packet p = MakePacket<MyDataClass>("constructor_argument");
// Make a new packet with the same data and a different timestamp.
Packet p2 = p.At(Timestamp::PostStream());
```

or

```cpp
// Create some new data.
auto data = absl::make_unique<MyDataClass>("constructor_argument");
// Create a packet to own the data.
Packet p = Adopt(data.release()).At(Timestamp::PostStream());
```

Data within a packet is accessed with `Packet::Get<T>()`
