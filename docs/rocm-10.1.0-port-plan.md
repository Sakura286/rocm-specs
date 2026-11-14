# ROCm 10.1.0 与系统 LLVM 24 移植计划

本任务在 openRuyi 上使用系统 `llvm-snapshot`（LLVM 24）移植 ROCm 10.1.0。按用户于 2026-11-13 确认的顺序，以 `rocm-cmake` → `rocm-llvm` 推进。x86_64 用于快速验证和推进依赖链；最终验收以 riscv64 为准。两项基础包均通过 riscv64 最终验收后，才开始其余组件。本文件是本任务的持续计划与上下文恢复入口，适用范围仅为 `rocm10` 实验分支。

## 用户最新方向（2026-11-13）

优先使用可追溯的 LLVM／ROCm 上游原始提交及必要前置提交进行 backport，弥补 ROCm 所用 LLVM 24 与 openRuyi snapshot 的接口差异；不要优先自造兼容补丁。当前本地 API 适配、postopt 双阶段实现及测试变更均转为待审查的实验对照，不能仅因测试通过就作为最终交付。下一步先比较两端 LLVM 基线、定位上游提交，区分 C++ API／ABI 变化和 AMD 专有功能；能回移原始提交的应替换为带来源的 backport。无法找到上游方案的项应明确记录证据和剩余差异。

审查结果：postopt 是当前系统 LLVM 已支持的上游功能，不需补丁；恢复原始调用。九项上游回移替换自写 API 和测试适配，剩余本地补丁限于发行版构建路径、测试环境及增加回归覆盖。上游完整 lgamma_r 检查已恢复；本地 x86_64 device-libs 33/33、LLVM 原始 postopt pipeline 4/4 通过，正式双架构 RPM 已完成重验，见当前检查点。后文各轮构建记录保留为历史，其中“AMD 私有 postopt 缺失”的判断已被本次审查纠正。

## 当前检查点

基础包阶段已完成：`rocm-cmake` revision 3 与 `rocm-llvm` revision 13 均已在 x86_64 / riscv64 构建、发布并验证实际 RPM。用户明确要求继续升级仓库中全部 ROCm 软件；当前范围为原有 33 个源码包，加上新依赖 rocm-stinkytofu 与 LLVM 24 支持包 rocm-clang，共 35 个；持续清单见[全栈进度](rocm-10.1.0-stack-status.md)。不要在基础包完成或单批提交后停止。

`rocm-llvm` 配方 `a09779dd2417790e05fdcf152b5c3a05791eb939`，OBS revision `13` / srcmd5 `f6f951edbfadbccc2e57624d1fd9904d`，实际 RPM `10.1.0-13.1.nor`。两个架构均通过 device-libs CTest 33/33、COMGR CTest 39/39、unit 310/310、lit 177 pass / 27 unsupported / 1 xfail。实际 RPM 的 21 项检查（含 COMGR、嵌入 libc++、缓存、hipcc gfx1100 编译和无未定义符号检查）与 CMake 下游导入／运行、LLVM 24 宏检查均通过。riscv64 在 `sh-plct-sg2044` 原生执行，RPM 校验值与下载产物一致。

证据：工作区 `tmp/rocm10-rocm-llvm/upstream-review/build-final-{x86_64,riscv64}.log`、`artifact-final-x86_64.log`、`cmake-final-x86_64.log`、`riscv64-validation/`；总审计 `tmp/rocm10-rocm-llvm/audit.json`。旧 revision 11 和 custom-patch native-build 均为历史实验，不要恢复其下载／构建流程。

当前全栈检查点（2026-11-14 01:30 UTC）：35/35 已完成 x86_64 构建和对应快速功能验证，27/35 已完成 riscv64 构建与实际 RPM 无 GPU 验收。正式 rocm-clang 13.1、rocFFT 与 hipFFT 的原生编译/链接/实际消费者验证均通过；rocFFT 原先的 RDC 浮点 ABI 错误由 LLVM PR 168164 回移修复，新实际 ELF 为 double-float ABI。MIOpen 9.1 x86_64 的 CMake/tensor 描述符 API 也通过。剩余原生包为 rocSPARSE、rocSOLVER、hipBLAS、hipSPARSE、hipSOLVER、hipBLASLt、hipSPARSELt、MIOpen。rocSPARSE 正在 sg2044-0317:8 构建（约 320/622），后续按依赖关系继续；实际产物验证脚本持续运行。完整状态、证据及恢复命令见全栈进度的最新检查点，不在全 x86_64 或 FFT 分支完成时结束任务。每个包分别记录源码、补丁审查、配方提交、OBS 修订、双架构构建和实际产物验证；GPU 执行能力单独记录，不把无 GPU 的检查表述为完整 GPU 验证。

