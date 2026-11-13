# ROCm 10.1.0 全栈进度

本任务包括原有 33 个 ROCm 源码包，并补入 10.1 新依赖 rocm-stinkytofu 和 LLVM 24 支持包 rocm-clang（共 35 个）。基础包阶段已完成，持续推进剩余组件；x86_64 是快速验证，riscv64 是最终验收。构建成功与实际 RPM 功能验证分别记录；用户已明确本阶段先完成无 GPU 验证；GPU 运算另列为未验证。

源码统一基线：rocm-systems `therock-10.1` → `7da43026e4f2ef7600433c38c820732f7a205d22`；rocm-libraries → `39d8d60365d2272a5366f76ccb3bfba24b219eaf`。TheRock 固定 half `207ee58595a64b5c4a70df221f1e6e704b807811`（与旧配方相同），HIPIFY `0e051929fe80ccc0af6dc194ddb990aa82eec97d`。归档校验值逐包核实并记入 SPEC。`rocm-bandwidth-test` 不在 systems 10.1 发布中，也无 therock-10.1 标签；采用独立仓库最新标签 `rocm-7.2.4` 的固定提交 `06dd9df114855ed2dc38cd731ad214066a62d6da`（从旧 6.4.2 升级），RPM 保留其真实发布版本 7.2.4，依赖 10.1.0 HSA。上游证据与实验目录：工作区 `tmp/rocm10-stack/`。

顺序：独立基础库／管理工具 → HSA 与 HIP 运行时 → 基础模板库／随机数库 → BLAS／FFT／稀疏矩阵 → 求解器和 MIOpen。独立包可同时构建，避免等待一个包阻塞全部工作。

