# Packets

`Calculators` 通過發送和接收 `packets` 進行通信。 通常在每個 input timestamp 處沿著每個 input stream 發送 single packet。

一個 Packet 可以包含任何 data 類型，如:

- a single frame of video
- a single integer detection count.

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
