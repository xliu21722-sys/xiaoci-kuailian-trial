# 随附开源组件与语音资源

本机识别、模型下载和离线朗读不调用计费语音 API。模型首次加载需要网络，模型加载后的运算在使用者电脑上完成。

- Vosk Browser 0.0.8：Apache-2.0，https://github.com/ccoreilly/vosk-browser
- Vosk small Mandarin 0.22：Apache-2.0，https://alphacephei.com/vosk/models
  - 来源：https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
  - 原包 SHA-256：3af8b0e7e0f835ae9d414ce5df580237a3cfb08d586c9fbbb0f7ff29ad5b14ba
- Sherpa-ONNX 2.0.0：Apache-2.0，https://github.com/k2-fsa/sherpa-onnx
- 中文 Matcha icefall zh-baker 与 Vocos：使用 Sherpa-ONNX 官方发布的中文 WASM 包，https://k2-fsa.github.io/sherpa/onnx/tts/all/Chinese/matcha-icefall-zh-baker.html
  - 来源：https://github.com/k2-fsa/sherpa-onnx/releases/download/v2.0.0/sherpa-onnx-wasm-simd-2.0.0-matcha-icefall-zh-baker.tar.bz2
  - 原包 SHA-256：aaddc15072e1c60b47a0481b5425e50ddaba2427e9acc21deafa5efce0a18e96
  - 网页的三种免费朗读风格来自同一个中文女声模型，按语速区分，不冒充三位不同演员或克隆身份。

中文分词读音使用 pinyin-pro；DOCX / PDF 解析使用 Mammoth 与 PDF.js。各许可证随资源放在 assets/vendor 或许可证文件中。Electron 及其 Chromium、Node.js 许可证随桌面发行包提供。

Vosk Browser 的内嵌 worker 在构建时提取为同源静态文件，让动态绑定仅在识别 worker 内运行；主界面不开放 unsafe-eval。ASR 原包重新打成含目录项的 tar.gz，模型权重未更改。Sherpa 模型数据仅分块，下载后按 SHA-256 校验重组。完整版权许可见 licenses/，上游信息链接如上。
