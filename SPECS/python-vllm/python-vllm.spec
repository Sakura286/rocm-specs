# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global flavor @BUILD_FLAVOR@%{nil}

%global srcname vllm

# The "cpu" multibuild flavor builds the CPU backend; the default flavor builds
# the ROCm/HIP backend.  Local builds can also force CPU with --without rocm.
%if "%{flavor}" == "cpu"
%bcond rocm 0
%else
%bcond rocm 1
%endif

%if %{with rocm}
%global toolchain clang

# TODO: gfx1100 for test build
%global rocm_gpu_arch gfx1100
%endif

%if %{with rocm}
Name:           python-%{srcname}-rocm
%else
Name:           python-%{srcname}-cpu
%endif
Version:        0.22.1
Release:        %autorelease
Summary:        A high-throughput and memory-efficient inference and serving engine for LLMs
License:        Apache-2.0
URL:            https://github.com/vllm-project/vllm
#!RemoteAsset:  sha256:4666b4052880d29c4a2c3d5b14cbb37b0457de1ea495dafc07ee128e7f3c4ad8
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
# TODO: add triton-conch deps
# Offline replacement for cmake/external_projects/triton_kernels.cmake, which
# otherwise git-clones the triton repo at configure time (no network on OBS).
Source1:        triton_kernels-stub.cmake
BuildSystem:    pyproject

%if %{with rocm}
# cumem_allocator (LANGUAGE CXX) never gets -DUSE_ROCM on the HIP build, so
# cumem_allocator_compat.h takes the CUDA path and #includes cuda_runtime_api.h.
Patch0:         0001-cumem_allocator-define-USE_ROCM-for-CXX-target.patch
%endif

# Adjust dependencies and build configurations for openRuyi
Patch1:         2002-Adjust-dependencies-for-openRuyi.patch
# Fix spinloop x86intrin header include (x86-guarded, no-op on riscv64)
Patch2:         2004-Fix-spinloop-x86intrin-header.patch

%if %{with rocm}
# Run find_package(hipsparselt) before find_package(Torch) for proper link target
Patch3:         2003-ROCm-hipsparselt-ordering.patch
%else
# Adjust CPU backend for openRuyi's OpenMP path
Patch4:         2001-CPU-backend-OpenMP-path.patch
%endif

BuildOption(install):  %{srcname}

# --- Python build backend (build-system.requires from pyproject.toml) -------
# setup.py imports torch, setuptools_scm and setuptools_rust at module load, so
# these must be present before %%pyproject_buildrequires can run the backend.
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-scm)
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(jinja2)
BuildRequires:  python3dist(torch)
# find_package(Torch) loads Caffe2Config, which find_package(Protobuf)s the
# system protobuf torch was built against; torch's import also wants numpy.
BuildRequires:  pkgconfig(protobuf)
BuildRequires:  python3dist(numpy)
BuildRequires:  cmake
BuildRequires:  ninja

%if %{with rocm}
# --- ROCm toolchain ---------------------------------------------------------
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  libstdc++-devel
BuildRequires:  hipcc
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocm-device-libs
BuildRequires:  roctracer-devel

# --- ROCm libraries ---------------------------------------------------------
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hipcub)
BuildRequires:  cmake(hipfft)
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(hipsparselt)
BuildRequires:  cmake(hipsolver)
BuildRequires:  cmake(miopen)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocrand)
BuildRequires:  cmake(rocfft)
BuildRequires:  cmake(rccl)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocsolver)
BuildRequires:  cmake(rocthrust)
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm_smi)
%else
# --- CPU backend ------------------------------------------------------------
# vLLM's CPU extension compiles with gcc (the x86 path requires gcc >= 12.3) and
# links libnuma for NUMA-aware allocation.  RISC-V uses the RVV path.
BuildRequires:  gcc-c++
BuildRequires:  numactl-devel
# When python-torch is built with ROCm support, it links ROCm libraries even on
# CPU-only builds, so vLLM's CPU flavor needs the ROCm libraries at build time
# (for linking against torch) and at runtime (for loading torch).
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hipcub)
BuildRequires:  cmake(hipfft)
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(hipsparselt)
BuildRequires:  cmake(hipsolver)
BuildRequires:  cmake(miopen)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocrand)
BuildRequires:  cmake(rocfft)
BuildRequires:  cmake(rccl)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocsolver)
BuildRequires:  cmake(rocthrust)
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm_smi)
Requires:       miopen
Requires:       hipblas
Requires:       hipblaslt
Requires:       hipcub
Requires:       hipfft
Requires:       hiprand
Requires:       hipsparse
Requires:       hipsparselt
Requires:       hipsolver
Requires:       rocblas
Requires:       rocrand
Requires:       rocfft
Requires:       rccl
Requires:       rocprim
Requires:       amd-comgr
Requires:       rocm-core
Requires:       hsa-runtime
Requires:       rocsolver
Requires:       rocthrust
Requires:       amdsmi
Requires:       abseil-cpp
%endif

Requires:       python3dist(torch)
# vLLM's "ninja" dependency is the PyPI wheel that bundles a ninja binary for
# pip/venv users; at runtime vLLM/torch only invoke the ninja executable on
# PATH, which the system package provides.  Require that and drop the PyPI wheel
# requirement in %%prep (openRuyi does not package the wheel).
Requires:       ninja
%if %{with rocm}
Requires:       python3dist(triton)
Requires:       amdsmi
%endif

