# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname vllm

# The whole ROCm stack builds with clang.
%global toolchain clang

# vLLM v0.22.1 pins torch == 2.11.0 for both CUDA and ROCm, matching the
# python-torch / python-triton already in this stack.  The CMake extensions
# (_C, _moe_C, _rocm_C, cumem_allocator) are large AMDGPU device-code links, so
# drop LTO and the dwz pass to keep memory in check (same as python-torch).
%global _lto_cflags %{nil}
%define _find_debuginfo_dwz_opts %{nil}

# Only gfx1100 is supported on openRuyi (see python-torch).
%global rocm_gpu_arch gfx1100

Name:           python-%{srcname}
Version:        0.22.1
Release:        %autorelease
Summary:        A high-throughput and memory-efficient inference and serving engine for LLMs
License:        Apache-2.0
URL:            https://github.com/vllm-project/vllm
#!RemoteAsset:  sha256:4666b4052880d29c4a2c3d5b14cbb37b0457de1ea495dafc07ee128e7f3c4ad8
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz

# cumem_allocator (LANGUAGE CXX) never gets -DUSE_ROCM on the HIP build, so
# cumem_allocator_compat.h takes the CUDA path and #includes cuda_runtime_api.h.
Patch0:         0001-cumem_allocator-define-USE_ROCM-for-CXX-target.patch

# Offline replacement for cmake/external_projects/triton_kernels.cmake, which
# otherwise git-clones the triton repo at configure time (no network on OBS).
Source1:        triton_kernels-stub.cmake

BuildSystem:    pyproject
# %%pyproject_save_files needs the importable module name.
BuildOption(install):  vllm

# --- Python build backend (build-system.requires from pyproject.toml) -------
# setup.py imports torch, setuptools_scm and setuptools_rust at module load, so
# these must be present before %%pyproject_buildrequires can run the backend.
BuildRequires:  pyproject-rpm-macros
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

# --- Toolchain --------------------------------------------------------------
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  compiler-rt
BuildRequires:  lld
# clang-offload-bundler invokes llvm-objcopy during HIP offload linking.
BuildRequires:  llvm
BuildRequires:  libstdc++-devel
BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  hipcc
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocm-device-libs
BuildRequires:  roctracer-devel

# --- ROCm libraries vLLM's HIP extensions link against ----------------------
# torch ${TORCH_LIBRARIES} drags in the ROCm runtime libs, so the same set that
# python-torch builds against has to be available here too.
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hipcub)
BuildRequires:  cmake(hipfft)
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(hipsparse)
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

# Core runtime deps that are actually packaged on openRuyi. The full vLLM
# runtime stack (transformers, fastapi, ...) is large and mostly unpackaged;
# those install_requires are emitted automatically from the wheel metadata.
Requires:       python3dist(torch)
Requires:       python3-triton
Requires:       amdsmi

Provides:       vllm = %{version}-%{release}
Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
vLLM is a fast and easy-to-use library for LLM inference and serving, featuring
PagedAttention for efficient management of attention key/value memory,
continuous batching of incoming requests, and an OpenAI-compatible API server.

This build targets the AMD ROCm (HIP) backend for gfx1100.

%prep -a
# cmake and ninja are supplied as system BuildRequires and the wheel is built
# with --no-build-isolation, so drop them from build-system.requires; otherwise
# %%pyproject_buildrequires emits unsatisfiable python3dist(cmake)/python3dist(ninja).
sed -i -e '/^[[:space:]]*"cmake>=3.26.1",$/d' -e '/^[[:space:]]*"ninja",$/d' pyproject.toml

# Replace the network-fetching triton_kernels external project with the offline
# stub (see Source1).
cp -f %{SOURCE1} cmake/external_projects/triton_kernels.cmake

%generate_buildrequires
# Tarball builds have no git, so setuptools_scm cannot infer the version;
# VLLM_VERSION_OVERRIDE sets SETUPTOOLS_SCM_PRETEND_VERSION and also bypasses
# the "+rocmXYZ" local-version suffix in setup.py:get_vllm_version().
export VLLM_TARGET_DEVICE=rocm
export VLLM_VERSION_OVERRIDE=%{version}
export ROCM_PATH=%{_prefix}
# -R: skip vLLM's huge runtime requirement set as build dependencies; only the
# build backend deps are needed to produce the wheel.
%pyproject_buildrequires -R

%build -p
export VLLM_TARGET_DEVICE=rocm
export VLLM_VERSION_OVERRIDE=%{version}
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
# Release (not RelWithDebInfo) trims compile time and memory on the big kernels.
export CMAKE_BUILD_TYPE=Release

# Cap parallelism by available memory: the HIP kernel translation units are
# memory hungry and will thrash or OOM otherwise.
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

%changelog
%autochangelog
