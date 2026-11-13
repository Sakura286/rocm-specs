# ROCm 10.1.0 全栈进度

本任务包括下列 33 个 ROCm 源码包。基础包阶段已完成，持续推进剩余组件；x86_64 是快速验证，riscv64 是最终验收。构建成功与实际 RPM 功能验证分别记录；GPU 运行验证需要可用硬件。

源码统一基线：rocm-systems `therock-10.1` → `7da43026e4f2ef7600433c38c820732f7a205d22`；rocm-libraries → `39d8d60365d2272a5366f76ccb3bfba24b219eaf`。TheRock 固定 half `207ee58595a64b5c4a70df221f1e6e704b807811`（与旧配方相同），HIPIFY `0e051929fe80ccc0af6dc194ddb990aa82eec97d`。归档校验值逐包核实并记入 SPEC。`rocm-bandwidth-test` 不在 systems 10.1 发布中，也无 therock-10.1 标签；采用独立仓库最新标签 `rocm-7.2.4` 的固定提交 `06dd9df114855ed2dc38cd731ad214066a62d6da`（从旧 6.4.2 升级），RPM 保留其真实发布版本 7.2.4，依赖 10.1.0 HSA。上游证据与实验目录：工作区 `tmp/rocm10-stack/`。

顺序：独立基础库／管理工具 → HSA 与 HIP 运行时 → 基础模板库／随机数库 → BLAS／FFT／稀疏矩阵 → 求解器和 MIOpen。独立包可同时构建，避免等待一个包阻塞全部工作。

| 源码包 | 当前步骤 | x86_64 | riscv64 |
| --- | --- | --- | --- |
| amdsmi | 已提交，构建／修复中 | blocked | blocked；产物验证待完成 |
| half | 已提交，构建／修复中 | succeeded；实际 RPM CMake/API 通过 | succeeded；产物验证待完成 |
| hipblas | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipblas-common | 已提交，构建／修复中 | succeeded；实际 RPM CMake/API 通过 | scheduled；产物验证待完成 |
| hipblaslt | 源码与补丁审查中 | 待构建 | 待构建和产物验证 |
| hipcub | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipfft | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipify | 已提交，构建／修复中 | building | scheduled；产物验证待完成 |
| hiprand | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipsolver | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipsparse | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| hipsparselt | 源码与补丁审查中 | 待构建 | 待构建和产物验证 |
| miopen | 源码与补丁审查中 | 待构建 | 待构建和产物验证 |
| python-tensile | 已提交，构建／修复中 | succeeded | scheduled；产物验证待完成 |
| rccl | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocblas | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocclr | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocfft | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocm-bandwidth-test | 源码与补丁审查中 | 待构建 | 待构建和产物验证 |
| rocm-cmake | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-core | 已提交，构建／修复中 | succeeded；实际 RPM CMake/API 通过 | building；产物验证待完成 |
| rocm-llvm | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-origami | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocm-smi | 已提交，构建／修复中 | succeeded | scheduled；产物验证待完成 |
| rocminfo | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocprim | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocprofiler-register | 已提交，构建／修复中 | succeeded；实际 RPM CMake/API 通过 | succeeded；产物验证待完成 |
| rocr-runtime | 已提交，构建／修复中 | building | scheduled；产物验证待完成 |
| rocrand | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocsolver | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocsparse | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| rocthrust | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |
| roctracer | 已提交，构建／修复中 | unresolvable | unresolvable；产物验证待完成 |

## 当前修复与验收证据

- 第一批实际 RPM 验证：`tmp/rocm10-stack/validation/wave1-*x86_64.log`。CMake 导入三个包、编译链接并验证 half 运算、hipBLAS 枚举、ROCm 10.1.0 版本 API、rocprofiler-register 错误字符串 API。rocprofiler-register 的 132 项上游模拟运行时测试在双架构 OBS 均通过。
- HSA 新依赖包含 `mlir24-devel`；HIP/数学库显式依赖 `rocr-runtime-devel` / `rocm-hip-devel >= 10.1.0`，防止源服务初次构建或系统仓库的 7.x 产物被误用于验收。
- HIP 组件本身仍为 7.16.0，库 SONAME 为 7；ROCm 产品 RPM 版本与组件 ABI 分开维护。AMD SMI 的 SONAME 已升为 27。
- 已删除上游替代的 AMD SMI 缺失 CPU 符号、rocBLAS nodiscard、hipFFT SONAME、hipSPARSELt F16C 补丁；rocFFT 保留上游 SQLite >= 3.51.3 要求。MIOpen 所需 `-fno-offload-uniform-block` 已用 LLVM 24 实测支持，删除旧禁用补丁；clang-tidy 在所选 Clang 构建下不是 ALL 目标，删除旧 no-op 补丁。
- 大归档在 `sh-plct-sg2044:/home/openruyi/tmp/rocm10-stack/` 下载、校验和检查；本机只保存必要上下文，保留全部实验目录。
- 状态快照为任务目录 `obs-state.json` / `result-current.xml`，`monitor.py` 保存已完成构建的日志及 OBS history。表格是检查点，不代表实时状态；继续查询并修复所有包，不在此处结束任务。
