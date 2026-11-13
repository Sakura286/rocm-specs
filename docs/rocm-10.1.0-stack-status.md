# ROCm 10.1.0 全栈进度

本任务包括原有 33 个 ROCm 源码包，并补入 10.1 新依赖 rocm-stinkytofu（共 34 个）。基础包阶段已完成，持续推进剩余组件；x86_64 是快速验证，riscv64 是最终验收。构建成功与实际 RPM 功能验证分别记录；GPU 运行验证需要可用硬件。

源码统一基线：rocm-systems `therock-10.1` → `7da43026e4f2ef7600433c38c820732f7a205d22`；rocm-libraries → `39d8d60365d2272a5366f76ccb3bfba24b219eaf`。TheRock 固定 half `207ee58595a64b5c4a70df221f1e6e704b807811`（与旧配方相同），HIPIFY `0e051929fe80ccc0af6dc194ddb990aa82eec97d`。归档校验值逐包核实并记入 SPEC。`rocm-bandwidth-test` 不在 systems 10.1 发布中，也无 therock-10.1 标签；采用独立仓库最新标签 `rocm-7.2.4` 的固定提交 `06dd9df114855ed2dc38cd731ad214066a62d6da`（从旧 6.4.2 升级），RPM 保留其真实发布版本 7.2.4，依赖 10.1.0 HSA。上游证据与实验目录：工作区 `tmp/rocm10-stack/`。

顺序：独立基础库／管理工具 → HSA 与 HIP 运行时 → 基础模板库／随机数库 → BLAS／FFT／稀疏矩阵 → 求解器和 MIOpen。独立包可同时构建，避免等待一个包阻塞全部工作。

| 源码包 | 当前步骤 | x86_64 | riscv64 |
| --- | --- | --- | --- |
| amdsmi | 已提交，构建／验证中 | succeeded；实际 RPM Python 版本 API 通过 | succeeded；产物验证待完成 |
| half | 双架构实际 RPM 验收通过 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| hipblas | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipblas-common | 双架构实际 RPM 验收通过 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| hipblaslt | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipcub | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| hipfft | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| hipify | 已提交，构建／验证中 | succeeded；实际 RPM 自动资源发现与 API 翻译通过（声明夹具） | succeeded；产物验证待完成 |
| hiprand | 已提交，构建／验证中 | succeeded；实际 RPM CMake/版本 API/Philox CPU 算法通过 | unresolvable；产物验证待完成 |
| hipsolver | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipsparse | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| hipsparselt | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| miopen | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| python-tensile | 已提交，构建／验证中 | succeeded；Python 导入和 CLI 通过，生成验证待完成 | succeeded；Python 导入和 CLI 通过，生成验证待完成 |
| rccl | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| rocblas | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| rocclr | 已提交，构建／验证中 | succeeded；指定 GNU host triple 后离线 HIP 编译/链接通过 | unresolvable；产物验证待完成 |
| rocfft | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocm-bandwidth-test | 已提交，构建／验证中 | building；产物验证待完成 | unresolvable；产物验证待完成 |
| rocm-cmake | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-core | 双架构实际 RPM 验收通过 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| rocm-llvm | 双架构实际 RPM 验收通过 | 通过 | 通过 |
| rocm-origami | 已提交，构建／验证中 | succeeded；实际 RPM CMake/gfx1100 硬件模型 API 通过 | unresolvable；产物验证待完成 |
| rocm-smi | 已提交，构建／验证中 | succeeded；CLI 通过（无 GPU） | succeeded；CLI/API 通过（无 GPU） |
| rocm-stinkytofu | 双架构实际 RPM 验收通过 | 1500 CTest；CMake/API/解析/优化通过 | 1500 CTest；SG2044 原生 CMake/API/解析/优化通过 |
| rocminfo | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocprim | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| rocprofiler-register | 双架构实际 RPM 验收通过 | succeeded；实际 RPM CMake/API 通过 | succeeded；实际 RPM CMake/API 通过 |
| rocr-runtime | 已提交，构建／验证中 | succeeded；产物验证待完成 | building；产物验证待完成 |
| rocrand | 已提交，构建／验证中 | succeeded；实际 RPM CMake/版本 API/Philox CPU 算法通过 | unresolvable；产物验证待完成 |
| rocsolver | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocsparse | 已提交，构建／验证中 | unresolvable；产物验证待完成 | unresolvable；产物验证待完成 |
| rocthrust | 已提交，构建／验证中 | succeeded；产物验证待完成 | unresolvable；产物验证待完成 |
| roctracer | 已提交，构建／验证中 | succeeded；实际 RPM 链接/版本 API 通过 | unresolvable；产物验证待完成 |