## 固定边界和目标环境

2026-11-13 调度修正：继承的 openruyi 配置新增 `Constraint: sandbox exclude="true" kvm`，OBS 将引号保留为属性值，实际错误地只匹配 KVM worker；这些 worker 的 jobs=4，无法满足本包 jobs=32。已在 **home:Sakura286:ROCm10** 项目配置加入如下修正，保留 RVA23/NATIVE 和包内 jobs=32 约束。上游 OBS `BSDispatcher::Constraints::list2struct` 的本地复现确认了引号问题；修正后 `osc checkconstraints` 恢复匹配六台 worker。未修改 openruyi 或主线 ROCm 项目配置。证据位于 `tmp/rocm10-rocm-llvm/upstream-review/constraint-parser-proof.json`、`project-config-after.txt`、`constraints-after-config.log`。后续若继承配置修正，应重新评估是否可以移除本项。

```text
%ifarch riscv64
Constraint: sandbox! exclude=true kvm
%endif
```

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

主线副本 `rocm-specs/`、`main` 分支和 `home:Sakura286:ROCm` 继续其独立任务。本任务不向主线推送，不迁移其他 OBS 项目的非 ROCm 包，不将主线 OBS 项目添加为依赖来源。可读取旧实验的诊断和测试脚本作为参考，但复用前核对源码版本及路径。

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

当前下一步：跟踪 OBS revision 11（srcmd5 `2c4acc1c617ce69d8a6b9a3ea1c6c72f`）的 riscv64 调度和构建，取得最新双架构 RPM；在 `ssh sh-plct-sg2044` 的 `/home/openruyi/tmp/rocm10-rocm-llvm/` 运行实际 RPM 检查及 `tests/validate-artifacts.py`、`tests/cmake/` 下游测试。x86_64 已通过实际产物功能验证，本轮只有调度约束变化，但仍复核最新产物。缓存测试需使用脚本直接传入的环境变量，隔离环境内不依赖 env 命令。所有临时内容和日志保留于工作区 `tmp/rocm10-rocm-llvm/`；未启动其余 ROCm 包。

## rocm-cmake 最终验收记录

配方提交 `eb9267d`，OBS revision `3`，展开 srcmd5 `e34e934fba9b87f10617c31ac9d8c882`，RPM `10.1.0-3.1.nor`。两个架构均构建并发布成功，各执行 32 项 CTest，通过；4 项排除及原因记录在 SPEC 和 `tmp/rocm10-rocm-cmake/audit.json`。

x86_64 与 `sh-plct-sg2044` 的 riscv64 实际 RPM 均通过模块发现、共享库编译、lib64 安装、CMake 导出与下游导入，以及下游程序运行验证。远端目录 `/home/openruyi/tmp/rocm10-rocm-cmake/`；本地日志、校验和与审计摘要位于 `tmp/rocm10-rocm-cmake/`。验证使用独立解包目录，未替换目标机现有系统包；不是系统升级事务测试。

## rocm-llvm 首轮适配记录

