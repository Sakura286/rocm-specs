# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global flavor @BUILD_FLAVOR@%{nil}

%global srcname vllm

%if "%{flavor}" == "rocm"
%bcond rocm 1
%else
%bcond rocm 0
%endif

%if %{with rocm}
%global toolchain clang
%endif

%if %{with rocm}
Name:           python-%{srcname}-rocm
%else
Name:           python-%{srcname}
%endif
Version:        0.25.0
Release:        %autorelease
Summary:        A high-throughput and memory-efficient inference and serving engine for LLMs
License:        Apache-2.0
URL:            https://github.com/vllm-project/vllm
#!RemoteAsset:  sha256:7e04e2b37164de8c4012f27f75af6c4768039b32610865e9b6fb8c49c34a84aa
Source0:        https://files.pythonhosted.org/packages/source/v/%{srcname}/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:ba5834a1fdbb6d1c1b1c065dfd789438e7aa42c03fc52d92c02af85d78d1c75c
Source2:        https://github.com/uxlfoundation/oneDNN/archive/refs/tags/v3.10.tar.gz
BuildSystem:    pyproject

BuildOption(install):  %{srcname}

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
BuildRequires:  libomp
BuildRequires:  pkgconfig(protobuf)
BuildRequires:  python3dist(numpy)
BuildRequires:  cmake
BuildRequires:  ninja
%if %{with rocm}
BuildRequires:  clang
BuildRequires:  clang-tools-extra
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
BuildRequires:  compiler-rt
BuildRequires:  hipcc
BuildRequires:  libstdc++-devel
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  python-torch-rocm-devel
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocminfo
BuildRequires:  roctracer-devel
%else
BuildRequires:  cmake(sleef)
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(numa)
BuildRequires:  python-torch-devel
%endif

Requires:       ninja
%if %{with rocm}
Requires:       python-torch-rocm
Requires:       python3dist(triton)
# NOTE: no Requires on triton_kernels -- openRuyi does not package it.  It is
# a separate pure-Python distribution living in the triton repo, versioned on
# its own tag rather than the compiler's, and the tag matching triton 3.7.x no
# longer provides the API vLLM imports.  vLLM detects its absence and runs the
# gpt-oss/MXFP4 MoE through Mxfp4MoeBackend.EMULATION instead.
Requires:       amdsmi
%else
Requires:       python3dist(torch)
%endif

%if %{with rocm}
Provides:       vllm-rocm = %{version}-%{release}
Conflicts:      python-%{srcname}
%else
Provides:       python-%{srcname} = %{version}-%{release}
Provides:       vllm = %{version}-%{release}
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
Conflicts:      python-%{srcname}-rocm
%endif

%patchlist
# Upstream PR #45532: clang requires mwaitxintrin.h via x86intrin.h.
0001-Fix-clang-spinloop-mwaitx-include.patch
%if %{without rocm}
# Adjust CPU backend for openRuyi's OpenMP path
2001-CPU-backend-OpenMP-path.patch
%endif
# Ignore some version requirement; Tailor some packages
2002-Adjust-dependencies-for-openRuyi.patch
%if %{with rocm}
# Run find_package(hipsparselt) before find_package(Torch) for proper link target
2003-ROCm-hipsparselt-ordering.patch
%endif
# Single-process: fall back to a fake distributed backend when torch lacks
# the gloo c10d backend (lets vLLM run without rebuilding torch w/ USE_GLOO=ON).
2005-CPU-single-process-fake-distributed-backend.patch
%if %{with rocm}
# cumem_allocator (LANGUAGE CXX) never gets -DUSE_ROCM on the HIP build, so
# cumem_allocator_compat.h takes the CUDA path and #includes cuda_runtime_api.h.
2006-cumem_allocator-define-USE_ROCM-for-CXX-target.patch
# triton_kernels.cmake otherwise git-clones the triton repo at configure time
# (no network on OBS); vLLM only uses the bundled copy as an import fallback.
2007-Skip-triton_kernels-bundling-via-env.patch
%endif

%description
vLLM is a fast and easy-to-use library for LLM inference and serving, featuring
PagedAttention for efficient management of attention key/value memory,
continuous batching of incoming requests, and an OpenAI-compatible API server.

%prep -a
%if %{without rocm}
# OneDNN is used when building CPU backend
tar -xzf %{SOURCE2}
%endif

%generate_buildrequires
%if %{with rocm}
export VLLM_VERSION_OVERRIDE=%{version}+rocm
export VLLM_TARGET_DEVICE=rocm
%else
export VLLM_VERSION_OVERRIDE=%{version}+cpu
export VLLM_TARGET_DEVICE=cpu
%endif
%pyproject_buildrequires -R

%build -p
%if %{with rocm}
export VLLM_VERSION_OVERRIDE=%{version}+rocm
export VLLM_TARGET_DEVICE=rocm
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
export ROCM_HOME=%{_prefix}
export PATH=%{rocmllvm_bindir}:$PATH
export HIP_CLANG_PATH=%{rocmllvm_bindir}
# Do not bundle triton_kernels into vllm/third_party (2007): openRuyi ships no
# triton_kernels at all (see the Requires note above), and the cmake module
# would need network access to fetch it.
export VLLM_SKIP_TRITON_KERNELS=1
# --rocm-device-lib-path: the LLVM-21 clang looks for the AMDGPU device bitcode
# in its own resource dir, but rocm-device-libs installs it under
# %{_prefix}/lib/clang/%{rocmllvm_version}/amdgcn/bitcode, so point clang there
export CMAKE_ARGS="-DCMAKE_HIP_FLAGS=--rocm-device-lib-path=%{_prefix}/lib/clang/%{rocmllvm_version}/amdgcn/bitcode"
%else
export VLLM_VERSION_OVERRIDE=%{version}+cpu
export VLLM_TARGET_DEVICE=cpu
# Prevent FetchContent from cloning oneDNN in the network-isolated OBS worker
# (unused when the arch/ISA does not enable the oneDNN path).
export FETCHCONTENT_SOURCE_DIR_ONEDNN="$PWD/oneDNN-3.10"
# RISC-V CPU: cpu_extension.cmake auto-detects the RVV vector length from
# /proc/cpuinfo. SG2044 has VLEN=128
%ifarch riscv64
export CMAKE_ARGS="-DVLLM_RVV_VLEN=128"
%endif
%endif
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
# importing vllm pulls its large runtime dependency stack that is not、packaged
# on openRuyi, and needs a GPU runtime.
# Temporarily skip them

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/vllm

%changelog
%autochangelog