## 当前修复与验收证据

- 第一批实际 RPM 验证：`tmp/rocm10-stack/validation/wave1-*x86_64.log`。CMake 导入三个包、编译链接并验证 half 运算、hipBLAS 枚举、ROCm 10.1.0 版本 API、rocprofiler-register 错误字符串 API。rocprofiler-register 的 132 项上游模拟运行时测试在双架构 OBS 均通过。
- HSA 新依赖包含 `mlir24-devel`；HIP/数学库显式依赖 `rocr-runtime-devel` / `rocm-hip-devel >= 10.1.0`，防止源服务初次构建或系统仓库的 7.x 产物被误用于验收。
- HIP 组件本身仍为 7.16.0，库 SONAME 为 7；ROCm 产品 RPM 版本与组件 ABI 分开维护。AMD SMI 的 SONAME 已升为 27。
- 已删除上游替代的 AMD SMI 缺失 CPU 符号、rocBLAS nodiscard、hipFFT SONAME、hipSPARSELt F16C 补丁；rocFFT 保留上游 SQLite >= 3.51.3 要求。MIOpen 所需 `-fno-offload-uniform-block` 已用 LLVM 24 实测支持，删除旧禁用补丁；clang-tidy 在所选 Clang 构建下不是 ALL 目标，删除旧 no-op 补丁。
- 大归档在 `sh-plct-sg2044:/home/openruyi/tmp/rocm10-stack/` 下载、校验和检查；本机只保存必要上下文，保留全部实验目录。
- 状态快照为任务目录 `obs-state.json` / `result-current.xml`，`monitor.py` 保存已完成构建的日志及 OBS history。表格是检查点，不代表实时状态；继续查询并修复所有包，不在此处结束任务。

## 2026-11-14 检查点

- 全部原有配方已升级并接入 ROCm10；新增 `rocm-stinkytofu` 是 hipBLASLt/hipSPARSELt 的 rocisa 必需依赖，同样取自 `therock-10.1` 已核实资产。StinkyTofu ABI 为 0.1.0，产品 RPM 为 10.1.0。首轮 PatternParser 固定临时文件名导致并发干扰；改为串行后 x86_64 全部 1500 项测试通过（RPM 10.1.0-4.1）。riscv64 正在构建。
- LLVM 24 的默认宿主 triple 缺少环境字段，`clang-linker-wrapper` 产生的 host bundle ID 被 bundler 拒绝。明确 `--target=x86_64-openruyi-linux-gnu` 后，实际 HIP RPM 的编译、完整链接以及 ROCMCheckTargetIds 的 gfx1100/gfx1200 探测通过。数学库采用 CMake 的 `CMAKE_CXX_COMPILER_TARGET` / `CMAKE_HIP_FLAGS_INIT`，RISC-V 对应 `riscv64-openruyi-linux-gnu`。这属于发行版目标配置，不是 API/ABI 补丁；未修改系统 LLVM。
- HIPIFY 的 standalone Clang 资源发现通过指向系统 clang24-libs 资源的 symlink 修正。CUDA API 名称翻译最小验证已通过（使用明确的声明夹具，无完整 CUDA SDK）；实际 RPM 的自动发现仍需随新产物复核。
- bandwidth-test 7.2.4 已变为使用 TransferBench 的插件架构，不能沿用 6.4 的 prep、许可证名和单二进制清单。已调整系统依赖选择、编译路径和常规 lib64 安装规则，等待构建验证。
- 原生 riscv64 的首批 CMake/API 验证见 `validation/riscv64/wave1-*`。Tensile 导入/CLI、rocm-smi CLI 和版本 API 通过，见 `validation/riscv64/native-tools-riscv64.json`；SMI 组件版本为 7.8.0，产品 RPM 版本为 10.1.0。隔离环境尚未安装 Tensile 的可选 joblib/msgpack 依赖，不能将 CLI 检查写成完整库生成通过。
- 已确认 `sh-plct-sg2044` 没有 AMD PCI GPU、没有 `/dev/kfd`。已询问其他带 GPU 的 riscv64 验收机器，等待用户回复；继续所有构建、CPU API、离线编译验证，不声称 GPU 运算已通过。
- RCCL 的目标探测在 OBS 仍失败，但相同目标与 RPM 编译标志的本地最小探测通过。已保留失败时的 CMakeConfigureLog.yaml 到 OBS 日志，下一步依据真实编译/链接错误修复，不强制把探测结果设为成功。