# The unsuffixed names resolve to the ROCm build; the CPU and ROCm packages are
# mutually exclusive (both ship the same /usr/bin/vllm and vllm module).
%if %{with rocm}
Provides:       python-%{srcname} = %{version}-%{release}
Provides:       vllm = %{version}-%{release}
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
Conflicts:      python-%{srcname}-cpu
%else
Conflicts:      python-%{srcname}-rocm
%endif

%description
vLLM is a fast and easy-to-use library for LLM inference and serving, featuring
PagedAttention for efficient management of attention key/value memory,
continuous batching of incoming requests, and an OpenAI-compatible API server.

%prep -a
# Replace the network-fetching triton_kernels external project with the offline
# stub (see Source1).
cp -f %{SOURCE1} cmake/external_projects/triton_kernels.cmake

%generate_buildrequires
# Tarball builds have no git, so setuptools_scm cannot infer the version;
# VLLM_VERSION_OVERRIDE sets SETUPTOOLS_SCM_PRETEND_VERSION and also bypasses
# the "+rocmXYZ" local-version suffix in setup.py:get_vllm_version().
export VLLM_VERSION_OVERRIDE=%{version}
%if %{with rocm}
export VLLM_TARGET_DEVICE=rocm
export ROCM_PATH=%{_prefix}
%else
export VLLM_TARGET_DEVICE=cpu
%endif
# -R: skip vLLM's huge runtime requirement set as build dependencies; only the
# build backend deps are needed to produce the wheel.
%pyproject_buildrequires -R

%build -p
export VLLM_VERSION_OVERRIDE=%{version}
%if %{with rocm}
export VLLM_TARGET_DEVICE=rocm
export PYTORCH_ROCM_ARCH=%{rocm_gpu_arch}
# ROCm lives under %%{_prefix} on openRuyi, not /opt/rocm; make torch's
# ROCM_HOME (and thus setup.py's -DROCM_PATH) resolve there, and build HIP with
# the ROCm clang++ like the rest of the stack.
export ROCM_PATH=%{_prefix}
export ROCM_HOME=%{_prefix}
export PATH=%{rocmllvm_bindir}:%{_bindir}:$PATH
# CMAKE_HIP_ARCHITECTURES must be set explicitly: enable_language(HIP) tries to
# auto-detect a default arch via rocm_agent_enumerator, which finds nothing on a
# GPU-less builder ("Failed to find a default HIP architecture").
#
# --rocm-device-lib-path: the LLVM-21 clang looks for the AMDGPU device bitcode
# in its own resource dir, but rocm-device-libs installs it under
# %{_prefix}/lib/clang/%{rocmllvm_version}/amdgcn/bitcode, so point clang there
# (a single flag — no ';' — to avoid CMake's list-separator splitting).
export CMAKE_ARGS="-DROCM_PATH=%{_prefix} -DCMAKE_HIP_COMPILER=%{rocmllvm_bindir}/clang++ -DCMAKE_HIP_ARCHITECTURES=%{rocm_gpu_arch} -DCMAKE_HIP_FLAGS=--rocm-device-lib-path=%{_prefix}/lib/clang/%{rocmllvm_version}/amdgcn/bitcode"
%else
export VLLM_TARGET_DEVICE=cpu
# torch was built with ROCm support, so its Caffe2Targets.cmake references
# hip::amdhip64 and LoadHIP.cmake requires PYTORCH_ROCM_ARCH.  Set ROCM_PATH
# so cmake can resolve the HIP package, and a dummy PYTORCH_ROCM_ARCH to
# satisfy the guard (no HIP code is actually compiled for the CPU backend).
export ROCM_PATH=%{_prefix}
export PYTORCH_ROCM_ARCH=gfx1100
# RISC-V CPU: cpu_extension.cmake auto-detects the RVV vector length from
# /proc/cpuinfo; override with -DVLLM_RVV_VLEN=128/256, or =0 to force scalar.
# sg2044 has VLEN=128; specify it explicitly to ensure correct configuration.
%ifarch riscv64
export CMAKE_ARGS="-DROCM_PATH=%{_prefix} -DVLLM_RVV_VLEN=128"
%endif
%endif
# Release (not RelWithDebInfo) trims compile time and memory on the big kernels.
export CMAKE_BUILD_TYPE=Release

# Cap parallelism by available memory: the kernel translation units are memory
# hungry and will thrash or OOM otherwise.
mem_gb=$(awk '/MemTotal/ {print int($2/1024/1024)}' /proc/meminfo)
compile_jobs=$(nproc)
mem_jobs=$(( 1 + mem_gb / 3 ))
[ "$mem_jobs" -lt "$compile_jobs" ] && compile_jobs=$mem_jobs
[ "$compile_jobs" -lt 1 ] && compile_jobs=1
export MAX_JOBS=$compile_jobs

%check
# The default pyproject self-import check cannot run here: importing vllm pulls
# its large runtime dependency stack (transformers, fastapi, ...) that is not
# packaged on openRuyi, and needs a GPU runtime.

%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/vllm

%changelog
%autochangelog
