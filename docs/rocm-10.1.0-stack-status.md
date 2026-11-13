# ROCm 10.1.0 全栈进度

本任务包括原有 33 个 ROCm 源码包，并补入 10.1 新依赖 rocm-stinkytofu（共 34 个）。基础包阶段已完成，持续推进剩余组件；x86_64 是快速验证，riscv64 是最终验收。构建成功与实际 RPM 功能验证分别记录；GPU 运行验证需要可用硬件。

源码统一基线：rocm-systems `therock-10.1` → `7da43026e4f2ef7600433c38c820732f7a205d22`；rocm-libraries → `39d8d60365d2272a5366f76ccb3bfba24b219eaf`。TheRock 固定 half `207ee58595a64b5c4a70df221f1e6e704b807811`（与旧配方相同），HIPIFY `0e051929fe80ccc0af6dc194ddb990aa82eec97d`。归档校验值逐包核实并记入 SPEC。`rocm-bandwidth-test` 不在 systems 10.1 发布中，也无 therock-10.1 标签；采用独立仓库最新标签 `rocm-7.2.4` 的固定提交 `06dd9df114855ed2dc38cd731ad214066a62d6da`（从旧 6.4.2 升级），RPM 保留其真实发布版本 7.2.4，依赖 10.1.0 HSA。上游证据与实验目录：工作区 `tmp/rocm10-stack/`。

顺序：独立基础库／管理工具 → HSA 与 HIP 运行时 → 基础模板库／随机数库 → BLAS／FFT／稀疏矩阵 → 求解器和 MIOpen。独立包可同时构建，避免等待一个包阻塞全部工作。

| 源码包 | 当前步骤 | x86_64 | riscv64 |
| --- | --- | --- | --- |
| amdsmi | 已提交，构建／验证中 | succeeded；产物验证待完成 | building；产物验证待完成 |
| half | 已提交，构建／验证中 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| hipblas | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipblas-common | 已提交，构建／验证中 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| hipblaslt | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipcub | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| hipfft | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipify | 已提交，构建／验证中 | succeeded；产物验证待完成 | building；产物验证待完成 |
| hiprand | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipsolver | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipsparse | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipsparselt | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| miopen | 已提交，构建／验证中 | blocked；产物验证待完成 | blocked；产物验证待完成 |
| python-tensile | 已提交，构建／验证中 | succeeded；Python 导入和 CLI 通过，生成验证待完成 | succeeded；Python 导入和 CLI 通过，生成验证待完成 |
| rccl | 已提交，构建／验证中 | failed；产物验证待完成 | unresolvable；产物验证待完成 |
| rocblas | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| rocclr | 已提交，构建／验证中 | succeeded；指定 GNU host triple 后离线 HIP 编译/链接通过 | unresolvable；产物验证待完成 |
| rocfft | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocm-bandwidth-test | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocm-cmake | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-core | 已提交，构建／验证中 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| rocm-llvm | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-origami | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocm-smi | 已提交，构建／验证中 | succeeded；CLI 通过（无 GPU） | succeeded；CLI/API 通过（无 GPU） |
| rocm-stinkytofu | 已提交，构建／验证中 | building；产物验证待完成 | building；产物验证待完成 |
| rocminfo | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocprim | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocprofiler-register | 已提交，构建／验证中 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| rocr-runtime | 已提交，构建／验证中 | succeeded；产物验证待完成 | building；产物验证待完成 |
| rocrand | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| rocsolver | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocsparse | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocthrust | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| roctracer | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |

## 当前修复与验收证据