配方提交 `874d465`，触发 [Actions 43412226757](https://github.com/Sakura286/rocm-specs/actions/runs/43412226757) 成功。OBS `_service` 已接入 `rocm10`；初次 service 创建取得旧配方的构建不计入验收。源码归档 SHA-256 为 `db317aadb90366b61af0fd93b0ccf3cefe70a18e4e37c23744d968ea6f900654`。两架构查询到 snapshot `24.0.0~git20261109.b1de84e-11.1.or`，实际 buildinfo 待构建完成核对。

保留 signed-char 补丁；删除上游已包含的两个 device-libs 补丁。COMGR 系统适配重写为显式 unordered_set 头文件、系统 libc++ 头文件入口及暂时移除 AMD 私有 postopt 选项。最后一项的设备库链接语义仍须修复和验证，不能因编译成功视为完成。hipcc 新版路径初始化已改为必须精确命中一次的替换；保留用户 HIP_CLANG_PATH 覆盖。所有 device-libs 和 COMGR CTest 已启用。

首轮 x86_64 在 CMake 配置阶段失败：ClangTargets 引用的 `libMLIRCIRAnalysis.a` 未安装。当前 snapshot 的 ClangIR 导出还引用 MLIR targets，配方增加 `mlir24-devel`（带静态库依赖）。同时将 device-libs 测试的 amdgcn 链接改为构建目录内的相对路径，避免指向未安装的宿主路径。首轮 OBS revision `2` / srcmd5 `587ceb272d44274e33200e83194ccc01` / `.obsinfo` 已核对为 `874d465db12b3b506574988e4d43728ce04bb918`；buildinfo 确认为本项目 rocm-cmake `10.1.0-3.1.nor` 和 LLVM snapshot `24.0.0~git20261109.b1de84e-11.1.or`。日志 `logs/build-x86_64-first-latest.log`。

第二轮 OBS revision `3` / srcmd5 `9bd82baaebc092f566090f7b91031a94` 已越过配置，device-libs 编译完成；COMGR 元数据代码因 LLVM 24 删除 `getArchAttrAMDGCN` 和旧特性掩码而失败。修复提交 `9532c51` 改为 feature bitset，并使用 XNACK/SRAMECC 的可切换模式位。实际 x86_64 snapshot 库的 gfx900、gfx90a、gfx1100、gfx1250 查询检查通过（`logs/target-features.log`）；不等同于 COMGR 产物验收。当前继续第三轮构建。riscv64 独立目录 `/home/openruyi/tmp/rocm10-rocm-llvm/` 已解包 LLVM 24 运行依赖，Clang 启动通过。

第三轮 revision `4` / srcmd5 `b83adc892abdfdc7005b525f0403bd64` 的 x86_64 编译进一步暴露已删除的 Clang `OffloadUnbundlingJobClass`。该枚举仅作为 COMGR 缓存键类型，分配独立于 driver／SPIR-V 的类型 ID 进行修复。测试检查还发现 CTest 不覆盖已有的 unit／lit 套件；保留源码归档内的 Python lit runner（不编译私有 LLVM），并在 `%check` 显式运行两套测试。日志 `logs/build-x86_64-third-progress.log`。

第四轮 revision `5` / srcmd5 `2150f077f10922e4eef84b486d3bbde3`：x86_64 成功链接 COMGR 主库，后续 `DemangleSymbolNameTest` 缺少 llvm_gtest 依赖的 LLVM Support 符号。补丁按 COMGR 相同的 LLVM 链接模式补齐依赖；同时修正 lit 工具目录错误地跟随 Python runner 路径的问题。日志 `logs/build-x86_64-fourth-latest.log`。

riscv64 已用解包的 bubblewrap 建立隔离挂载环境，默认 `/usr/lib64/llvm24/bin/clang` 启动通过，脚本 `tests/prepare-isolation.py`，日志 `logs/remote-bwrap-runtime-retry.log`。postopt 双阶段方案已在独立小型程序中验证可行；该诊断使用旧主线设备库，仅用于验证方案，不计入 ROCm10 验收，待真实新产物回归。

第五轮 revision `6` / srcmd5 `e6576e135c2a761de56c6ea7184ec49f`：编译和安装成功后，device-libs 原始 33 项 CTest 失败 17 项，COMGR CTest 32 项通过 30 项（两个原始 OpenCL 链接测试失败），unit 全部通过，lit 205 项中失败 8 项。完整日志 `logs/build-x86_64-fifth-final.log`。当前准备第六轮：

- 在 COMGR 内截获 AMD postopt 标记，先优化、再执行禁止优化的 IR 链接；保留驱动选择的设备库及 Clang 属性传播，不修改 API 调用方或 OpenCL 功能测试。补丁 `2005`。
- 本地以系统 LLVM 24 动态库构建新 device-libs，复现全部 17 项失败。按实际等价 lowering 修正寄存器检查边界、half rsqrt、finite 比较、NaN-preserving min、IR 名称及 MMRA 命名，补丁 `2006`。修正后 33 项检查通过，日志 `logs/local-device-tests-final.log`。这是本地诊断构建，不替代 OBS／riscv64 验收。
- 明确测试限制：原有完整 `lgamma_r` 常量折叠的两项测试保留但排除，系统 LLVM 不会折叠某些 target reciprocal intrinsic；同时新增两架构的严格特殊值、符号及已支持常量结果检查。无穷／NaN 的 IR 格式也已变化。不能声称原始完整优化测试通过，不能据此宣称 GPU 数值执行已验证。
- lit 适配 canonical AMDGPU subarch triple 和 gfx1250 XNACK 能力，libstdc++ 头文件共存夹具使用 constexpr array，以免依赖 GNU 运行时访问器的 device 注解。补丁 `2007`。所有补丁在干净源码子集应用成功，postopt 补丁整理前后源码完全一致。

本地调试入口：`tmp/rocm10-rocm-llvm/run-build.sh`（允许系统 C++ 头文件，用于编译诊断工具）与 `run-runtime.sh`（隐藏宿主 C++ 头文件，检查嵌入 libc++）。本地 device-libs 源码／构建位于 `sources/llvm-project-therock-10.1/amd/device-libs/`、`build/local-device-libs/`。`tests/pristine-device-tests/` 保存未修改测试用于差异审查。

第六轮已经推送：包提交 `e6ca86f`，推送 HEAD `3548400`，OBS revision `7` / srcmd5 `301b1ad79a8de21071aec8eef48d887d`。上一轮 unit 共 310 项全部通过；lit 为 169 passed、27 unsupported、1 expected failure、8 failed。原始日志均保留。riscv64 原生 LLVM 特性查询也已通过（`logs/target-features-riscv64.log`），仍不计作 COMGR RPM 验收。

第六轮结果：x86_64 device-libs 33/33、COMGR CTest 32/32（包括两个未修改的 OpenCL 测试）、unit 310/310 通过；lit 205 项中 173 passed、27 unsupported、1 expected failure、4 failed。日志 `logs/build-x86_64-sixth-final.log`。三项解包测试失败是因为 LLVM 24 将 CPU 编入 canonical triple，不再保留冗余 target-cpu 属性；改为精确检查 gfx900/gfx1030 的 triple。GNU 头文件共存测试的 constexpr array 仍调用 host-only bounds assertion，改用静态索引 `std::get`，本地相同 Clang 24 探针通过（`logs/libstdcxx-get-probe.log`）。未关闭任何 lit 测试。

riscv64 第六轮在 obsworker-pico-itx-box02-0 的构建根初始化阶段失败：`build-preinstall/dev/null` 挂载无法清理、目录已存在，未执行 SPEC。日志 `logs/build-riscv64-sixth-final.log`。须观察后续修订是否分配到可用 worker；不能把基础设施失败写成编译失败或验收完成。

第七轮已推送：`57532ab` / HEAD `d3ad129`，Actions 43418484519 成功；OBS revision `8` / srcmd5 `80a3d342891bf24c995b6666e2c86686`，`.obsinfo` 已核对。两架构 buildinfo 保存在 `logs/buildinfo-seventh-<arch>.xml`。riscv64 调度到 pico-itx-box08:1；评估 jobs=32 约束时匹配 6 个 worker，暂未添加约束，先观察新 worker 的实际情况。

第七轮 x86_64 构建／发布成功（`10.1.0-8.1.nor`）：device-libs 33/33、COMGR CTest 32/32、unit 310/310、lit 177 passed / 27 unsupported / 1 xfail。日志 `logs/build-x86_64-seventh-test.log`。实际 RPM 的 hipcc 编译 gfx1100、拆包、ELF 检查及无未解析符号验证通过，COMGR API 3.5 / 61 ISAs 正常；尚不能验收，发现以下问题并准备第八轮：

- 上游 CTest 全部禁用缓存，实际默认缓存会先运行预处理 job，postopt 适配错误拒绝该 job。改为仅在 EmitBC 阶段执行第二阶段链接；新增 OpenCL、VFS、嵌入 libc++ 的缓存开启及重复调用回归。诊断 `logs/artifact-opencl-diagnostic.log`。
- 原有 HIP libc++ CTest 被上游注释；现在启用并强制嵌入头文件，避免误用宿主 GNU runtime。实际 RPM 在缓存关闭／强制嵌入模式通过（`logs/artifact-libcxx-forced-nocache.log`）。本地隔离宿主的多架构 GNU 头文件探测会误判，这是使用 force 模式的原因；并非声称自动探测已在任意宿主通过。
- AMDDeviceLibs CMake 导出将两个绝对路径重复拼接。删除旧模板前缀覆盖，按上游要求将安装目录传为相对 `/usr` 的路径；对应调整构建内 bitcode 目录软链接。诊断 `logs/artifact-cmake-configure-lib64.log`。本机 pip CMake 默认不搜索 lib64，测试需显式 `CMAKE_PREFIX_PATH=/usr;/usr/lib64/cmake`；目标机 openRuyi CMake 另行验证。

第七轮 riscv64 仍在 pico-itx-box08:1 执行；在线日志返回 IncompleteRead，状态尚不能计作完成。后续若新源码触发重建，最终只验收最新配方产物。

第八轮已推送：包提交 `8f7ba19` / HEAD `f645733`，Actions 43419797505 成功；OBS revision `9` / srcmd5 `614409c9e4b5ca3696a5249eabb9df6b`。相对安装布局生成的配置已在本地 CMake 下游证明能找到四个实际 bitcode 文件（`logs/cmake-relative-config-proof.log`），最终仍需重测本轮 RPM。

第八轮 x86_64 已通过 device-libs 33/33、COMGR CTest 39/39（新增缓存／嵌入头文件回归），等待完整打包结果。riscv64 又在 pico-itx-box02:0 的同一 preinstall 挂载清理步骤失败，日志 `logs/build-riscv64-eighth-final.log`。决定添加包级、仅 riscv64 的 jobs>=32 约束，匹配 6 个 worker（`logs/constraints-final-riscv64.log`），避免反复进入故障小型 worker，同时改善这类 LLVM 开发依赖较重的构建调度。约束放入 Git 配方，由同一 service 提取；pre-commit 禁止约束文件的旧规则仅对此包设置例外，不放开其他包。

第九轮仅增加调度约束：包提交 `0a274eb` / HEAD `bf438f1`，OBS revision `10` / srcmd5 `7e2a63b4181e0f6c3cb372f3dde1229d`。实际核查发现 `_service:obs_scm:_constraints` 未被此实例调度器识别，远端 checkconstraints 仍包含 pico worker，不能声称约束生效。按 [OBS 官方构建约束文档](https://openbuildservice.org/help/manuals/obs-user-guide/cha-obs-build-constraints) 改为 `%ifarch riscv64` 内的 `#!BuildConstraint: hardware:jobs 32`；删除不起作用的 XML 并恢复原 pre-commit 规则。源码与构建触发方式保持不变。

第八轮 x86_64 实际 RPM `10.1.0-9.1.nor` 功能已全部通过：原始 OpenCL/VFS/HIP 嵌入 libc++ 测试、缓存开启及重复调用、COMGR API 3.5/61 ISAs、hipcc gfx1100 链接后无未解析符号、CMake 导出及下游运行。日志 `logs/artifact-validation-run-x86_64-rev9-fixed-harness.log`、`logs/artifact-cmake-*-rev9.log`。测试脚本曾尝试在隔离环境运行不可用的 env 命令，已改为直接传 subprocess 环境；该失败不是 RPM 缺陷。当前仅等待最终调度修订的双架构构建与 riscv64 功能验收。

第十轮 OBS revision `11` 已确认生效：调度状态为 `scheduled` / `waiting for 6 compliant workers`，不再进入 pico 小型 worker。`osc checkconstraints` 不带 XML 的远端查询在本实例仍列出未合并 recipe directive 的名单，因此以调度器的匹配数、实际 worker 及源码修订联合验证，不能只依赖该命令输出。源码证明及 buildinfo 保存为 `logs/source-final.obsinfo`、`logs/buildinfo-final-<arch>.xml`。

x86_64 最新实际产物 `10.1.0-11.1.nor` 已全部复验通过，`_statistics` 的 srcmd5 与 revision 11 一致。证据：`logs/artifacts-x86_64.json`、`logs/artifact-validation-final-x86_64.log`、`logs/cmake-validation-final-x86_64.log`；宏展开指向 LLVM 24。当前 riscv64 排队监视脚本 `tests/wait-riscv-build.py`，进度保存在 `logs/result-monitor.jsonl`，进入构建后脚本退出，届时跟踪新日志和实际 worker。

2026-11-13 12:19 UTC 监视到 riscv64 调度到 sg2044-0317:9；worker 日志实际开始时间 12:21:40 UTC，srcmd5 正确，内存上限约 84 GiB，已越过此前故障 worker 的初始化步骤并安装 LLVM 24 静态依赖。日志 `logs/build-riscv64-final-start.log`。排队期间还在目标机准备了备用原生诊断构建，源码及脚本在 `native-sources/`、`native-recipe/`、`tests/*native*`；大型静态包下载中，尚未编译，不计作任何验收。

### 2026-11-14 验收范围与新增编译器支持包

用户已确认目前无带 AMD GPU 的 riscv64 机器，先完成全部包的无 GPU 验证：riscv64 构建、实际 RPM 的 CPU/API 与离线编译。GPU 数值运算保留为未验证项，不再等待硬件答复。全栈状态及 LLVM PR 216938/233925/168164、独立 rocm-clang 支持包的最终产物验证见全栈进度文档最新检查点。三项 PR 均未合并，必须保留来源、完整提交及实验性状态；使用系统 LLVM 24 相同源码基线，不扩展到主线工程。当前两项基础包与支持包的双架构验收已经完成，继续其余全部组件。
