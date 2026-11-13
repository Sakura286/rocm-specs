# ROCm 10 实验分支

本文件适用于 `Sakura286/rocm-specs` 的 `rocm10` 分支。在 openRuyi 工作区中，本分支使用独立副本 `rocm-specs-rocm10/`；工作区公共约定仍适用。

- 实验目标：使用 openruyi 的 `llvm-snapshot`（LLVM 24）构建 ROCm 10.1.0。每个组件的源码标签或固定提交须核实；现有配方版本不代表目标已实现。
- 兼容性修复优先回移可追溯的 LLVM／ROCm 上游提交，记录来源 URL、完整 SHA、前置依赖及回移时的必要调整。先核查上游方案，再考虑本地适配；分别记录 C++ API／ABI 变化和 AMD 专有功能差异，不以测试通过代替补丁来源及行为语义审查。
- 持续计划与上下文恢复入口：[ROCm 10.1.0 移植计划](docs/rocm-10.1.0-port-plan.md)。按 `rocm-cmake` → `rocm-llvm` 推进；基础包通过 x86_64 快速验证后可推进下游快速验证，同时跟进 riscv64。两包均已完成 riscv64 最终验收。当前继续升级全部原有 33 个 ROCm 源码包及新版本必需的依赖，按依赖顺序推进并维护全栈进度表；不在基础包或某一批次完成时停止。
- Git 分支：`rocm10`；唯一对应的 OBS 项目：`home:Sakura286:ROCm10`；API：`https://pickaxe.oerv.ac.cn`。
- 操作前核对当前分支、remote 和 workflow 目标。`main` 对应 `home:Sakura286:ROCm`，在独立主线副本中工作。跨分支引入提交时保留本分支的 workflow 及项目映射。
- 配方的权威来源为本分支的 `SPECS/<包名>/`。OBS 各包 `_service` 从 `https://github.com/Sakura286/rocm-specs.git` 拉取 `revision=rocm10`，提取对应包目录；不把配方复制到 OBS 工作目录上传。
- `amd64_build/x86_64` 用于快速验证，`riscv64_build/riscv64` 的构建和实际产物功能验证用于最终验收；需要目标机时使用 `ssh sh-plct-sg2044`。两个状态分别记录。LLVM snapshot 会滚动更新，按架构记录实际使用的完整版本与 ROCm 源码提交。
- 在 openRuyi 工作区执行时，先读 `../skills/rpm-obs-upgrade/SKILL.md` 及其 `references/projects.md` 中 `rocm-specs / rocm10` 条目。临时文件、缓存、日志和构建产物统一放在工作区 `tmp/rocm10-<任务名>/`。
