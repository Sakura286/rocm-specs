# ROCm 10 实验分支

本文件适用于 `Sakura286/rocm-specs` 的 `rocm10` 分支。在 openRuyi 工作区中，本分支使用独立副本 `rocm-specs-rocm10/`；工作区公共约定仍适用。

- 实验目标：使用 openruyi 的 `llvm-snapshot`（LLVM 24）构建 ROCm 10。每个组件的源码标签或固定提交须核实；现有配方版本不代表目标已实现。
- Git 分支：`rocm10`；唯一对应的 OBS 项目：`home:Sakura286:ROCm10`；API：`https://pickaxe.oerv.ac.cn`。
- 操作前核对当前分支、remote 和 workflow 目标。`main` 对应 `home:Sakura286:ROCm`，在独立主线副本中工作。跨分支引入提交时保留本分支的 workflow 及项目映射。
- 配方的权威来源为本分支的 `SPECS/<包名>/`。OBS 各包 `_service` 从 `https://github.com/Sakura286/rocm-specs.git` 拉取 `revision=rocm10`，提取对应包目录；不把配方复制到 OBS 工作目录上传。
- 默认验证 `amd64_build/x86_64`；`riscv64_build/riscv64` 结果单独报告。LLVM snapshot 会滚动更新，记录实际使用的完整版本与 ROCm 源码提交。
- 在 openRuyi 工作区执行时，先读 `../skills/rpm-obs-upgrade/SKILL.md` 及其 `references/projects.md` 中 `rocm-specs / rocm10` 条目。临时文件、缓存、日志和构建产物统一放在工作区 `tmp/rocm10-<任务名>/`。