- x86_64 实际 HIP RPM：`hipRuntimeGetVersion` 返回 71600000；HIPRTC 将向量加法内核离线编译为 4544 字节 gfx1100 ELF，日志为空。证据：`validation/hiprtc-offline-x86_64.log`、`hiprtc-offline-result.json`、`hiprtc-add-gfx1100.co`，不含 GPU 执行。

## 后续检查点：LLVM 24 汇编模式与实际 RPM 消费者

- rocBLAS 的旧 Tensile 生成 `v_cvt_f16_f32 v18, v18`，系统 LLVM 24 默认 Real16 模式拒绝这一 Fake16 写法。上游变更 [bf02d3b7b028850c1130ce80291d26d5a5fdc42c](https://github.com/llvm/llvm-project/commit/bf02d3b7b028850c1130ce80291d26d5a5fdc42c) 明确禁止混用；hipBLASLt 的 true16 提交针对另一套 rocisa，不能直接套到旧 Tensile。采用 LLVM 已有 `-Xclangas -target-feature -Xclangas -real-true16`，仅给 rocBLAS 的 Tensile 汇编器入口使用；能力探测和生成汇编保持一致。未修改 LLVM/Tensile 指令生成源码。四个 gfx1100/1101/1200/1201 的复现均通过，且与 Real16 的 `v18.l` 写法生成相同 `.text` 字节 `1215247e`，证据 `llvm-driver-review/fake16-validation.json`。完整 rocBLAS 重建仍待结果。
- RCCL 子配置用 `CMAKE_TRY_COMPILE_PLATFORM_VARIABLES=ROCM_PATH` 继承路径；撤去进程环境的 `ROCM_PATH=/usr`，因为该环境覆盖会阻止 Clang 按版本目录发现 device-libs。最新构建已越过配置，等待完整结果。
- GNU host triple 与发行版 libomp 安装目录不同，rocFFT/hipSPARSELt 明确 LIBRARY_PATH 和安装 RUNPATH。rocFFT 已越过 OpenMP 探测，随后 SPIR-V 客户端拒绝 `-ffat-lto-objects`；配方关闭本包的 RPM LTO flags，保留上游 SPIR-V 客户端目标重建。
- 实际 x86_64 RPM 联合消费者见 `validation/math-consumer-*`：StinkyTofu 编译期/运行期版本一致，rocRAND 与 hipRAND 组件版本 500000，256 个 Philox 输出一致且可复现，Origami 创建 gfx1100 模型，ROCtracer 版本 API 为 4.1。使用实际导出的 CMake targets；未伪造 GPU 运行结果。
- rocRAND 主机生成器也在 `host_system::alloc()` 调用 `hipDeviceSynchronize()`，当前无可用 GPU 时返回 allocation failure；已保留失败日志，改用公开头文件的 Philox 算法验证 CPU 路径，不能把它表述为 host generator API 完整通过。
- StinkyTofu 实际 RPM 的 `stinkytofu-opt` 汇编 round-trip 通过 LLVM FileCheck；优化案例须使用上游自己的 `stinkytofu-check`（其 CHECK-SAME 语义不同于 LLVM FileCheck），`peephole_mul_fma_fusion.stir` 通过。证据 `validation/stinkytofu-*x86_64*`。
- HIPIFY 10.1.0-6.1 修正先前未展开的 RUNPATH 宏；剔除测试环境的 LLVM LD_LIBRARY_PATH 后，声明夹具翻译仍成功，自动使用 `/usr/include/hipify` 的资源 symlink。日志保留缺失完整 CUDA SDK 的预探测提示，不宣称完整 CUDA SDK 验证。
- riscv64 HSA 在 pico-itx-hc037 安装 clang24-static 时解包失败，未进入源码编译。已为该包增加 jobs>=32 约束，checkconstraints 确认匹配 4 个 SG2044 和 2 个 v100 worker。曾尝试 disk>=32G，但当前 worker 声明无匹配，已撤掉该条件；HIPIFY 也遇到 MLIR 静态库解包失败，采用同一 jobs 约束。继续跟踪实际调度，不将此次失败归为源码不兼容。

- StinkyTofu 双架构实际 RPM 验收完成：10.1.0-4.1，OBS revision 4；riscv64 全部 1500 CTest 通过。`validation/stinkytofu-native-riscv64.log` 记录 SG2044 原生导入已安装 CMake targets、编译链接/运行、版本一致性和两个上游 stinkytofu-check 案例成功。工具无 GPU 执行依赖，此包的最终功能验收已完成。
- rocPRIM/rocThrust 实际 x86_64 RPM：`validation/template-kernel-x86_64.o` 包含 gfx1100/gfx1200 编译结果，联合使用 block_reduce 与 thrust::transform；未运行 GPU 内核。
- rocFFT：`llvm-config --targets-built` 确认系统 LLVM 24 未编入 SPIR-V。检索到的上游 FFT/SPIR-V 提交未提供缺失后端的兼容方案；配方仅移除客户端的额外 `amdgcnspirv` 回退，保留四个原生 GPU 目标，并恢复正常 RPM LTO。这不是 ABI backport，也不声称支持未预编译 GPU 的 SPIR-V 回退。
- rocBLAS：Tensile CMake 不转发 `Tensile_ASSEMBLER`，实际通过配置期 PATH 选择汇编器；`%conf -p` 中 `buildsubdir` 尚未定义，最终用 `$PWD/tensile-assembler` 并检查 executable 存在。保持原有 HIP/C++ 编译器入口，只改变 Tensile 汇编器模式。验证脚本记录 `validation/tensile-assembler-resolution.json`；同一 Fake16 汇编在 SG2044 原生 Clang 24 也通过。


## 后续检查点：HSA 上游可移植 helper 与客户端安装

- HSA riscv64 已在 `sg2044-0317:8` 成功安装 LLVM 静态依赖并进入源码编译，暴露 SDMA 新增的两处无条件 `_mm_pause()`。配方 `e5bee1b` 回移 ROCm 合并提交 [3a6a0d89e39e2dbcf28b066a31b7d2ec4c020712](https://github.com/ROCm/rocm-systems/commit/3a6a0d89e39e2dbcf28b066a31b7d2ec4c020712)（PR #11310，包含评审后的全部修改），只调整 standalone 归档路径，无额外源码前置提交；所有 hunk 在 10.1 资产上以 fuzz=0 应用。替换原发行版的 pause/fence 覆盖，保留独立的 glibc ELF 地址调整。该修复是宿主架构可移植性修复，不是 LLVM ABI 适配。
- 上游最终版本的 RISC-V store fence 为 `fence ow, ow`，完整 fence 为 `fence iorw, iorw`，包含 I/O 顺序；早期 PR 提交和旧本地补丁的语义不应混同。实际 x86_64/SG2044 LLVM 24 头文件编译探测分别生成对应 x86 指令与 RISC-V pause/fence，证据 `validation/hsa-portable-helpers-*`。完整 OBS 构建与产物验证尚待结果。
- 上游 `cacheline_flush()` 在 RISC-V 仍发出未实现警告；本资产的调用位于 XDNA 驱动，不能以 fence 或无操作声称完成缓存刷新。原本地补丁的 Zicbom 条件实现未冒充上游保留；本次不宣称 XDNA/RISC-V 非一致缓存设备可用，须待相应设备与缓存一致性验证。
- rocFFT 在移除缺失的 SPIR-V fallback 后已完整编译库与客户端；RPM 清单随后暴露旧 `rtc_helper_crash` 条目。`7533410` 移除未安装的内部测试工具条目，并保留/打包实际运行时所需的版本化 `rocfft_rtc_helper`。准备了 `validation/fft-api-rtc.py` 对实际 RPM 的 CPU API 与独立 HIPRTC helper 进行离线编译验证，等待新 RPM。
- hipFFT 客户端同样只移除缺失后端的 `amdgcnspirv` fallback；hipSPARSE 改用新版客户端开关以确实构建 benchmark，保留 Fortran，并显式配置 LLVM OpenMP 的库路径。rocSOLVER 在 riscv64 使用 jobs>=32 worker，编译池 8 配合已有每 TU 4 个 HIP 任务、链接池 1，限制嵌套并发。
- RCCL x86_64 已推进至 5106/6013，HIPIFY riscv64 已进入最终链接，AMD SMI riscv64 已至 228/230；这些是构建过程进展，不是验收通过。继续跟踪全部 34 个包。


## 后续检查点：实际产物覆盖与运行期缺陷

- 当前 OBS 快照为 x86_64 23 个 succeeded、3 个 building、8 个 unresolvable；riscv64 11 个 succeeded、HSA building、22 个依赖待解。仅记录构建结果，未把无 GPU 的验证算成 GPU 运算验收。全部 34 个包的展开源码已审计与当前分支对应包内容一致，见 `source-audit/audit-current.json`。
- HIPIFY riscv64 10.1.0-7.1 在 SG2044 用实际 RPM 自动资源发现完成 CUDA→HIP 声明夹具翻译，使用仅含声明的 cuda_runtime.h 夹具，未安装完整 CUDA SDK。剔除 LLVM LD_LIBRARY_PATH 后仍通过；`validation/hipify-native-riscv64.json` 保存输出及 SDK 预探测提示。
- AMD SMI riscv64 已构建发布；隔离环境明确导入实际 RPM 的 Python 模块，加载 SONAME 27，版本 API 返回 27.1.0/build 2，见 `validation/amdsmi-native-riscv64.json`。测试环境原有 26.x 库不算本次验证；无 GPU 的目标机不能验证 GPU 监控功能。
- rocFFT、hipFFT、hipCUB x86_64 实际 RPM 联合 CMake 消费者通过，导入各自 target；rocFFT/hipFFT 组件版本一致为 1.0.40，hipCUB block reduction 编译为 gfx1100/gfx1200。见 `validation/fft-cub-*x86_64.log`。rocFFT 独立 RTC helper 离线编译两个目标均生成 4544 字节 ELF（`fft-api-rtc-x86_64.json`）。`execution_info_create` 会枚举 HIP 设备，无 GPU 时失败；保留原失败日志，不声称该 API 或 FFT 运算通过。
- RCCL 在 5100 多个编译任务后，CE-reduce 自定义命令仍使用不完整 host triple。`87bc074` 为独立 DeviceLinker 命令补上同一 GNU target；四目标直接 Clang 编译复现通过，完整重建待结果。常规 CMake compiler target 不会自动传播到这些自定义命令。
- bandwidth-test 实际 RPM 退出时在 `PluginManagement_t::plugin_unload()` 空 vector::back 上触发断言，GDB 已定位。上游 develop 及文件的三项历史提交均仍有错误，未找到可回移提交；`e436b15` 增加有调查记录的一行发行版补丁：以实际被 pop 的库 handle 容器作为循环条件。另将默认插件搜索路径补全至 GNUInstallDirs 的 lib64/rocm_bandwidth_test/plugins。此为普通 C++ 运行时错误及安装路径修复，不是 LLVM API/ABI 补丁。重建后须重跑 CLI 与插件发现，旧 RPM 出包不能标记验收完成。


## 构建吞吐与恢复提示

- rocBLAS 旧 x86 worker 实际只给 `-j4`；`osc checkconstraints` 确认有 20 个 jobs>=32 的 x86 worker。rocBLAS、RCCL、rocSPARSE、rocSOLVER、hipBLASLt、hipSPARSELt、MIOpen 分别独立提交，将已有大 worker 约束扩展到两个架构；未重建已完成的 FFT/CUB 包。最新提交范围 `324843a` 至 `f335602`。
- 已通过 `_buildinfo` 核实 rocBLAS/RCCL 的 `hardware:jobs 32`，实际调度分别为 `epyc-massive-02-n0h:8` / `epyc-massive-03:9`，日志均为 `-j32`。RCCL 104 秒到 1186/6013，继续跟踪后段 CE-reduce 与链接。HSA riscv64 当前 worker `sg2044-0317:8` 仍在安装最后的 clang24-static；旧 `_mm_pause` 错误日志不是新修订的结果。
- 本机剩余磁盘有限，大产物归档优先存放 SG2044 的任务目录（约 450 GiB 可用）。实际 RPM 解包脚本更新为在同一文件系统中用 hardlink 连接 staging 与只读验证 root，避免重复的大库副本；保留所有 RPM/日志/实验产物。覆盖借用的 Python stdlib 目录时保留缺失宿主条目，防止新包的 site-packages 覆盖导致隔离环境缺少 encodings。
- 恢复任务时继续查询全部 34 包的最新 OBS 状态、失败日志和 source revision，再推进实际 RPM 的 x86_64 与 SG2044 验证；不要把本检查点或所有 SPEC 已升级视为工作完成。

## 后续检查点：原生 HSA 与 GNU target 的运行库目录

- HSA 10.1.0-7.1 双架构构建成功。实际 RPM 的 CMake 导入、链接和三个状态字符串 API 在 x86_64 与 SG2044 均通过；两个 ELF 的 280 个 `hsa_*` 导出完全一致。证据为 `validation/hsa-consumer-*`、`hsa-symbol-comparison.json`。无 AMD GPU 时 `hsa_init` 返回 OUT_OF_RESOURCES，未计为 GPU 运行通过。RISC-V 构建还出现 `kfd_runtime_info` 前置声明导致的 ThunkLoader LTO ODR 警告，尚未发现上游修复，需保留关注；不等于已观察到运行期 ABI 故障。
- bandwidth-test 7.2.4-8.1 的 `--help`、`--version`、插件列表、tb 插件信息均正常退出，正确发现 lib64 下的插件，原 unload 崩溃已修复。`run tb --help` 会先初始化 GPU 引擎，无 GPU 时仍因设备属性获取失败崩溃；不将前四项 CLI 通过写成引擎运行验收。证据 `validation/bandwidth-cli-x86_64.json`。
- RCCL `7675db5` 移除上游 CMake 内部再次设置的 `ENV{ROCM_PATH}`；最小真实编译探测证实该环境变量令 Fabric API/handle 等检测失败，删除后通过。新完整构建已越过原类型重定义错误，在 5732/6013 的覆盖率测试链接处暴露 compiler-rt 路径问题。
- HIP 的原 RISC-V PCH/RTC 汇编配置只设 lp64d，没有启用 F/D 指令集。`30e39f9` 同时指定 `--target-abi=lp64d -mattr=+f,+d`；LLVM 上游 ABI 测试提交 `fea4957177315f83746dca90cb4c9013eb465c46` 说明该约束。SG2044 实际 LLVM 24 汇编、ELF double-float ABI、共享库链接及读取 marker=42 均通过，见 `validation/hip-pch-abi-native-riscv64.log`。该提交已随下一批推送，不能把此前失败日志算成新修订失败。
- hipCUB 额外采用双架构 jobs>=32；其新 x86_64 完整构建成功。此前“未重建已完成 FFT/CUB”的描述仅指当时的 worker 调整批次，后续原生目标配置仍需重建。
- 显式 GNU target 对应的 RISC-V GCC 搜索路径和 compiler-rt 路径与发行版目录不同。SG2044 使用上游已有 `--gcc-triple=riscv64-openruyi-linux` 后，带 GNU target 的编译、链接、执行及 HSA CMake 消费者通过。15 个已设 GNU target 的配方逐包补充该选项，包括 RCCL 自定义 device-linker 和 bandwidth-test 外部 HIPCC 子构建。
- rocBLAS 已完成 486 个编译任务和全部 Tensile 生成，在最终链接因 GNU triple 下不存在 `libclang_rt.builtins.a` 失败；RCCL 同类错误涉及 `libclang_rt.profile.a`。`74513aa` / `7196ce0` 用 Clang 标准 `-resource-dir` 指向构建目录内的资源别名，复用系统原有 native compiler-rt、头文件及设备库；不改系统 LLVM、不禁用覆盖率、不伪造运行库。实际两架构的 compiler-rt 链接/运行/覆盖率数据读取通过，x86_64 gfx1100/gfx1200 HIP 编译和 RCCL Fabric 探测也通过，见 `validation/compiler-resource-*`、`rccl-feature-resource-x86_64.log`。
- 上述 15 包独立提交和 pre-commit 均通过，连同 HIP 修复推送至 `6ad423c`。OBS 完整重建尚待结果；后续继续全部数学库依赖链与原生实际产物验证。
