# ROCm 10.1.0 与系统 LLVM 24 移植计划

本任务在 openRuyi 上使用系统 `llvm-snapshot`（LLVM 24）移植 ROCm 10.1.0。按用户于 2026-11-13 确认的顺序，以 `rocm-cmake` → `rocm-llvm` 推进。x86_64 用于快速验证和推进依赖链；最终验收以 riscv64 为准。两项基础包均通过 riscv64 最终验收后，才开始其余组件。本文件是本任务的持续计划与上下文恢复入口，适用范围仅为 `rocm10` 实验分支。

## 当前检查点

最后更新：2026-11-13。当前阶段：rocm-cmake 已通过双架构构建及 riscv64 最终功能验收；rocm-llvm 首轮配方已推送，两个架构正在构建。

| 阶段 | 状态 | 证据与下一步 |
| --- | --- | --- |
| 分支及 workflow 初始化 | 已完成 | 初始化提交 `0102982542b5ec2e60bae2fdc9a49ceab2cc770b` 已推送；[Actions 43407438828](https://github.com/Sakura286/rocm-specs/actions/runs/43407438828) 成功，但没有触发任何包 |
| 源码基线核实 | 标签和提交已确认 | 两包均使用 `therock-10.1`；归档 SHA-256 已记录于 SPEC，补丁已按新源码审查 |
| rocm-cmake | 最终验收通过 | 双架构构建／发布、32 项 CTest 及实际 RPM 功能验证通过；详见文末验收记录 |
| rocm-llvm | 首轮 OBS 构建中 | 配方 `874d465` 已推送，Actions 43412226757 成功；系统 LLVM 24，COMGR API 3.5，device-libs 和 COMGR CTest 已启用 |
| 其余组件 | 未开始 | 两项基础包验收完成后再确定依赖顺序 |

最近一次 OBS 查询（2026-11-13 初始化时）：`home:Sakura286:ROCm10` 已存在，无软件包，项目 `_config` 为空。新项目的真实包服务调用、token 权限、取源和构建链路尚未验证。开始执行时重新读取远端状态，不将这个时间点的结果视为实时状态。

ROCm10/rocm-cmake 已完成取源、构建、发布和最终验证。本地初次全量 CTest 的失败及修正后日志保留在 `tmp/rocm10-rocm-cmake/logs/`。初始配置证据位于工作区 `tmp/rocm10-setup/`。旧主线构建结果不计入本任务验收。

| 包 | x86_64 快速验证 | riscv64 构建和发布 | riscv64 产物功能验证 | 最终验收 |
| --- | --- | --- | --- | --- |
| rocm-cmake | 通过 | 成功并发布 | 目标机通过 | 通过 |
| rocm-llvm | 构建中 | 构建中 | 未开始 | 未通过 |

## 固定边界和目标环境

| 项目 | 本任务约定 |
| --- | --- |
| 工作区 | `/home/infinity/Desktop/or` |
| 配方副本 | `rocm-specs-rocm10/` |
| Git remote 和分支 | `git@github.com:Sakura286/rocm-specs.git`，`rocm10` |
| OBS 项目 | `home:Sakura286:ROCm10` |
| OBS API | `https://pickaxe.oerv.ac.cn` |
| 本地 OBS 项目目录 | `obs/home:Sakura286:ROCm10/`，用于服务配置和状态核查，非配方权威来源 |
| 快速验证 | `amd64_build/x86_64`，依赖 `openruyi/x86_64` |
| 最终验收 | `riscv64_build/riscv64`，依赖 `openruyi/riscv64`；要求构建、产物及功能验证通过 |
| RISC-V 运行验证入口 | `ssh sh-plct-sg2044` |
| ROCm 产品基线 | 10.1.0；源码标签及组件自身 API 版本分别记录 |
| 工具链 | openruyi 的 `llvm-snapshot` 产出的 LLVM／Clang／LLD 24 及相应开发库 |
| 配方权威来源 | 本分支 `SPECS/<包名>/`；修复以 SPEC、补丁、配套文件形式保存 |
| 提交身份 | `CHEN Xuan <chenxuan@iscas.ac.cn>` |

主线副本 `rocm-specs/`、`main` 分支和 `home:Sakura286:ROCm` 继续其独立任务。本任务不向主线推送，不批量迁移其他包，不将主线 OBS 项目添加为依赖来源。可读取旧实验的诊断和测试脚本作为参考，但复用前核对源码版本及路径。

x86_64 验证用于尽早发现错误和减少依赖链等待。rocm-cmake 的 x86_64 产物可用且快速功能验证通过后，可开始 rocm-llvm 的 x86_64 移植，同时继续处理 rocm-cmake 的 riscv64 构建和测试，不必串行等待 RISC-V worker。rocm-llvm 的 riscv64 构建仍须使用本项目对应架构可用的新依赖，不能用 x86_64 产物替代。

“快速验证通过”不等于“包已完成”。最终必须在 riscv64 完成下述包功能验证，所测 RPM、工具链及依赖都须对应本次修订。通过目标机执行 CMake 下游项目或编译工具测试时，确认实际加载的是本次产物。真实 GPU/HIP runtime 联调留到相关运行时组件就绪后；本阶段的 riscv64 功能验收验证编译工具及离线生成的 AMDGPU 代码对象，不宣称 GPU 执行已通过。

## 已核实的源码基线

AMD 将 [ROCm 10.1.0](https://rocm.docs.amd.com/en/docs-10.1.0/release/versions.html) 列为 2026-10-05 发布版本。本任务固定使用该版本，不在执行期间自动升级到后续发布或 nightly。

| 组件 | 上游仓库 | 标签 | 标签解引用后的源码提交 |
| --- | --- | --- | --- |
| rocm-cmake | `https://github.com/ROCm/rocm-cmake` | `therock-10.1` | `10155d7272ea1bf79f6b5a9dbc339657af1aa372` |
| rocm-llvm 的 AMD 组件 | `https://github.com/ROCm/llvm-project` | `therock-10.1` | `d6f6cb691863e9258034ab48c1dfce21689d5606` |

完整提交已通过 `git ls-remote` 核实；不要误用 annotated tag 对象本身的 SHA 作为源码提交。参考 [rocm-cmake 发布页](https://github.com/ROCm/rocm-cmake/releases/tag/therock-10.1) 和 [LLVM 源码标签](https://github.com/ROCm/llvm-project/tree/therock-10.1)。源码归档实际下载、SHA-256、顶层目录名、组件版本和许可证仍在各包阶段核实。

产品版本 `10.1.0` 与标签 `therock-10.1` 分开定义。当前 SPEC 的 `therock-%{version}` 和 LLVM 解包目录拼接需要相应调整，不能假设存在 `therock-10.1.0`。

目标 [LLVMVersion.cmake](https://github.com/ROCm/llvm-project/blob/d6f6cb691863e9258034ab48c1dfce21689d5606/cmake/Modules/LLVMVersion.cmake) 声明 LLVM 24.0.0git。相同主版本不保证与 openruyi snapshot 的 C++ API 或 AMD 私有扩展完全兼容。

初始化时查询到 openruyi x86_64 snapshot 产物版本为 `24.0.0~git20261109.b1de84e-11.1.or`。实际构建前重新查询并保存 buildinfo、完整 RPM NEVRA、源码修订及可获得的 LLVM commit；每次重试检查工具链是否发生变化。`llvm-snapshot` 是源码包名，依赖应写实际二进制包名或 `llvm(major) = 24` 等 capability。

## 阶段一 完成交付 rocm-cmake

1. 阅读工作区和本分支 `AGENTS.md`、共享 RPM OBS skill；按需阅读 `homepage/docs/packaging-guidelines/` 中的 `rpmspecification.md`、`sourceurl.md`、`versioning.md`、`patches.md`、`licenses.md`、`buildsystems/cmake.md`，以及构建系统编写指南。
2. 下载并核验 `therock-10.1` 源码，记录完整提交、归档地址、SHA-256 和解包目录。比较 7.14.1 与目标版本的 CMake 模块布局、最低依赖、安装目录和许可证。
3. 审查 `0001-rocm-cmake-follow-cmake-install-rules.patch` 及 SPEC 中两处 libdir 替换；确认哪些已被上游解决，哪些仍需保留或重写。在干净源码上实际应用补丁，避免只修改版本。
4. 更新 SPEC 的产品版本、独立源码标签、归档校验和、依赖、文件清单和必要检查。遵守 openRuyi CMake 构建约定；测试明确传入正确的 `CMAKE_INSTALL_LIBDIR`，x86_64 为 `lib64`。
5. 在 ROCm10 项目创建或复用 `rocm-cmake` 包，配置从 `rocm10` 分支提取 `SPECS/rocm-cmake/*` 的 `_service`。检查包和项目构建设置，避免被遗留禁用设置影响。
6. 完成 SPEC 解析、干净解包和补丁检查、`git diff --check`、相关 pre-commit 检查；单独提交该包并推送 `rocm10`，沿现有 workflow 验证 source service 和 OBS 构建。
7. 从本次 OBS 修订获取实际 RPM，先在 x86_64 隔离环境快速验证模块发现、最小共享库项目配置／构建／安装，以及安装后的导出配置可供下游使用；随后在 riscv64 环境完成同类功能验收。即使 RPM 为 noarch，也须验证其在 RISC-V 环境的实际使用。检查目录归属、依赖、许可证文件和构建路径泄漏。
8. 评估并运行上游适用测试。当前 SPEC 直接跳过 CTest 是待审查项，不能原样继承为“全部测试通过”；失败和跳过项记录具体原因，必要的安装路径回归必须有可复现测试。

### rocm-cmake 快速验证与最终验收

x86_64 快速验证要求源码与配方前置检查通过、真实取源链路正确、`amd64_build/x86_64` 构建及发布成功、实际 RPM 的模块发现和最小下游项目测试通过。达到这些条件即可推进 rocm-llvm 的快速验证；以下清单用于最终验收。

- [x] 配方对应确定的 ROCm 10.1.0 源码，校验和及补丁审查完成。
- [x] Git 提交已推送，workflow 确实调用 ROCm10 项目；OBS `.obsinfo` 中的 Git SHA 与该次配方提交匹配。
- [x] `riscv64_build/riscv64` 构建成功，产物已在本项目对应仓库可用；保留 OBS revision、srcmd5 和发布状态。
- [x] 在 riscv64 环境中，实际 RPM 的模块发现、下游最小项目及安装路径验证通过。
- [x] 测试报告列明执行、失败、跳过项目及理由；核心行为无未解决失败。
- [x] 更新本计划的双架构状态和证据索引，将 rocm-cmake 标记为最终验收通过。

rocm-cmake 尚在等待 riscv64 最终验收时，可推进已具备依赖的 rocm-llvm 快速验证，但不能将 rocm-cmake 标记为完成。单纯观察到 `succeeded` 不满足最终验收。

## 阶段二 完成交付 rocm-llvm

沿用当前包职责：使用系统 LLVM 构建 AMD device-libs、COMGR、hipcc 和相关 RPM 宏。不要把任务改成自建一套 ROCm 私有 LLVM 来绕过系统 LLVM 24 的兼容问题。

1. 在各架构分别核实 rocm-cmake 产物已进入构建依赖解析，并在 rocm-llvm buildinfo 中确认实际使用的是本实验项目的新版本。x86_64 快速验证无需等待 rocm-cmake 的 riscv64 功能验收完成。
2. 下载固定 LLVM 源码，记录 SHA-256；核实 `amd/device-libs`、`amd/comgr`、`amd/hipcc` 的目录和构建方式。读取 COMGR `VERSION.txt`、公共头文件及 CMake 设置，确定 API、SONAME 和包 Provides；不沿用旧的 3.3 假设。
3. 将依赖及安装路径切换到系统 LLVM 24，核实 LLVM／Clang／LLD、静态开发库、libc++ headers、compiler-rt 的包名及完整版本。检查 CMake 查找路径、`llvm-config`、Clang resource directory 和 AMDGPU target 支持，防止回落到 LLVM 23。
4. 逐项审查现有四个补丁和 `rocm-llvm.prep.in`。为每项记录“上游已包含而删除／仍需保留／按新接口重写”，包括 signed-char、device-libs target features、alias diagnostics、COMGR 系统 LLVM 适配、hipcc 路径和 CMake policy 修改。检查每个文本替换实际命中，避免静默失效。
5. 按 device-libs → COMGR → hipcc 顺序排查构建；调整新 API、源码和库依赖。更新宏、子包依赖、CMake 导出文件、许可证及 `%files`，确保没有构建目录泄漏或缺少运行库。
6. 在 ROCm10 项目接入 `rocm-llvm` 的 `_service`；完成前置检查后单独提交并推送。保存每次构建的配方 SHA、OBS 修订、buildinfo、工具链版本和首个有效错误，修复后追加提交。
7. 对实际 RPM 先执行 x86_64 快速功能检查，再在 riscv64 环境执行下述最终验收测试；需要目标机时使用 `ssh sh-plct-sg2044`。必要时在隔离 openRuyi 环境解包或安装产物。依赖和动态库来源必须可追溯，避免使用宿主旧库或旧主线产物造成假通过。

### rocm-llvm 快速验证与最终验收

x86_64 用于快速检查构建、依赖解析及下述核心编译功能并修复问题。以下清单的构建和功能结果必须来自 riscv64；按架构分别记录，不能直接复用 x86_64 结果。

- [ ] 源码、校验和、补丁、COMGR API／SONAME 和 LLVM 24 依赖均已核实。
- [ ] 配方已推送，OBS 取得对应 Git SHA，`riscv64_build/riscv64` 构建并发布成功。
- [ ] buildinfo 及实际运行路径证明使用 openruyi LLVM 24 和本项目 rocm-cmake；记录 snapshot 完整版本。
- [ ] device-libs bitcode 能由目标 LLVM 读取，并参与至少一个代表性 AMDGPU 目标（优先 gfx1100）的离线编译与链接。
- [ ] COMGR 实际共享库可加载，公共 API 和 CMake 导出可被下游编译／链接使用；完成基础编译、device-libs 链接和代码对象生成。
- [ ] 核实 COMGR 的 libc++ headers 来源并验证需要标准 C++ 头文件的编译流程。
- [ ] hipcc／hipconfig 能找到系统 Clang 24 及已安装 device-libs；完成本包范围内的离线设备编译。需要 HIP runtime 才能完成的全程序运行单列为后续集成项。
- [ ] RPM 子包文件、依赖、宏、CMake 配置和许可证检查通过，无构建目录泄漏。
- [ ] 上游适用的 device-libs／COMGR 测试已运行并逐项归因；关键编译、设备库链接、API 行为无未解决失败。
- [ ] 更新本计划的证据、限制和交接信息；确认 rocm-cmake 与 rocm-llvm 均已通过 riscv64 最终验收，随后才开始剩余组件的依赖梳理。

### 必须重新验证的已知问题

旧主线 7.14.1／LLVM 23 曾遇到 AMD 私有 `-mlink-builtin-bitcode-postopt` 选项不被系统 Clang 支持、COMGR offload bundle 接口差异，以及两个原始 OpenCL 测试缺失 `cbrt(float)`／`__printf_alloc` 的最终链接失败。旧实验通过调整 device-lib linking action 获得过成功结果，这不证明原始调用路径通过。

这些是 10.1.0 的回归检查线索，不是已确认仍存在的问题。保留未修改的测试输入和失败日志；若需适配，分别报告原始行为和修改后的行为。不得仅删除测试、删除关键选项而不验证语义，或把调用方绕过方式当作包已完全兼容。

若核心行为仍失败，应继续在这两包及必要适配范围内诊断，不进入剩余组件。若必须修改 openruyi 工具链、改变目标版本或接受功能缺口，先形成具体证据和方案，再与用户确认范围变化。

## OBS 与 Git 执行约定

本任务继续使用共享 [RPM OBS 工作流程](../../skills/rpm-obs-upgrade/SKILL.md)（相对于仓库根目录的工作区入口为 `../skills/rpm-obs-upgrade/SKILL.md`）。每次操作先核对当前分支及目标，不额外建立配方上传流程。

每个包的 `_service` 使用 `obs_scm`，参数为 `scm=git`、`url=https://github.com/Sakura286/rocm-specs.git`、`revision=rocm10`、`exclude=*`、`extract=SPECS/<包名>/*`，后接 `download_files`。初次配置模板来自已验证主线服务，但新项目的实际服务执行仍需验证。

触发凭据权限验证随首包真实调用完成；不将 secret 写入日志。推送前审阅全部待推送提交和变更包；每包使用独立提交，构建修复可追加提交，不擅自改写已发布历史。必要时通过现有 workflow 的 `rocm10` 手动入口补触发指定包。

核对链路为：配方 Git SHA → Actions 运行 → OBS source service → `.obsinfo` Git SHA → OBS source revision／展开 srcmd5 → 构建和发布 → RPM 校验和与功能测试。服务返回 200、workflow 成功、构建成功和功能通过分别记录。

## 证据保存与上下文恢复

计划保存在本文件；稳定映射保存在工作区 `skills/rpm-obs-upgrade/references/projects.md`，不把不断增长的实验日志复制进通用 skill。

| 内容 | 工作区相对路径 |
| --- | --- |
| 分支初始化及源码基线核查 | `tmp/rocm10-setup/` |
| rocm-cmake 源码、构建及验证 | `tmp/rocm10-rocm-cmake/` |
| rocm-llvm 源码、构建及验证 | `tmp/rocm10-rocm-llvm/` |

各包目录按需使用 `sources/`、`logs/<架构>/`、`artifacts/<架构>/`、`tests/<架构>/`、`build/`、`cache/`，架构分别为 `x86_64` 和 `riscv64`；本地命令的 TMPDIR/TMP/TEMP、工具缓存和构建根目录显式指向对应任务目录。远端目标机使用专门的任务目录并记录完整路径，将测试脚本、产物校验和与日志回收至本地对应架构目录。保留失败和成功证据，不覆盖前次日志；不得使用系统 `/tmp`、`/var/tmp` 存放任务文件。

每次阶段切换、推送、构建失败或测试完成后更新顶部检查点。至少记录：当前包和下一步、已推送与未推送改动、上游 commit、配方 SHA、各架构 OBS revision／srcmd5、实际工具链版本、产物校验和、测试结论、日志位置、正在运行的任务标识及阻碍。分别维护 x86_64 快速验证与 riscv64 最终验收进度；没有实际运行的检查写“未验证”，不预填通过。

上下文压缩或新 thread 接手后依次执行：

1. 读取工作区 `AGENTS.md`、本分支 `AGENTS.md`、本计划的当前检查点及共享 skill 对应映射。
2. 运行 `git status --short --branch`，核对 remote、HEAD 和待推送范围；保留用户及其他线程已有修改。
3. 按检查点中的 OBS 修订和日志路径重新查询在途作业，不因上下文缺失重复创建包、重复推送或无依据触发构建。
4. 若阶段状态与 Git／OBS 实际状态不同，先补齐证据并修正检查点，再执行明确记录的下一步。

当前下一步：跟踪 `874d465` 的 OBS 构建，诊断编译及 CTest 失败；随后验证实际 RPM。两架构 LLVM 24 运行依赖已下载至 `tmp/rocm10-rocm-llvm/dependencies/`，校验和见 `logs/runtime-dependencies.json`。本机 LLVM 24 已在隔离环境启动成功；本地 device-libs CMake 配置因未下载大型静态开发库而停止，不能计作功能验证。

## rocm-cmake 最终验收记录

配方提交 `eb9267d`，OBS revision `3`，展开 srcmd5 `e34e934fba9b87f10617c31ac9d8c882`，RPM `10.1.0-3.1.nor`。两个架构均构建并发布成功，各执行 32 项 CTest，通过；4 项排除及原因记录在 SPEC 和 `tmp/rocm10-rocm-cmake/audit.json`。

x86_64 与 `sh-plct-sg2044` 的 riscv64 实际 RPM 均通过模块发现、共享库编译、lib64 安装、CMake 导出与下游导入，以及下游程序运行验证。远端目录 `/home/openruyi/tmp/rocm10-rocm-cmake/`；本地日志、校验和与审计摘要位于 `tmp/rocm10-rocm-cmake/`。验证使用独立解包目录，未替换目标机现有系统包；不是系统升级事务测试。

## rocm-llvm 首轮适配记录

配方提交 `874d465`，触发 [Actions 43412226757](https://github.com/Sakura286/rocm-specs/actions/runs/43412226757) 成功。OBS `_service` 已接入 `rocm10`；初次 service 创建取得旧配方的构建不计入验收。源码归档 SHA-256 为 `db317aadb90366b61af0fd93b0ccf3cefe70a18e4e37c23744d968ea6f900654`。两架构查询到 snapshot `24.0.0~git20261109.b1de84e-11.1.or`，实际 buildinfo 待构建完成核对。

保留 signed-char 补丁；删除上游已包含的两个 device-libs 补丁。COMGR 系统适配重写为显式 unordered_set 头文件、系统 libc++ 头文件入口及暂时移除 AMD 私有 postopt 选项。最后一项的设备库链接语义仍须修复和验证，不能因编译成功视为完成。hipcc 新版路径初始化已改为必须精确命中一次的替换；保留用户 HIP_CLANG_PATH 覆盖。所有 device-libs 和 COMGR CTest 已启用。

首轮 x86_64 在 CMake 配置阶段失败：ClangTargets 引用的 `libMLIRCIRAnalysis.a` 未安装。当前 snapshot 的 ClangIR 导出还引用 MLIR targets，配方增加 `mlir24-devel`（带静态库依赖）。同时将 device-libs 测试的 amdgcn 链接改为构建目录内的相对路径，避免指向未安装的宿主路径。首轮 OBS revision `2` / srcmd5 `587ceb272d44274e33200e83194ccc01` / `.obsinfo` 已核对为 `874d465db12b3b506574988e4d43728ce04bb918`；buildinfo 确认为本项目 rocm-cmake `10.1.0-3.1.nor` 和 LLVM snapshot `24.0.0~git20261109.b1de84e-11.1.or`。日志 `logs/build-x86_64-first-latest.log`。

第二轮 OBS revision `3` / srcmd5 `9bd82baaebc092f566090f7b91031a94` 已越过配置，device-libs 编译完成；COMGR 元数据代码因 LLVM 24 删除 `getArchAttrAMDGCN` 和旧特性掩码而失败。修复提交 `9532c51` 改为 feature bitset，并使用 XNACK/SRAMECC 的可切换模式位。实际 x86_64 snapshot 库的 gfx900、gfx90a、gfx1100、gfx1250 查询检查通过（`logs/target-features.log`）；不等同于 COMGR 产物验收。当前继续第三轮构建。riscv64 独立目录 `/home/openruyi/tmp/rocm10-rocm-llvm/` 已解包 LLVM 24 运行依赖，Clang 启动通过。

第三轮 revision `4` / srcmd5 `b83adc892abdfdc7005b525f0403bd64` 的 x86_64 编译进一步暴露已删除的 Clang `OffloadUnbundlingJobClass`。该枚举仅作为 COMGR 缓存键类型，分配独立于 driver／SPIR-V 的类型 ID 进行修复。测试检查还发现 CTest 不覆盖已有的 unit／lit 套件；保留源码归档内的 Python lit runner（不编译私有 LLVM），并在 `%check` 显式运行两套测试。日志 `logs/build-x86_64-third-progress.log`。
