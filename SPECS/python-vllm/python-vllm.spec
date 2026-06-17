# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname vllm

%global toolchain clang

# TODO: gfx1100 for test build
%global rocm_gpu_arch gfx1100

Name:           python-%{srcname}
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

# cumem_allocator (LANGUAGE CXX) never gets -DUSE_ROCM on the HIP build, so
# cumem_allocator_compat.h takes the CUDA path and #includes cuda_runtime_api.h.
Patch0:         0001-cumem_allocator-define-USE_ROCM-for-CXX-target.patch

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

# --- Toolchain --------------------------------------------------------------
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  libstdc++-devel
BuildRequires:  cmake
BuildRequires:  ninja
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

Requires:       python3dist(torch)
Requires:       python3dist(triton)
Requires:       amdsmi
# vLLM's "ninja" dependency is the PyPI wheel that bundles a ninja binary for
# pip/venv users; at runtime vLLM/torch only invoke the ninja executable on
# PATH, which the system package provides.  Require that and drop the PyPI wheel
# requirement in %prep (openRuyi does not package the wheel).
Requires:       ninja

# For convention
Provides:       vllm = %{version}-%{release}
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
vLLM is a fast and easy-to-use library for LLM inference and serving, featuring
PagedAttention for efficient management of attention key/value memory,
continuous batching of incoming requests, and an OpenAI-compatible API server.

%prep -a
sed -i -e 's/setuptools>=77.0.3,<81.0.0/setuptools/' pyproject.toml
# cmake and ninja in pyproject.toml's build-system.requires resolve to system
# packages on openRuyi (BuildRequires above), not python3dist(...); without this
# the buildrequires generator emits unresolvable python3dist(cmake)/(ninja).
sed -i -e '/"cmake>=3.26.1",/d' -e '/"ninja",/d' pyproject.toml

# --- Runtime dependency adjustments (vLLM requirements/*.txt -> openRuyi) ------
# Drop the PyPI "ninja" wheel dep: vLLM/torch only need a ninja binary on PATH at
# runtime, which the system "ninja" package (Requires: above) provides.
sed -i '/^ninja /d' requirements/common.txt

# Relax vLLM's runtime pins to the newer, compatible versions openRuyi ships.
# protobuf: drop only the !=6.33.2.* band so base's 6.33.2 resolves.  That band
# is the CVE-2026-0994 mitigation (fixed upstream in 6.33.5), so this relies on
# openRuyi's protobuf carrying the backport -- revisit if base lags behind.
sed -i 's/, !=6\.33\.2\.\*//' requirements/common.txt
# Exact "==" pins -> unpinned; base ships newer, compatible releases.
sed -i 's/^lark == 1.2.2/lark/' requirements/common.txt
sed -i 's/^grpcio==1.78.0/grpcio/' requirements/rocm.txt
sed -i 's/^grpcio-reflection==1.78.0/grpcio-reflection/' requirements/rocm.txt
sed -i 's/^tensorizer==2.10.1/tensorizer/' requirements/rocm.txt
# setuptools: base is 82.x; drop the <81 (common) / <80 (rocm) upper bounds.
sed -i 's/setuptools>=77.0.3,<81.0.0/setuptools>=77.0.3/' requirements/common.txt
sed -i 's/setuptools>=77.0.3,<80.0.0/setuptools>=77.0.3/' requirements/rocm.txt
# Extra subpackages base does not build: [standard] only adds the
# uvicorn/multipart/httpx stack (base has uvicorn); [image] only adds opencv,
# which vLLM already requires directly (the opencv-python line below).
sed -i 's/fastapi\[standard\]/fastapi/' requirements/common.txt
sed -i 's/mistral_common\[image\]/mistral_common/' requirements/common.txt
# base ships the cv2 module as the "opencv" dist (4.13.0), not upstream's
# "opencv-python-headless" dist name.
sed -i 's/opencv-python-headless/opencv/' requirements/common.txt

# Drop runtime deps openRuyi does not package yet.  Tracked for later packaging:
#   numba                       - N-gram speculative decoding (needs llvmlite)
#   opentelemetry-exporter-otlp - OTLP trace export
# Optional vLLM features skipped for the riscv64 preview:
#   openai-harmony (gpt-oss), amd-quark (Quark quant), conch-triton-kernels,
#   tilelang, runai-model-streamer (cloud model streaming).
sed -i '/^numba /d' requirements/rocm.txt
sed -i '/^opentelemetry-exporter-otlp/d' requirements/common.txt
sed -i '/^openai-harmony/d' requirements/common.txt
sed -i '/^amd-quark/d' requirements/rocm.txt
sed -i '/^conch-triton-kernels/d' requirements/rocm.txt
sed -i '/^tilelang/d' requirements/rocm.txt
sed -i '/^runai-model-streamer/d' requirements/rocm.txt

# Replace the network-fetching triton_kernels external project with the offline
# stub (see Source1).
cp -f %{SOURCE1} cmake/external_projects/triton_kernels.cmake

# torch's Caffe2Targets.cmake references roc::hipsparselt in the torch_hip link
# interface, but LoadHIP.cmake treats hipsparselt as optional.  Ensure
# find_package(hipsparselt) runs before find_package(Torch) so the target exists.
sed -i '/^find_package(Torch REQUIRED)$/i find_package(hipsparselt CONFIG PATHS /usr/lib64/cmake/hipsparselt)' CMakeLists.txt

# clang (unlike gcc) forbids including <mwaitxintrin.h> directly and errors out;
# it must come via <x86intrin.h>. This monitorx/mwaitx path is x86-only and
# guarded by #if defined(__x86_64__), so the substitution no-ops on riscv64.
sed -i -e 's@#include <mwaitxintrin.h>@#include <x86intrin.h>@' csrc/spinloop.cpp

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
%{_bindir}/vllm

%changelog
%autochangelog