| 源码包 | 当前步骤 | x86_64 | riscv64 |
| --- | --- | --- | --- |
| amdsmi | 本阶段无 GPU 验证通过 | succeeded；实际 Python 模块/27.1 版本 API | succeeded；实际 Python 模块/27.1 版本 API |
| half | 本阶段无 GPU 验证通过 | succeeded；CMake/half 运算 | succeeded；CMake/half 运算 |
| hipblas | 继续构建／实际 RPM 验证 | succeeded；CMake/3.7.0 属性 API | unresolvable；依赖待解 |
| hipblas-common | 本阶段无 GPU 验证通过 | succeeded；CMake/枚举 API | succeeded；CMake/枚举 API |
| hipblaslt | 继续构建／实际 RPM 验证 | building；跟踪新结果 | unresolvable；依赖待解 |
| hipcub | 本阶段无 GPU 验证通过 | succeeded；CMake/BlockReduce 离线 gfx1100/1200 | succeeded；CMake/BlockReduce 离线 gfx1100/1200 |
| hipfft | 继续构建／实际 RPM 验证 | succeeded；CMake/版本 API | unresolvable；依赖待解 |
| hipify | 本阶段无 GPU 验证通过 | succeeded；实际资源发现/CUDA→HIP 声明夹具 | succeeded；实际资源发现/CUDA→HIP 声明夹具 |
| hiprand | 本阶段无 GPU 验证通过 | succeeded；CMake/版本/Philox 256 CPU 样本 | succeeded；CMake/版本/Philox 256 CPU 样本 |
| hipsolver | 继续构建／实际 RPM 验证 | succeeded；CMake/Jacobi 配置与非法参数 API | unresolvable；依赖待解 |
| hipsparse | 继续构建／实际 RPM 验证 | succeeded；CMake/矩阵描述符 create/set/get/destroy | unresolvable；依赖待解 |
| hipsparselt | 继续构建／实际 RPM 验证 | building；跟踪新结果 | unresolvable；依赖待解 |
| miopen | 继续构建／实际 RPM 验证 | unresolvable；依赖待解 | unresolvable；依赖待解 |
| python-tensile | 本阶段无 GPU 验证通过 | succeeded；Python/CLI、生成 helper 并离线编译 gfx1100/1200 | succeeded；Python/CLI、生成 helper 并离线编译 gfx1100/1200 |
| rccl | 继续构建／实际 RPM 验证 | succeeded；3 CTest+110 micro-tests、CMake/23007 版本 API | building；跟踪新结果 |
| rocblas | 本阶段无 GPU 验证通过 | succeeded；CMake/5.7.0 版本 API、四架构 catalog | succeeded；CMake/5.7.0 版本 API、四架构 catalog |
| rocclr | 本阶段无 GPU 验证通过 | succeeded；HIPRTC gfx1100 ELF、实际 HIP 离线编译 | succeeded；HIPRTC gfx1100 ELF、实际 HIP 离线编译 |
| rocfft | 继续构建／实际 RPM 验证 | succeeded；CMake/版本 API、RTC helper gfx1100/1200 | unresolvable；依赖待解 |
| rocm-bandwidth-test | 本阶段无 GPU 验证通过 | succeeded；4 项 CPU CLI/插件发现（无 GPU） | succeeded；4 项 CPU CLI/插件发现（无 GPU） |
| rocm-clang | 继续构建／实际 RPM 验证 | succeeded；上游诊断、实际 HIP/RDC/LTO 编译链接 | scheduled；跟踪新结果 |
| rocm-cmake | 本阶段无 GPU 验证通过 | succeeded；32 CTest、实际模块/安装/消费者 | succeeded；32 CTest、实际模块/安装/消费者 |
| rocm-core | 本阶段无 GPU 验证通过 | succeeded；CMake/版本 API | succeeded；CMake/版本 API |
| rocm-llvm | 本阶段无 GPU 验证通过 | succeeded；COMGR、HIP/设备库离线编译 | succeeded；COMGR、HIP/设备库离线编译 |
| rocm-origami | 本阶段无 GPU 验证通过 | succeeded；CMake/gfx1100 硬件模型 API | succeeded；CMake/gfx1100 硬件模型 API |
| rocm-smi | 本阶段无 GPU 验证通过 | succeeded；CLI/版本 API（无 GPU） | succeeded；CLI/版本 API（无 GPU） |
| rocm-stinkytofu | 继续构建／实际 RPM 验证 | succeeded；产物验证待完成 | building；跟踪新结果 |
| rocminfo | 本阶段无 GPU 验证通过 | succeeded；无 GPU 诊断/目标枚举 | succeeded；无 GPU 诊断/目标枚举 |
| rocprim | 本阶段无 GPU 验证通过 | succeeded；BlockReduce 离线 gfx1100/1200 | succeeded；BlockReduce 离线 gfx1100/1200 |
| rocprofiler-register | 本阶段无 GPU 验证通过 | succeeded；132 上游测试、CMake/错误 API | succeeded；132 上游测试、CMake/错误 API |
| rocr-runtime | 本阶段无 GPU 验证通过 | succeeded；CMake/状态 API、280 符号 | succeeded；CMake/状态 API、280 符号 |
| rocrand | 本阶段无 GPU 验证通过 | succeeded；CMake/版本/Philox 256 CPU 样本 | succeeded；CMake/版本/Philox 256 CPU 样本 |
| rocsolver | 继续构建／实际 RPM 验证 | succeeded；CMake/3.37.0 版本 API | unresolvable；依赖待解 |
| rocsparse | 继续构建／实际 RPM 验证 | succeeded；CMake/矩阵描述符 create/set/get/destroy | unresolvable；依赖待解 |
| rocthrust | 本阶段无 GPU 验证通过 | succeeded；transform 离线 gfx1100/1200 | succeeded；transform 离线 gfx1100/1200 |
| roctracer | 本阶段无 GPU 验证通过 | succeeded；CMake/版本 API | succeeded；CMake/版本 API |

表格状态采集时间：2026-11-13T21:11:07.229528+00:00；下方追加记录保留历史诊断。

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

## 后续检查点：HIP 原生通过与 LLVM 前端阻塞