- 第一批实际 RPM 验证：`tmp/rocm10-stack/validation/wave1-*x86_64.log`。CMake 导入三个包、编译链接并验证 half 运算、hipBLAS 枚举、ROCm 10.1.0 版本 API、rocprofiler-register 错误字符串 API。rocprofiler-register 的 132 项上游模拟运行时测试在双架构 OBS 均通过。
- HSA 新依赖包含 `mlir24-devel`；HIP/数学库显式依赖 `rocr-runtime-devel` / `rocm-hip-devel >= 10.1.0`，防止源服务初次构建或系统仓库的 7.x 产物被误用于验收。
- HIP 组件本身仍为 7.16.0，库 SONAME 为 7；ROCm 产品 RPM 版本与组件 ABI 分开维护。AMD SMI 的 SONAME 已升为 27。
- 已删除上游替代的 AMD SMI 缺失 CPU 符号、rocBLAS nodiscard、hipFFT SONAME、hipSPARSELt F16C 补丁；rocFFT 保留上游 SQLite >= 3.51.3 要求。MIOpen 所需 `-fno-offload-uniform-block` 已用 LLVM 24 实测支持，删除旧禁用补丁；clang-tidy 在所选 Clang 构建下不是 ALL 目标，删除旧 no-op 补丁。
- 大归档在 `sh-plct-sg2044:/home/openruyi/tmp/rocm10-stack/` 下载、校验和检查；本机只保存必要上下文，保留全部实验目录。
- 状态快照为任务目录 `obs-state.json` / `result-current.xml`，`monitor.py` 保存已完成构建的日志及 OBS history。表格是检查点，不代表实时状态；继续查询并修复所有包，不在此处结束任务。

## 2026-11-14 检查点

- 全部原有配方已升级并接入 ROCm10；新增 `rocm-stinkytofu` 是 hipBLASLt/hipSPARSELt 的 rocisa 必需依赖，同样取自 `therock-10.1` 已核实资产。StinkyTofu ABI 为 0.1.0，产品 RPM 为 10.1.0。首轮 1500 项测试中 1492 通过；PatternParser 的固定临时文件名导致并发干扰，保留全部测试并改为串行执行，等待重建。
- LLVM 24 的默认宿主 triple 缺少环境字段，`clang-linker-wrapper` 产生的 host bundle ID 被 bundler 拒绝。明确 `--target=x86_64-openruyi-linux-gnu` 后，实际 HIP RPM 的编译、完整链接以及 ROCMCheckTargetIds 的 gfx1100/gfx1200 探测通过。数学库采用 CMake 的 `CMAKE_CXX_COMPILER_TARGET` / `CMAKE_HIP_FLAGS_INIT`，RISC-V 对应 `riscv64-openruyi-linux-gnu`。这属于发行版目标配置，不是 API/ABI 补丁；未修改系统 LLVM。
- HIPIFY 的 standalone Clang 资源发现通过指向系统 clang24-libs 资源的 symlink 修正。CUDA API 名称翻译最小验证已通过（使用明确的声明夹具，无完整 CUDA SDK）；实际 RPM 的自动发现仍需随新产物复核。
- bandwidth-test 7.2.4 已变为使用 TransferBench 的插件架构，不能沿用 6.4 的 prep、许可证名和单二进制清单。已调整系统依赖选择、编译路径和常规 lib64 安装规则，等待构建验证。
- 原生 riscv64 的首批 CMake/API 验证见 `validation/riscv64/wave1-*`。Tensile 导入/CLI、rocm-smi CLI 和版本 API 通过，见 `validation/riscv64/native-tools-riscv64.json`；SMI 组件版本为 7.8.0，产品 RPM 版本为 10.1.0。隔离环境尚未安装 Tensile 的可选 joblib/msgpack 依赖，不能将 CLI 检查写成完整库生成通过。
- 已确认 `sh-plct-sg2044` 没有 AMD PCI GPU、没有 `/dev/kfd`。已询问其他带 GPU 的 riscv64 验收机器，等待用户回复；继续所有构建、CPU API、离线编译验证，不声称 GPU 运算已通过。
- RCCL 的目标探测在 OBS 仍失败，但相同目标与 RPM 编译标志的本地最小探测通过。已保留失败时的 CMakeConfigureLog.yaml 到 OBS 日志，下一步依据真实编译/链接错误修复，不强制把探测结果设为成功。

- x86_64 实际 HIP RPM：`hipRuntimeGetVersion` 返回 71600000；HIPRTC 将向量加法内核离线编译为 4544 字节 gfx1100 ELF，日志为空。证据：`validation/hiprtc-offline-x86_64.log`、`hiprtc-offline-result.json`、`hiprtc-add-gfx1100.co`，不含 GPU 执行。
