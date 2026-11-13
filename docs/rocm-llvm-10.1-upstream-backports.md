# ROCm 10.1 / LLVM 24 上游回移审查

按用户 2026-11-13 的要求，兼容修复优先使用可追溯的上游提交。源码固定为 ROCm `therock-10.1`（`d6f6cb691863e9258034ab48c1dfce21689d5606`），系统 LLVM 为 openRuyi `24.0.0~git20261109.b1de84e-11.1.or`（`b1de84ea1aa8c686639f4c0144e045e4a2a12510`）。两者都是 LLVM 24，但不能据此推断 C++ API 或 ABI 一致。

## 纠正 postopt 判断

先前把 `-mlink-builtin-bitcode-postopt` 误判为当前系统 LLVM 缺失的 AMD 私有功能，因而添加了 COMGR 双阶段编译补丁 `2005`。该补丁已删除，恢复 COMGR 原始调用路径。

该选项和优化后链接流程已在 LLVM 上游：

- [11a6799740f824282650aa9ec249b55dcf1a8aae](https://github.com/llvm/llvm-project/commit/11a6799740f824282650aa9ec249b55dcf1a8aae)：2024 年引入当前选项及仅在优化后链接的行为。
- [d9cf5980b7788a8840d69c6e4abb9092a35997bc](https://github.com/llvm/llvm-project/commit/d9cf5980b7788a8840d69c6e4abb9092a35997bc)：优化后链接新增全局对象的 GUID 修复。

当前 snapshot 的 `CodeGenOptions.def`、生成的 `Options.inc`、`CodeGenAction.cpp` 和 `BackendUtil.cpp` 均含该实现，实际 `clang -cc1 --help` 也列出该选项。用 openRuyi x86_64 和 riscv64 Clang 运行第一个提交附带的四种 pipeline 回归（默认、开启、关闭、先开启再关闭），两种架构均全部通过；只有开启时出现 `LinkInModulesPass`。这些已有功能无需再次 backport，也无需替代实现。COMGR 新 RPM 的端到端测试仍须单独通过。

## 回移清单

下表的 AMD 组件修复来自 **ROCm/llvm-project**，不是把 ROCm fork 的提交误称为 llvm/llvm-project 主线提交。涉及的 LLVM API 变化已在系统 snapshot 中，修复方向是使 10.1 COMGR 使用这些接口；本轮不修改系统 LLVM 配方。

| 补丁 | 上游提交 | 回移方式及依赖 |
| --- | --- | --- |
| `1001` AMDGPU feature bitset | [f327d0b1b4bc61ef9042747ffa77e70b92254c11](https://github.com/ROCm/llvm-project/commit/f327d0b1b4bc61ef9042747ffa77e70b92254c11) | 原始 patch 不变；替代本地 `getArchAttrAMDGCN` 适配 |
| `1002` SRAM ECC 可切换模式 | [6b5ccd0e88b0eb23ba3103e730b8efd26ac9e8f8](https://github.com/ROCm/llvm-project/commit/6b5ccd0e88b0eb23ba3103e730b8efd26ac9e8f8) | 依赖 `1001`；保留源代码修复和上游回归 helper，仅重定位到 10.1 的 ISA 枚举测试上下文，不引入后续 ISA 表重构 |
| `1003` COMGR 自有缓存标签 | [5778526e3e788f8fa60bd8a8b37b2b737a1413ee](https://github.com/ROCm/llvm-project/commit/5778526e3e788f8fa60bd8a8b37b2b737a1413ee) | 原始 patch 不变；替代本地 `JobClassLast + 2` 单点修改，包含 SPIR-V 标签共享定义 |
| `1004` device-libs 过期检查 | [25affef0d99027aee4dcdf573e6b2b9d174b04eb](https://github.com/ROCm/llvm-project/commit/25affef0d99027aee4dcdf573e6b2b9d174b04eb) | 原始 patch 不变；恢复上游完整 lgamma_r 测试，不再使用本地排除和替代测试 |
| `1005` COMGR subarch triple 检查 | [3acdcc1e8f1feb831aa7e0238d8c850d2266799c](https://github.com/ROCm/llvm-project/commit/3acdcc1e8f1feb831aa7e0238d8c850d2266799c) | 原始 patch 不变 |
| `1006` unbundle 架构检查 | [2bc76dfeecf71b94d0f83487dadc42e75a2d1362](https://github.com/ROCm/llvm-project/commit/2bc76dfeecf71b94d0f83487dadc42e75a2d1362) | 原始 patch 不变；依赖 `1005` |
| `1007` gfx12.5 XNACK 测试 | [fad9cb3d631c287314e2de2f190274fb8c866a01](https://github.com/ROCm/llvm-project/commit/fad9cb3d631c287314e2de2f190274fb8c866a01) | 省略删除临时 `FixFromJacob` 限制的 hunk（10.1 没有此限制）；保留全部新增 XNACK 测试 |
| `1008` GTest 的 LLVM Support 链接 | [feb6bdbb08b2c55077377cd3e0a36bbcd04e49a0](https://github.com/ROCm/llvm-project/commit/feb6bdbb08b2c55077377cd3e0a36bbcd04e49a0) | 仅摘取独立的 `test-unit/CMakeLists.txt` 修复及说明；不引入与本配方动态链接无关的静态链接框架重构 |
| `1009` generic gfx12.5 的最终特性预期 | [1c1a11bcabbfda3f52d8541f5536bf69c95941e4](https://github.com/ROCm/llvm-project/commit/1c1a11bcabbfda3f52d8541f5536bf69c95941e4) | 原始 patch 不变；依赖 `1007`，跟进 generic 型号不再暴露可切换 XNACK 的后续变化 |

没有额外回移 [a23e3d7ec1100fd41d5d4c04816041f2ff85dcd9](https://github.com/ROCm/llvm-project/commit/a23e3d7ec1100fd41d5d4c04816041f2ff85dcd9)：10.1 原始源码已经使用 `llvm::StringSet<>`。此前本地添加的 `<unordered_set>` 因此直接删除。补丁检查使用 `--forward --fuzz=0`，避免 patch 自动反向应用已包含的提交。

没有回移 `1fb7031b6de6dfdbfca9bd2822e7fd51d2164a21` 的 XNACK 删除方案：后续 LLVM 已恢复 gfx12.5 的 XNACK on/off 支持，当前 snapshot 应按 `1007` 的最终预期检查，不能只根据较早的提交说明选择修复。

## 保留的发行版适配

以下不伪装为上游 ABI 修复。已检查对应上游文件历史；后续有合适上游方案时继续替换。

- `0001`：原有 Debian 来源的 signed-char 构建修复，来源见 SPEC。
- `2000`：指定已安装的 libc++ 头文件目录，支持发行版独立构建。
- `2003`：源码 Python lit 与已安装 LLVM 工具分开定位。
- `2007`：GNU 头文件共存夹具改用 constexpr `std::array` / `std::get`，避免发行版启用的 host-only bounds assertion；不修改库实现。
- `2008`：启用嵌入 libc++ 测试，并增加 OpenCL、VFS、HIP 的缓存开启及重复调用回归；测试上游 postopt 原始路径。
- `2009`：atomic fence 的 IR 测试显式传入 `-fno-discard-value-names`，保留上游要求的 `entry:` 标签。发行版 Clang 默认丢弃名称；此项只统一测试输入参数，不改上游 FileCheck 或编译器实现。

## 验证与证据

原始上游 patch、API 返回、源码对照及日志位于工作区 `tmp/rocm10-rocm-llvm/upstream-review/`。六个完整回移文件与上游下载内容逐字节一致；三个局部或上下文回移明确保留原作者、完整 SHA 和调整说明。整组补丁已在干净归档解包源码上按 SPEC 顺序正向、零 fuzz 应用通过。原始 patch 的空白上下文行保留 diff 格式，普通 `git diff --check` 会将其报告为空白；非 patch 文件检查及 pre-commit 通过。

本地 x86_64 使用系统 LLVM 24 重新构建 device-libs 并通过全部 33 项 CTest，包含恢复的两个完整 `lgamma_r` 测试（`device-ctest-final.log`）。这是本地诊断构建，不替代 OBS 或 riscv64 验证。诊断链接器使用 `--allow-shlib-undefined` 跨过宿主旧 glibc 的符号检查，运行时加载隔离目录内的 openRuyi 库；正式 SPEC 不使用该参数。早期失败日志（依赖未构建、IR 名称丢弃、CMake 参数转发）均保留。

旧 OBS revision 11 的 x86_64 结果只作为实验对照，不能替代删除 `2005` 后的新构建验证。新配方必须重新完成 x86_64 快速验证，再以 riscv64 构建、实际 RPM 和功能测试作最终验收。当前进度以[持续计划](rocm-10.1.0-port-plan.md)为准。

首轮上游回移（`a824c7c`，OBS revision 12）在 x86_64 通过 device-libs 33/33、COMGR CTest 39/39 和 unit 310/310；lit 仅 generic gfx12.5 的新增 XNACK 预期失败。补齐上游后续提交 `1009`；96 条 ISA parsing 命令在旧 RPM 上的局部验证通过，新 RPM 的完整测试仍以接下来的 OBS 构建为准。

补齐后的 `a09779d` / OBS revision 13 在 x86_64 全部通过：device-libs 33/33、COMGR CTest 39/39、unit 310/310、lit 177 pass / 27 unsupported / 1 xfail；日志 `upstream-review/x86-rev13-current-2.log`。当前仍在签名，实际 RPM 验证与 riscv64 最终验收尚未完成。另用当前 x86_64 Clang 原始 postopt 路径和现有 10.1 设备库完成 `cbrt` / `printf` kernel 编译、链接，代码对象无未解析符号（`native-device-link-x86_64/`）；此诊断不代替新 RPM 验收，也不代表 GPU 执行验证。