- 用户已明确“暂无 [带 AMD GPU 的 riscv64 机器]，先完成无 GPU 验证”。本阶段完成条件为全部包的 riscv64 构建、实际 RPM 的 CPU/API 和离线编译验证；GPU 数值计算另列为未验证，不等待 GPU 机器才推进交付。
- HIP 10.1.0-6.1 双架构构建成功。riscv64 在 v100-01:0 耗时 1296 秒；实际 SG2044 RPM 的 HIPRTC 生成 gfx1100 的 4544 字节 ELF，版本 71600000、编译日志为空。证据 `validation/hiprtc-native-riscv64.log`。原生下游已解锁，含 rocBLAS、rocRAND、rocPRIM、Origami、ROCtracer 和带宽工具。
- rocBLAS 10.1.0-8.1 x86_64 完整构建成功（1281 秒），实际 RPM CMake/版本 API 通过，组件版本 5.7.0。产物包含四个 gfx1100/1101/1200/1201 lazy catalogs，共 40 个 .co、220 个 .hsaco、260 个 .dat；GPU BLAS 运算未执行。证据 `validation/rocblas-consumer-x86_64.log`。
- RCCL `7fe59b7` 补齐新版设备 API 头文件、tuner 数据、测试程序与 profiler stub 清单；`d83bfca` 增加 ROCTX 开发依赖。原构建缺失 roctracer-devel 后静默启用 NVTX stubs，当前源码的直接 NVTX 包含导致重复定义和缺失传递声明。最小头文件复现 `validation/rccl-roctx-headers/` 证实开启 ROCTX 后通过，关闭时重现错误。x86_64 完整构建成功，3 项生成器/telemetry CTest 和 110 项 CPU micro-tests 全通过；实际 CMake 联合消费者输出 RCCL 23007、rocBLAS 5.7.0 及两种不同错误字符串，见 `validation/blas-rccl-x86_64.log`。
- 默认 host triple 已找到直接对应的 LLVM 上游 PR [216938](https://github.com/llvm/llvm-project/pull/216938)，提交 `607dab5767199b4eef74b2b718a73e778e783f17`，将 linker-wrapper 的 host bundle triple 归一化为四段。该 PR 尚未合并，不能写成已合入上游。用本机 snapshot b1de84ea 的工具源码原样回移后，在 x86_64 与 SG2044 都完成不指定 GNU target 的 gfx1100/gfx1200 HIP 编译和共享库链接。证据 `llvm-driver-review/linker-wrapper-probe/`；仅临时工具实验，系统工具未替换。
- rocSPARSE 完整构建遇到设备函数静态 constexpr 变量调用设备 constexpr helper，被误判为宿主全局初始化。LLVM 上游 PR [233925](https://github.com/llvm/llvm-project/pull/233925)，提交 `6b8c5dd883ca6fc2a29e39d35b72fbadeb4a4a26`，直接修正该执行空间检查，尚未合并；较大的 PR 222985 处理不同的静态初始化规则，不作为必要前置回移。ROCm develop 的 sizeofarray 调用和本资产一致，未发现 ROCm 侧已合入修复。
- 正在准备独立 `SPECS/rocm-clang/`，从系统 snapshot 的同一完整提交构建 Clang 和 linker-wrapper，复用系统 LLVM shared library，不重建 LLVM/运行库。安装到 `/usr/lib64/rocm/llvm24`，携带上述两项有来源的上游候选修复及原发行版目标配置；发行版 GCC 搜索列表补丁存在缺失逗号，此副本校正该排版错误。源码 SHA-256 已验证为 `84d435841d4227537f27ba89ca7647013264b380050c520b28c74e452e466963`，完整解包和 fuzz=0 应用检查仍在进行，尚未接入 OBS。下一步验证 standalone CMake 配置、提交本支持包、接入 ROCm10，然后让 rocSPARSE 使用它。不要仅为通过编译自行改写 sizeofarray 逻辑。

### 独立 Clang 已接入（最新恢复入口）

- 新增支持包后共 35 个 OBS 源码包。`rocm-clang` 配方 `6a2dd2a`、offload 检查依赖 `61cfc2c`、GCC 的 LLD 选项修复 `8f5de87`、LLVMConfig 导入依赖补齐 `fb8f7e9` 均已推送。包 `_service` 已核实仅取 `rocm10/SPECS/rocm-clang/*`；全部四个补丁在精确 snapshot 归档上 fuzz=0 应用，见 `rocm-clang-patch-check.log` / `rocm-clang-source-check.log`。PR 233925 的 SemaCUDA.cpp 在 SG2044 用真实 snapshot headers 已编译为对象，`validation/SemaCUDA-upstream-233925-build.log` 为空且命令成功。
- `rocsparse` 配方 `d9a77e1` 显式依赖新工具，通过 HIP_CLANG_PATH、PATH 和 CMAKE_HIP_COMPILER 选择独立编译器。未改写算法/sizeofarray。Clang 支持包两架构均在大型 worker 上构建，x86_64 `epyc-massive-01-n0h:9`，riscv64 `sg2044-0317:8`；先前两项配置失败分别为 GCC 不接受绝对 -fuse-ld 路径、缺失 LLVMConfig 导入的 LibLZMA target，已修复，等待新完整结果。
- 最新快照 x86_64 26 succeeded、8 依赖待解、Clang building；riscv64 18 succeeded、11 依赖待解、6 building。该计数不代表 35 包已完成验收。继续跟踪 Clang→rocSPARSE→rocSOLVER→hipBLAS→hipBLASLt→MIOpen 及其余依赖分支，原生 rocBLAS/RCCL 仍在构建。
- 原生实际 RPM 新增：Origami gfx1100 硬件模型和 ROCtracer 4.1 API 通过（`validation/native-model-riscv64.log`）；rocPRIM/rocThrust 联合 block reduction 和 transform 的 gfx1100/gfx1200 编译通过（`validation/template-kernel-native-riscv64.log`，对象在 SG2044）。无 GPU 执行。
- 全部临时构建源码与补丁检查保留于 `sh-plct-sg2044:/home/openruyi/tmp/rocm10-clang/`。此处完整 LLVM 归档已解包；不要重复下载/解包或反复对已应用源码再次 patch。验证 root 的 standalone CMake 探测因未 staging LLVM 静态库被 LLVMExports 拒绝，不是 OBS 开发包缺失的证据；OBS 通过 llvm24-devel 自动安装对应静态开发包。

### 实际 RPM 与安装目录检查（继续跟踪）

- 用户休息前要求继续把列表全部包构建、验证完成；持续推进全部 35 包及 riscv64 无 GPU 验收，不在检查点停止。
- Clang `41c4624` 补齐直接 cc1 调用的 lit resource include；随后 host/device 两项上游诊断测试、host triple 检查、rocSPARSE 模式语法复现全部通过。README 清单误用旧文件名，`f8fbf15` 改为归档中存在的根 README.md。x86_64 首个 RPM 为 `24.0.0~git20261109.b1de84e-7.1`，构建/测试/出包成功，但实际 RPM 的 HIP 编译暴露 linker-wrapper 仍需未打包 libclangBasic.so.24.0，故尚未验收通过。
- `9691be3` 明确 BUILD_SHARED_LIBS=OFF，让 wrapper 的 Clang 内部组件静态链接，保留 driver 使用的 monolithic clang-cpp；新增只用安装目录库执行 HIP 对象编译的检查，避免 build/lib 掩盖安装缺项。`582a948` 令 rocSPARSE 要求 release>=8，等待修正后的工具，防止继续使用已知不完整的 7.1。新完整构建仍在进行。
- 实际工具验证脚本 `validation/private-clang.py` 在隔离 runner 内将私有 lib 置于 LD_LIBRARY_PATH 首位；runner 原默认会优先加载系统 clang-cpp，不能把那种混用算成候选前端验证。真实 OBS 构建无此测试 runner 的环境覆盖。原失败证据为 `validation/rocm-clang-rpm-before-component-fix-x86_64.log`，后续新产物验证写回 `rocm-clang-rpm-x86_64.log`。
- rocRAND 与 hipRAND 原生构建完成，实际 RPM 的联合 CMake/API/Philox 验证通过：版本 API 均 500000、256 个样本可重复且两接口一致；同一消费者的 StinkyTofu/Origami/ROCtracer API 通过，见 `validation/math-consumer-native-riscv64.log`。构建目录首次新建并实际编译、链接、执行；SG2044 时钟比 RPM mtime 慢约 319 秒，Make 有 clock-skew 提示，未修改机器全局时钟。
- rocminfo 实际 riscv64 RPM 在无 GPU 环境正常给出 ROCk 未加载诊断并返回 1；显式 ROCM_TARGET_LST 配置枚举正确输出 gfx1100/gfx1200。证据 `validation/rocminfo-native-riscv64.log`，GPU agent 发现未验证。
- 原生 rocBLAS 完成全部 Tensile 生成（约 2322 秒），现编译库本体；RCCL、hipCUB、FFT、带宽工具及 Clang 的原生构建继续跟踪。后续仍先修 Clang→rocSPARSE 主链，并及时验证已发布的实际 RPM。

### 主链继续推进（最新记录）

- RCCL 原生后段在 net/coll_net 的通用路径缺少 ncclGdrCudaRead。`9d1ba71` 回移已合并 ROCm 提交 `6305765daacadbbef27e921c1907f13674e71fbd`（PR 10519，2026-09-14 合并），仅去掉 projects/rccl 路径前缀；两文件 fuzz=0 应用，无源码前置提交。上游在 PPC64LE/MI210 验证过，当前 RISC-V 仅做构建/CPU 范围，不声称 GPU DMA ordering 已验证。两个架构正在重建。
- rocSOLVER 源码明确强制 --rtlib=compiler-rt，`b28c3e3` 提前复用已验证的构建内 resource-dir aliases，覆盖 CXX/HIP 及 RISC-V GCC 参数；未等待全库编译完再处理同类路径错误。
- `78c2091` 给安装目录 HIP 集成检查补上真实 HIP runtime 声明及设备库依赖；先前 raw fixture 在 codegen 阶段缺少 hipLaunchKernel 声明，属于测试夹具缺项。`8c5eb6b` 过滤私有 cpp 的全局 Provides，实际 10.1 RPM 只提供包名/ISA，见 `validation/rocm-clang-provides-x86_64.log`。
- Clang 10.1 RPM 的完整 HIP 编译/链接通过，但 rocSPARSE 默认 LTO 探测暴露私有前缀无 LLVMgold.so。`34d32ed` 加入指向同 snapshot 系统 LLVMgold.so 的 symlink，补齐运行工具依赖并新增安装目录默认 LTO 编译/执行检查。Clang 11.1 x86_64 出包/检查及实际 RPM 验证通过：资源目录为系统 /usr/lib64/llvm24/lib/clang/24，constexpr 复现、gfx1100/gfx1200 编译和共享库链接成功，见 `validation/rocm-clang-rpm-x86_64.log`。原系统编译器对同一真实 HIP 夹具仍报 global initializer 错误，negative control 日志已保存。
- 注意验证环境 /usr/lib64 下本来就有指向系统 cpp 的 SONAME symlink，所以不能仅移除 LLVM 专用 LD_LIBRARY_PATH 而保留 /usr/lib64 优先；那仍会误载旧前端。`validation/private-clang.py` 最终恢复私有 cpp 首位选择，实际测试已成功；继承该环境的系统子工具可能有无版本信息提示，ABI 源码基线一致，保留日志。常规 OBS 环境不带该 runner 的路径覆盖。
- rocSPARSE 的新 buildinfo 已解析到 rocm-clang 11.1，但旧失败未自动重试，已仅对 amd64_build/x86_64 执行一次 osc rebuild。现完整构建已推进到 618/622，原 constexpr 诊断消失；尚未将全库标记成功。
- hipCUB 原生完整构建成功，实际 6.1 RPM 的独立 CMake 导入及 BlockReduce gfx1100/gfx1200 编译通过（`validation/cub-consumer-native-riscv64.log`）。此前底层 LP64D note 未令链接失败，不将该 note 误报为构建错误。
- 原生 bandwidth 7.2.4 工具的四项 CPU CLI/插件检查全部通过，补入验证 root 的依赖为 parent spdlog 1.15.3-4.21。证据 `validation/bandwidth-cli-native-riscv64.log`、`bandwidth-cli-cpu-riscv64.json`；GPU engine 不在本阶段验证范围。
- 当前仍需完成全部 35 包；原生 rocBLAS 已至 485/489，FFT 正在编译，Clang/RCCL 需等待大型 worker。继续主链、实际 RPM 验证及最新 source/build revision 核对，不在记录点结束。

### 稀疏包装库与 Tensile 实际产物（继续执行）

- rocSPARSE 10.1.0 完整 x86_64 构建成功（1311 秒），实际 RPM 的 CMake 导入、矩阵描述符创建、默认值、set/get、销毁通过，见 `validation/rocsparse-consumer-x86_64.log`。原生仍待 rocBLAS 与 rocm-clang。
- hipSPARSE 新版 benchmark 的 clients-common 无条件需要 GTest；`ee49526` 将 GTest 构建依赖移出 GPU 测试条件。重建成功，实际 RPM 同类描述符消费者通过，见 `validation/hipsparse-consumer-x86_64.log`；未启用或执行 GPU 测试。
- hipSPARSELt 配置失败于缺少 StinkyTofu 的 rocisa 转换源码。上游明确这两份源文件包含 rocisa 类型、定义其 Python binding，应编译进 `_rocisa` 而非 libstinkytofu；仅依赖 StinkyTofu devel 包不够。`1e8e6a5` / `2596d9e` 分别为 hipSPARSELt/hipBLASLt 增加同一 `therock-10.1/stinkytofu.tar.gz`（已核实 acc43368… 校验值），恢复它们预期的 `shared/stinkytofu` 源码相对布局。无需修改转换源码或 CMake，find_package 仍复用系统 StinkyTofu。新 hipSPARSELt 已越过配置进入 `_rocisa` 编译。
- python-tensile 的实际 RPM 在两个架构均完成 GEMM beta helper 生成，并经实际 LLVM 24 编译、解 bundle，确认 gfx1100/gfx1200 的 ELF machine=AMDGPU；证据 `validation/tensile-generator-x86_64.log` / `tensile-generator-native-riscv64.log`，生成源码、设备 ELF 和 JSON 在对应目录。按上游构建方式启用 `__HIP_HCC_COMPAT_MODE__=1`；可选 joblib 缺失仅导致串行，本检查未声称完整 GEMM 性能调优或 GPU 运算通过。
- RISC-V 大 worker 仍有其他项目的合法长任务，不能修改/中止它们。SG2044 测试机有 64 个可用 CPU、约 128 GiB 空闲内存，因此额外安排独立原生 Clang 源码预构建，以提前暴露原生问题；它不能替代 OBS RPM 验收。4.24 GB 的 llvm24-static 只在 SG2044 下载，随后转存 `build-dependencies/llvm-static/`，不混入常规运行验证的自动依赖解包。脚本为 `prepare-native-clang.py` / `build-native-clang.sh`；构建日志在 SG 的 `native-clang-prebuild.log`。完整 snapshot 源码已经应用四补丁，不要重复打补丁。
- 为避免大型原生产物挤满本机，新增任务脚本 `fetch-native-artifacts.py` / `download-native-public.py`：先核实 ROCm10 成功状态、取得 OBS 实际 binary 清单，再在 SG2044 从本项目发布仓下载，校验大小和 RPM digest。后续通过 SG 的 `stage-artifacts.py riscv64 <包>` 进入隔离验证 root；勿在本机解包原生 RPM。全部包继续跟踪，不在此处结束。

### RDC 宿主 ABI 与求解器（最新恢复入口）

- rocBLAS 10.1.0-8.1 原生完整构建成功，实际 RPM 的 CMake 导入、链接及 5.7.0 版本 API 通过，见 `validation/rocblas-consumer-native-riscv64.log`。两架构的产物均含 4 个 lazy catalogs、40 个 .co、220 个 .hsaco、260 个 .dat；尚无 GPU BLAS 数值计算验收。
- rocFFT 原生最终 RDC 链接失败于 double-float/soft-float 混合。最小真实 HIP RDC 共享库复现也失败，保存的 wrapper ELF flags=0x0；失败不依赖 RPM LTO 开关。找到直接对应的 LLVM PR [168164](https://github.com/llvm/llvm-project/pull/168164)，完整 head `58708298d039e73215a396b7955201881c3c5a3c`，仍未合并。`1722cf5` 将其作为第三项实验性上游候选回移到 rocm-clang。保留 snapshot 新版 LibraryOptionsContext/codegen API，并按当前 Clang::ConstructJob 已有的 auxiliary host triple / host Args API 选择宿主参数；无额外源码前置提交。补丁在精确 snapshot 上 fuzz=0 应用。
- 原生 wrapper 单独预编译后，以 +f,+d 参数按 PR 机制生成 flags=0x4，完整 RDC 共享库链接通过（`validation/rdc-upstream-wrapper-native-riscv64.log`）。这是先行的 wrapper 机制实验，不替代完整 driver/RPM 验收。
- Clang 12.1 x86_64 完整构建成功。安装目录检查新增跨目标 RISC-V host-features dry-run 和 HIP RDC 共享库链接；实际 RPM 的 gfx1100/gfx1200 普通/RDC 编译链接、默认 LTO 编译/运行、资源路径及驱动传递检查通过，见 `validation/private-clang-current-x86_64.log` / `private-clang-current-x86_64/result.json`。仍保留子工具载入私有 cpp 时的无版本信息提示。
- SG2044 已独立完成含全部 5 个补丁的 Clang 原生源码构建（1560 个任务），使用同 snapshot 系统 Clang bootstrap；该实验不等于 OBS 使用 GCC bootstrap 的 RPM 构建。DESTDIR 为 `clang-native-install/`，没有写入宿主系统。普通/RDC gfx1100/gfx1200、LTO 执行和 host feature 转发均通过，见 `validation/private-clang-source-riscv64.log`。正式原生 Clang RPM 现已在 v100-01:3 构建，完成后必须验证实际 RPM。源码构建日志实际保存在本机 `tmp/rocm10-stack/native-clang-prebuild-launch-v2.log`，首个自动 launcher 因未导入签名 key 返回失败的日志已保留，随后明确用 --nosignature 验证 package digests，不能称为已验证 GPG 签名。
- `a583281` 使 rocFFT 要求 rocm-clang release>=12，并选择其 CXX/HIP 工具路径；保留系统 C 编译器、OpenMP 库目录和所有 GPU targets。两个架构完整重建待结果。
- rocSOLVER 与 hipBLAS x86_64 构建、实际 RPM CMake/API 通过，组件分别 3.37.0、3.7.0，见 `validation/solver-blas-consumer-x86_64.log`。hipSOLVER 10.1 新增 geev 的 CPU LAPACK fallback，默认会通过 ExternalProject clone OpenBLAS；`aed940d` 使用上游 HIPSOLVER_INTERNAL_LAPACK_BUILD=OFF 和 lapack-devel。完整构建及实际 Jacobi 配置/非法参数 API 通过，见 `validation/hipsolver-consumer-x86_64.log`；没有声称 GPU 求解器或 geev 执行通过。
- hipBLASLt 的外部算子 AMax 在 gfx11/gfx12 输出 legacy Fake16 v_max_f16。上游 bf56af2e… 的完整 true16 特性提交跨 rocisa/StinkyTofu 38 个文件，并非本次 release 的小型 ABI 修复。沿用 LLVM 已有的 -real-true16 兼容模式，仅给该包外部算子的 CMake ASM TUs；不更改指令生成源码或重建 StinkyTofu ABI。四个目标的 v_max_f16/abs legacy 与 .l 写法生成完全相同 .text，见 `llvm-driver-review/amax-asm-mode-validation.json`。`fa62772` 已推送，完整重建正在 Tensile 生成阶段；后续仍需看完整结果。
- 原生仓库尚未发布某些新 RPM，直接公共仓下载 rocBLAS 返回 404。`fetch-native-artifacts.py` 已改为从本机有认证的 osc API 直接流式传至 SG2044，不在本机保存大型原生 RPM，也不传输凭据；之后校验大小与 RPM digest，再写 current manifest。此前“只从发布仓下载”的描述是首次实现，最终入口以此为准。
- 原生通用消费者脚本 `validation/run-native-api-consumer.py <包>` 已同步到 SG2044，覆盖待验收的 BLAS/sparse/solver/Lt/MIOpen。Clang 实际工具检查为 `validate-private-clang.py`（默认实际安装前缀）；ROCM10_CPP_PREFIX 与 ROCM10_CLANG_RESULT_LABEL 仅用于上述源码预构建，最终 RPM 验收不要设置它们。持续检查 `watch-results.log` / `obs-live-state.json`，另用 monitor.py 保留完成日志；当前仍有包未完成，不在本检查点停止。

### True16 主内核回移（覆盖前一检查点的临时方案）

- hipBLASLt 的外部 ASM TUs 选择 Fake16 后，完整 Tensile 主内核仍失败：工具主动带 +real-true16，但生成 v_cvt_f16_f32 v15, v14 等无 half selector 的操作数。不能把外部 ASM 修好当成完整库通过，也不能把“机器码相同”扩大成混合语法已正确。临时 CMAKE_ASM_FLAGS 已从最终配方移除。
- 已回移 **完整**已合入 ROCm 提交 [bf56af2e53b7ba22b4ac86e8d8cd25df8040b0f2](https://github.com/ROCm/rocm-libraries/commit/bf56af2e53b7ba22b4ac86e8d8cd25df8040b0f2)（PR 10052，2026-09-18），按 projects/hipblaslt 与 shared/stinkytofu 两个 subtree 拆分，仅去掉路径前缀。两部分都在实际 therock-10.1 归档对应文件上 fuzz=0 应用，无额外源码前置提交；包含上游测试与全部配套变更，不只摘取 AMax 单行。检查证据为 `llvm-driver-review/true16-{hipblaslt,stinkytofu}-release-check.log`。没有手工重写转换算法。
- `399239a` 为 rocm-stinkytofu（预期 release 5.1），`ddfb162` 为 hipBLASLt，`8d62bca` 为 hipSPARSELt 的对应转换源码；两项 Lt 包要求 StinkyTofu devel>=10.1.0-5，避免新胶合代码使用旧库/旧头文件。hipSPARSELt 同时 patch 其 bundled hipBLASLt；同一源归档版本和同一完整上游提交配套。
- `3fc0660` / `6ba44a6` 在两个 Lt 包先构建 `_rocisa`，随后执行上游 `test_amax_true16_activation.py` 的纯宿主回归，最后才生成完整设备库。pytest 的 confcutdir 限于 unit 目录，避免上层 GPU 分配 fixture；文件自身按 gfx1100/1101/1102/1103/1150/1151/1152/1153/1200/1201/1250 强制目标检查 half-selector，不依赖 GPU。测试尚待新 OBS 构建的真实结果，不能提前标记通过。
- 旧 StinkyTofu 4.1 的双架构 1500 CTest/实际 RPM 验证证据保留；新 5.x 须重新跟踪完整测试并验证实际 RPM。因此表格暂时撤下该包当前产物的通过标记。两个架构的新 StinkyTofu 正在构建，下游等待对应新开发包。
- rocFFT 使用 Clang 12.1 的 x86_64 完整重建已经成功；新实际 RPM 的版本/plan description API、RTC helper gfx1100/gfx1200（各 4544 字节 ELF）及已编译 hipFFT 联合消费者再次通过，见 `validation/fft-api-rtc-rdc-x86_64.json`、`fft-api-rdc-x86_64.log`。原生 FFT 仍待正式 Clang RPM。
- 当前所有工作继续；优先跟踪新 StinkyTofu→Lt 主链、原生 Clang→rocSPARSE/FFT、RCCL，以及后续 MIOpen。原生 rocBLAS 已验收，无需为这个检查点重建它。最新 Git HEAD `6ba44a6`（文档提交之前），不要把旧 feature 之前的成功日志算作新修订结果。
