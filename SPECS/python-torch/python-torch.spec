# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Originally extracted from Fedora Project
# Authors: The Fedora Project Contributors

%global srcname torch

%global toolchain clang

%global pypi_version 2.11.0
%global miniz_version 3.0.2

# For -test subpackage
# suitable only for local testing
# Install and do something like
#   export LD_LIBRARY_PATH=/usr/lib64/python3.12/site-packages/torch/lib
#   /usr/lib64/python3.12/site-packages/torch/bin/test_api, test_lazy
%bcond test 1

# The "cpu" multibuild flavor builds a CPU-only torch; the default flavor builds
# the ROCm backend.  Local builds can also force CPU with --without rocm.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "cpu"
%bcond rocm 0
%else
%bcond rocm 1
%endif

# For testing distributed+rccl etc.
# TODO: openmpi not included in openRuyi
%bcond mpi 0

%global _lto_cflags %nil

# Disable dwz with rocm because memory can be exhausted
%if %{with rocm}
%define _find_debuginfo_dwz_opts %{nil}
%endif

# Pytorch third-party buildrequires
#
# These system_xxx is kept for debug with some reasons:
#
# 1. some package that is not included in openRuyi.
# 2. some package on openRuyi lack some required component.
# 3. the corresponding version is mismatched with openRuyi.
%bcond system_flatbuffers 0
# Pytorch hardcode httplib to third_party/cpp-httplib
%bcond system_httplib 0
# TODO: kineto not included in openruyi
%bcond system_kineto 0
# TODO: tensorpipe not included in openRuyi
%bcond system_tensorpipe 0

%if %{with rocm}
Name:           python-%{srcname}-rocm
%else
Name:           python-%{srcname}
%endif
Version:        %{pypi_version}
Release:        %autorelease
Summary:        PyTorch AI/ML framework
# See license.txt for license details
License:        BSD-3-Clause AND BSD-2-Clause AND 0BSD AND Apache-2.0 AND MIT AND BSL-1.0 AND GPL-3.0-or-later AND Zlib
URL:            https://pytorch.org/
#!RemoteAsset:  sha256:52872a6bbdc42334b00051d88a92f801cfd9be730abdd2b37a2d08996f53bb29
Source0:        https://github.com/pytorch/pytorch/archive/refs/tags/v%{version}.tar.gz
%if %{without system_flatbuffers}
%global flatbuffers_version 24.12.23
#!RemoteAsset:  sha256:7e2ef35f1af9e2aa0c6a7d0a09298c2cb86caf3d4f58c0658b306256e5bcab10
Source1:        https://github.com/google/flatbuffers/archive/refs/tags/v%{flatbuffers_version}.tar.gz
%endif
%if %{without system_tensorpipe}
# Developement on tensorpipe has stopped, repo made read only July 1, 2023, this is the last commit
%global tp_commit 2b4cd91092d335a697416b2a3cb398283246849d
%global tp_scommit 2b4cd91
#!RemoteAsset:  sha256:0e85ca56bfe25ed7b3026d2784f716eb10ed1328ade346e3a252814752c57eeb
Source2:       https://github.com/pytorch/tensorpipe/archive/%{tp_commit}/tensorpipe-%{tp_scommit}.tar.gz
# The old libuv tensorpipe uses
#!RemoteAsset:  sha256:6cfeb5f4bab271462b4a2cc77d4ecec847fdbdc26b72019c27ae21509e6f94fa
Source3:       https://github.com/libuv/libuv/archive/refs/tags/v1.41.0.tar.gz
# Developement afaik on libnop has stopped, this is the last commit
%global nop_commit 910b55815be16109f04f4180e9adee14fb4ce281
%global nop_scommit 910b558
#!RemoteAsset:  sha256:ec3604671f8ea11aed9588825f9098057ebfef7a8908e97459835150eea9f63a
Source4:       https://github.com/google/libnop/archive/%{nop_commit}/libnop-%{nop_scommit}.tar.gz
%endif

%if %{without system_httplib}
%global hl_commit 4d7c9a788de136071ccf0dd4e96239151e2adadb
%global hl_scommit 4d7c9a7
#!RemoteAsset:  sha256:8ecb7bbe844f9b4a1418b8a015d0f815d021d2c0d53291387122cb510c8783ef
Source5:       https://github.com/yhirose/cpp-httplib/archive/%{hl_commit}/cpp-httplib-%{hl_scommit}.tar.gz
%endif
%if %{without system_kineto}
%global ki_commit 23b5bb5764b3dec988e25c52098407e508d84bb4
%global ki_scommit 23b5bb5
#!RemoteAsset:  sha256:5b85352628319e22c48b589d2f423f3761479058f87a3ecc328818f16e4394c6
Source6:       https://github.com/pytorch/kineto/archive/%{ki_commit}/kineto-%{ki_scommit}.tar.gz
%endif

%global mslk_commit 3d332d1c0c0ac7765852c97b3979c9ef913e037f
%global mslk_scommit 3d332d1
#!RemoteAsset:  sha256:1944e67d1baeffef3bb8f89793ea06e0f05b88aac4d5cd89b4558a21aca6754b
Source7:       https://github.com/meta-pytorch/MSLK/archive/%{mslk_commit}/MSLK-%{mslk_scommit}.tar.gz

# gloo: pinned submodule providing the torch.distributed Gloo backend.
# Required by USE_GLOO=ON; the v%{version} GitHub archive ships
# third_party/gloo empty (submodules excluded), so vendor it explicitly.
%global gloo_commit 3135b0b41b67dde590eef0938a0bf3d6238df5f7
%global gloo_scommit 3135b0b
#!RemoteAsset:  sha256:6a8c7ea8e3048762aaf3472f969ee42c2163e7ffcbb195eea4f245c1f7bd8cc3
Source9:       https://github.com/pytorch/gloo/archive/%{gloo_commit}/gloo-%{gloo_scommit}.tar.gz

# pytorch upstream issue #173707: libtorch_hip.so references the
# const_data_ptr / mutable_data_ptr / data_ptr template family with a
# different (non-SFINAE) mangling than libtorch_cpu.so exports.
# Appended to aten/src/ATen/core/Tensor.cpp in %prep when rocm is enabled.
Source8:       pytorch-rocm-symbol-bridge.cpp

# Fix magma version encoding
# https://github.com/pytorch/pytorch/pull/180388
Patch0:        0001-pytorch-magma-2.10.0-version-encoding.patch

# CPython 3.13.8 inspect.getsourcelines() truncates a decorated function's
# source when a comment line sits between the last decorator and the def
# (fixed in later 3.13.x).  TorchScript parses the RNN/LSTM/GRU forward
# overload stubs at import time, so "import torch" dies with an
# IndentationError.  Drop the offending pyrefly comment lines.
# https://github.com/python/cpython/issues/139783
Patch1:        0002-remove-pyrefly-comments-between-overload-decorator-and-def.patch

# Default to hipBLASLt on gfx1100: upstream lists gfx1100 only as a hipBLASLt-
# supported arch, not a preferred one, so torch defaults to rocBLAS -- whose fp16
# GEMM has no Tensile solution for some shapes on gfx1100, failing with
# HIPBLAS_STATUS_INTERNAL_ERROR.  hipBLASLt handles every shape.
Patch2:        0003-default-to-hipblaslt-on-gfx1100.patch

BuildRequires:  cmake
BuildRequires:  cmake(concurrentqueue)
BuildRequires:  cmake(sleef)
BuildRequires:  cpuinfo
# Although eigen3 enabled on openruyi, it cannot be detected during conf
# TODO: Fix this
BuildRequires:  eigen3
BuildRequires:  foxi-devel
BuildRequires:  libomp-devel
BuildRequires:  ninja
BuildRequires:  pkgconfig(fmt)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(numa)
BuildRequires:  pkgconfig(openblas64)
BuildRequires:  pkgconfig(protobuf)
# The system protobuf's cmake config does find_package(ZLIB), which imports the
# ZLIB::ZLIBSTATIC target referencing /usr/lib64/libz.a; cmake configure aborts
# if that static lib is absent. Pull it in (provided by zlib-ng-compat-static).
BuildRequires:  zlib-ng-compat-static
BuildRequires:  pkgconfig(valgrind)
BuildRequires:  pocketfft-devel
BuildRequires:  pthreadpool-devel
BuildRequires:  fp16-devel
BuildRequires:  fxdiv-devel
BuildRequires:  psimd-devel
BuildRequires:  xnnpack-devel = 0+git20260211.312eb7e
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(filelock)
BuildRequires:  python3dist(jinja2)
BuildRequires:  python3dist(networkx)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pybind11)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(sympy)
BuildRequires:  python3dist(typing-extensions)

%if %{with system_httplib}
BuildRequires:  cmake(httplib)
%endif

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  libstdc++-devel
BuildRequires:  compiler-rt
BuildRequires:  cmake(LLVM)
BuildRequires:  lld

BuildRequires:  cmake(ONNX)
BuildRequires:  cmake(onnxruntime)

%if %{with mpi}
BuildRequires:  openmpi-devel
%endif

%if %{with system_flatbuffers}
BuildRequires:  pkgconfig(flatbuffers)
%endif

%if %{with rocm}
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
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocsolver)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  cmake(rocthrust)
BuildRequires:  pkgconfig(magma)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel
%endif

%if %{with test}
BuildRequires:  cmake(GTest)
%endif

Requires:       python3dist(dill)
Requires:       python3dist(pyyaml)
%if %{with rocm}
Requires:       amdsmi
%endif

# The canonical torch names resolve to the CPU build; CPU and ROCm are mutually
# exclusive.  The ROCm flavor drops the auto-generated python3dist(torch) provide
# so the generic torch identity stays unambiguously CPU -- ROCm consumers ask for
# python-torch-rocm by name.
# Both flavors satisfy "any torch backend" for backend-agnostic consumers.
Provides:       python-torch-backend = %{version}-%{release}
%if %{with rocm}
%global __provides_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)
# CPU flavor now carries the bare python-torch name (masks base's python-torch).
Conflicts:      python-%{srcname}
%else
Provides:       python-%{srcname} = %{version}-%{release}
Provides:       pytorch = %{version}-%{release}
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
Conflicts:      python-%{srcname}-rocm
%endif

%description
PyTorch is a Python package that provides two high-level features:

 * Tensor computation (like NumPy) with strong GPU acceleration
 * Deep neural networks built on a tape-based autograd system

You can reuse your favorite Python packages such as NumPy, SciPy,
and Cython to extend PyTorch when needed.

%prep
%autosetup -p1 -n pytorch-%{version}

# GitHub release tarballs identify the version as an alpha, so replace that
echo "%{pypi_version}" > version.txt

# Remove bundled egg-info
rm -rf %{srcname}.egg-info

%if %{without system_flatbuffers}
tar xf %{SOURCE1}
rm -rf third_party/flatbuffers/*
cp -r flatbuffers-%{flatbuffers_version}/* third_party/flatbuffers/
%endif

%if %{without system_tensorpipe}
tar xf %{SOURCE2}
rm -rf third_party/tensorpipe/*
cp -r tensorpipe-*/* third_party/tensorpipe/
tar xf %{SOURCE3}
rm -rf third_party/tensorpipe/third_party/libuv/*
cp -r libuv-*/* third_party/tensorpipe/third_party/libuv/
tar xf %{SOURCE4}
rm -rf third_party/tensorpipe/third_party/libnop/*
cp -r libnop-*/* third_party/tensorpipe/third_party/libnop/

# gcc 15 include cstdint
sed -i '/#include <tensorpipe.*/a#include <cstdint>' third_party/tensorpipe/tensorpipe/common/allocator.h
sed -i '/#include <tensorpipe.*/a#include <cstdint>' third_party/tensorpipe/tensorpipe/common/memory.h
%endif

%if %{without system_httplib}
tar xf %{SOURCE5}
rm -rf third_party/cpp-httplib/*
cp -r cpp-httplib-*/* third_party/cpp-httplib/
%endif

%if %{without system_kineto}
tar xf %{SOURCE6}
rm -rf third_party/kineto/*
cp -r kineto-*/* third_party/kineto/
%endif

tar xf %{SOURCE7}
rm -rf third_party/mslk/*
cp -r MSLK-*/* third_party/mslk/

# GPU-arch / default-BLAS-backend handling is done in Patch2 (0003-*).  The arch
# lists moved from Blas.cpp to CUDAHooks.cpp in torch 2.11, so the old in-place
# seds here silently became no-ops; a patch fails the build loudly if upstream
# moves them again.

# Need to pip this
sed -i -e '/fsspec/d' setup.py

# Relax the setuptools<82 runtime pin — the distro ships 82.0.1.  The bound is
# in setup.py's install_requires, which becomes the wheel's Requires-Dist and
# thus the RPM Requires; editing pyproject.toml (build-system) does not affect
# it, so torch's dependents (python-triton, python-vllm) were left unresolvable.
sed -i -e 's@"setuptools<82"@"setuptools"@' setup.py

# Use system sympy
sed -i -e 's@sympy==1.13.1@sympy>=1.13.1@' setup.py

# A new dependency
# Connected to USE_FLASH_ATTENTION, since this is off, do not need it
sed -i -e '/aotriton.cmake/d' cmake/Dependencies.cmake
# Compress hip
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc --offload-compress@' cmake/Dependencies.cmake
# Silence noisy warning
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -Wno-pass-failed@' cmake/Dependencies.cmake
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -Wno-unused-command-line-argument@' cmake/Dependencies.cmake
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -Wno-unused-result@' cmake/Dependencies.cmake
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -Wno-deprecated-declarations@' cmake/Dependencies.cmake
# Fix: error: branch size exceeds simm16 (AMDGPUAsmBackend.cpp)
# -amdgpu-s-branch-bits=15(default is 16) and -amdgpu-long-branch-factor=2 are needed to avoid 'branch size exceed simm16' error
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -mllvm --amdgpu-s-branch-bits=15@' cmake/Dependencies.cmake
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc -mllvm --amdgpu-long-branch-factor=2@' cmake/Dependencies.cmake

# Use parallel jobs for GPU offload compilation
sed -i -e 's@HIP_CLANG_FLAGS -fno-gpu-rdc@HIP_CLANG_FLAGS -fno-gpu-rdc --offload-jobs=8@' cmake/Dependencies.cmake
# Need to link with librocm_smi64 (intra_node_comm.cpp calls rsmi_init /
# rsmi_is_P2P_accessible). The target string is "hiprtc::hiprtc" — the previous
# pattern "hipzrtc::hiprtc" had a stray 'z' so the sed was a no-op and
# libtorch_hip.so ended up with an undefined rsmi_init symbol.
sed -i -e 's@hiprtc::hiprtc@hiprtc::hiprtc rocm_smi64@' cmake/Dependencies.cmake

# No third_party fmt, use system
sed -i -e 's@fmt::fmt-header-only@fmt@' CMakeLists.txt
sed -i -e 's@fmt::fmt-header-only@fmt@' aten/src/ATen/CMakeLists.txt
sed -i -e 's@list(APPEND ATen_HIP_INCLUDE $<TARGET_PROPERTY:fmt,INTERFACE_INCLUDE_DIRECTORIES>)@@' aten/src/ATen/CMakeLists.txt

sed -i -e 's@fmt::fmt-header-only@fmt@' third_party/kineto/libkineto/CMakeLists.txt
sed -i -e 's@fmt::fmt-header-only@fmt@' c10/CMakeLists.txt
sed -i -e 's@fmt::fmt-header-only@fmt@' torch/CMakeLists.txt
sed -i -e 's@fmt::fmt-header-only@fmt@' cmake/Dependencies.cmake
sed -i -e 's@fmt::fmt-header-only@fmt@' caffe2/CMakeLists.txt

sed -i -e 's@add_subdirectory(${PROJECT_SOURCE_DIR}/third_party/fmt)@#add_subdirectory(${PROJECT_SOURCE_DIR}/third_party/fmt)@' cmake/Dependencies.cmake
sed -i -e 's@set_target_properties(fmt-header-only PROPERTIES INTERFACE_COMPILE_FEATURES "")@#set_target_properties(fmt-header-only PROPERTIES INTERFACE_COMPILE_FEATURES "")@' cmake/Dependencies.cmake
sed -i -e 's@list(APPEND Caffe2_DEPENDENCY_LIBS fmt::fmt-header-only)@#list(APPEND Caffe2_DEPENDENCY_LIBS fmt::fmt-header-only)@' cmake/Dependencies.cmake

# No third_party FXdiv
sed -i -e 's@if(NOT TARGET fxdiv)@if(MSVC AND USE_XNNPACK)@' caffe2/CMakeLists.txt
sed -i -e 's@TARGET_LINK_LIBRARIES(torch_cpu PRIVATE fxdiv)@#TARGET_LINK_LIBRARIES(torch_cpu PRIVATE fxdiv)@' caffe2/CMakeLists.txt

# https://github.com/pytorch/pytorch/issues/149803
# Tries to checkout nccl
sed -i -e 's@    checkout_nccl()@    True@' tools/build_pytorch_libs.py

# Disable the use of check_submodule's in the setup.py, we are a tarball, not a git repo
sed -i -e 's@check_submodules()$@#check_submodules()@' setup.py

# Release comes fully loaded with third party src
# Remove what we can
#
# For 2.1 this is all but miniz-2.1.0
# Instead of building as a library, caffe2 reaches into
# the third_party dir to compile the file.
# mimiz is licensed MIT
# https://github.com/richgel999/miniz/blob/master/LICENSE
mv third_party/miniz-%{miniz_version} .
#
# setup.py depends on this script
mv third_party/build_bundled.py .

%if %{without system_flatbuffers}
# Need the just untarred flatbuffers/flatbuffers.h
mv third_party/flatbuffers .
%endif

%if %{without system_tensorpipe}
mv third_party/tensorpipe .
%endif

%if %{without system_httplib}
mv third_party/cpp-httplib .
%endif

%if %{without system_kineto}
mv third_party/kineto .
%endif

mv third_party/mslk .

# Remove everything
rm -rf third_party/*
# Put stuff back
mv build_bundled.py third_party
mv miniz-%{miniz_version} third_party

%if %{without system_flatbuffers}
mv flatbuffers third_party
%endif

%if %{without system_tensorpipe}
mv tensorpipe third_party
%endif

%if %{without system_httplib}
mv cpp-httplib third_party
%endif

%if %{without system_kineto}
mv kineto third_party
%endif

mv mslk third_party

# gloo: vendored submodule for the torch.distributed Gloo backend (USE_GLOO=ON).
# The pytorch archive ships third_party/gloo empty and the scrub above
# (rm -rf third_party/*) drops it, so unpack and reinstate it here.
tar xf %{SOURCE9}
rm -rf third_party/gloo
mkdir -p third_party/gloo
cp -r gloo-*/* third_party/gloo/

# Fake out pocketfft, and system header will be used
mkdir third_party/pocketfft
cp /usr/include/pocketfft_hdronly.h third_party/pocketfft/

# Use the system valgrind headers
mkdir third_party/valgrind-headers
cp %{_includedir}/valgrind/* third_party/valgrind-headers

# Fix installing to /usr/lib64
sed -i -e 's@DESTINATION ${PYTHON_LIB_REL_PATH}@DESTINATION ${CMAKE_INSTALL_PREFIX}/${PYTHON_LIB_REL_PATH}@' caffe2/CMakeLists.txt

# reenable foxi linking
sed -i -e 's@list(APPEND Caffe2_DEPENDENCY_LIBS foxi_loader)@#list(APPEND Caffe2_DEPENDENCY_LIBS foxi_loader)@' cmake/Dependencies.cmake

%if %{without system_tensorpipe}
# cmake version changed
sed -i -e 's@cmake_minimum_required(VERSION 3.4)@cmake_minimum_required(VERSION 3.5)@' third_party/tensorpipe/third_party/libuv/CMakeLists.txt
sed -i -e 's@cmake_minimum_required(VERSION 3.4)@cmake_minimum_required(VERSION 3.5)@' libuv*/CMakeLists.txt
%endif

%if %{with rocm}
# Fix: hipOccupancyMaxActiveBlocksPerMultiprocessor is overloaded in new ROCm,
# force using hipModuleOccupancyMaxActiveBlocksPerMultiprocessor
sed -i -e 's/TORCH_HIP_VERSION < 305/TORCH_HIP_VERSION < 305 \&\& TORCH_HIP_VERSION > 0/' \
    aten/src/ATen/cuda/nvrtc_stub/ATenNVRTC.h
# pytorch upstream issue #173707 (gemm/bgemm variant):
# clang 21 mangles the instantiation-dependent SFINAE non-type template parameter
#   typename std::enable_if<...,Dtype>::type* = nullptr
# of at::cuda::blas::gemm/bgemm differently at an explicit specialization (the
# definition, Tn...enable_if form) than at a deduced call site (the reference,
# ...IffLPf0E... form), so libtorch_hip.so fails to dlopen with e.g.
#   undefined symbol: _ZN2at4cuda4blas4gemmIffLPf0EEEvcclllNS_10OpMathTypeIT_E4typeEPKS5_lS9_lS7_PT0_l
# Every real dtype is provided by an explicit specialization, so the SFINAE guard
# is redundant: drop it so the two overloads collapse to one primary template and
# clang emits a single consistent mangling everywhere. Must run before hipify.
sed -i \
    -e 's/, typename std::enable_if<!CUDABLAS_GEMM_DTYPE_IS_FLOAT_TYPE_AND_C_DTYPE_IS_FLOAT, Dtype>::type\* = nullptr>/>/g' \
    -e 's/, typename std::enable_if<CUDABLAS_GEMM_DTYPE_IS_FLOAT_TYPE_AND_C_DTYPE_IS_FLOAT, Dtype>::type\* = nullptr>/>/g' \
    aten/src/ATen/cuda/CUDABlas.h
# hipify
./tools/amd_build/build_amd.py
# use any hip, correct CMAKE_MODULE_PATH
sed -i -e 's@lib/cmake/hip@lib64/cmake/hip@' cmake/public/LoadHIP.cmake
sed -i -e 's@HIP 1.0@HIP MODULE@'            cmake/public/LoadHIP.cmake
# silence an assert
# sed -i -e '/qvalue = std::clamp(qvalue, qmin, qmax);/d' aten/src/ATen/native/cuda/IndexKernel.cu

# Append ROCm symbol bridge — see Source8 header for full context.
# Without this, libtorch_hip.so dlopen fails on:
#   undefined symbol: _ZNK2at10TensorBase14const_data_ptrI*Li0EEEPK*v
cat %{SOURCE8} >> aten/src/ATen/core/Tensor.cpp
%endif

# moodycamel include path needs adjusting to use the system's
sed -i -e 's@${PROJECT_SOURCE_DIR}/third_party/concurrentqueue@/usr/include/concurrentqueue@' cmake/Dependencies.cmake

%build
# Control the number of jobs
# The build can fail if too many threads exceed the physical memory
# Run at least one thread, more if CPU & memory resources are available.
COMPILE_JOBS=`nproc`
if [ ${COMPILE_JOBS}x = x ]; then
    COMPILE_JOBS=1
fi
# Take into account memory usage per core, do not thrash real memory
# TraceType/VariableType files can consume 4GB+ per compilation unit
# Use a more conservative estimate: 4GB per job for safety
BUILD_MEM=4
MEM_KB=0
MEM_KB=`cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'`
MEM_MB=`eval "expr ${MEM_KB} / 1024"`
MEM_GB=`eval "expr ${MEM_MB} / 1024"`
COMPILE_JOBS_MEM=`eval "expr 1 + ${MEM_GB} / ${BUILD_MEM}"`
if [ "$COMPILE_JOBS_MEM" -lt "$COMPILE_JOBS" ]; then
    COMPILE_JOBS=$COMPILE_JOBS_MEM
fi
# Ensure at least 2 jobs to avoid single-threading the large files
if [ "$COMPILE_JOBS" -lt 2 ]; then
    COMPILE_JOBS=2
fi
export MAX_JOBS=$COMPILE_JOBS

# cmake's ABI detection fails with clang 21 (Detecting CXX compiler ABI info - failed),
# leaving CMAKE_SIZEOF_VOID_P unset.  All openRuyi targets are 64-bit; set it explicitly
# so gloo (and anything else that checks sizeof(void*)) works without patching each guard.
export CMAKE_SIZEOF_VOID_P=8

# For verbose cmake output
# export VERBOSE=ON
# For verbose linking
# export CMAKE_SHARED_LINKER_FLAGS=-Wl,--verbose

# Manually set this hardening flag
export CMAKE_EXE_LINKER_FLAGS=-pie
export BUILD_CUSTOM_PROTOBUF=OFF
export BUILD_NVFUSER=OFF
export BUILD_SHARED_LIBS=ON
export BUILD_TEST=OFF
%if %{with test}
export BUILD_TEST=ON
%endif
# Use Release instead of RelWithDebInfo to reduce compile time and memory
# for huge generated files like TraceType/VariableType (saves ~30% compile time)
export CMAKE_BUILD_TYPE=Release
export CMAKE_FIND_PACKAGE_PREFER_CONFIG=ON
export CAFFE2_LINK_LOCAL_PROTOBUF=OFF
export INTERN_BUILD_MOBILE=OFF
export USE_DISTRIBUTED=OFF
export USE_CUDA=OFF
export USE_FAKELOWP=OFF
export USE_FBGEMM=OFF
export USE_FLASH_ATTENTION=OFF
export USE_GLOO=ON
export USE_ITT=OFF
export USE_KINETO=OFF
export USE_KLEIDIAI=OFF
export USE_LITE_INTERPRETER_PROFILER=OFF
export USE_LITE_PROTO=OFF
export USE_MAGMA=OFF
export USE_MEM_EFF_ATTENTION=OFF
export USE_MKLDNN=OFF
export USE_MPI=OFF
export USE_MSLK=OFF
export USE_NCCL=OFF
export USE_NNPACK=OFF
export USE_NUMPY=ON
export USE_OPENMP=ON
export USE_PYTORCH_QNNPACK=OFF
export USE_ROCM=OFF
export USE_SYSTEM_SLEEF=ON
export USE_SYSTEM_EIGEN_INSTALL=ON
export USE_SYSTEM_ONNX=ON
export USE_SYSTEM_PYBIND11=ON
export USE_SYSTEM_LIBS=OFF
export USE_SYSTEM_NCCL=OFF
export USE_XNNPACK=OFF
export USE_XPU=OFF
export USE_SYSTEM_PTHREADPOOL=ON
export USE_SYSTEM_CPUINFO=ON
export USE_SYSTEM_FP16=ON
export USE_SYSTEM_FXDIV=ON
export USE_SYSTEM_PSIMD=ON
export USE_SYSTEM_XNNPACK=OFF
export USE_DISTRIBUTED=ON
export USE_TENSORPIPE=ON
%if %{without system_tensorpipe}
export TP_BUILD_LIBUV=OFF
%endif

%if %{with mpi}
export USE_MPI=ON
%endif

%if %{with rocm}
export USE_ROCM=ON
export USE_ROCM_CK_SDPA=OFF
export USE_ROCM_CK_GEMM=OFF
export USE_FBGEMM_GENAI=OFF

export USE_MAGMA=ON
export HIP_PATH=`hipconfig -p`
export ROCM_PATH=`hipconfig -R`

# pytorch uses clang, not hipcc
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}

export CMAKE_NO_SYSTEM_FROM_IMPORTED=ON

# export CMAKE_BUILD_TYPE=Debug
%endif

export CMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES="/usr/include"
export CMAKE_C_IMPLICIT_INCLUDE_DIRECTORIES="/usr/include"

export LDFLAGS="-fuse-ld=lld %{?__global_ldflags}"
export CMAKE_LIBRARY_PATH=/usr/lib64
export CMAKE_PREFIX_PATH="/usr:/usr/lib64/cmake:/usr/lib/python3.13/site-packages"

%pyproject_wheel

%install
%if %{with rocm}
export USE_ROCM=ON
export USE_ROCM_CK=OFF
export HIP_PATH=`hipconfig -p`
export ROCM_PATH=`hipconfig -R`

# pytorch uses clang, not hipcc
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
%endif

%pyproject_install
%pyproject_save_files '*torch*'

%check
%pyproject_check_import torch

%files
%license LICENSE
%doc README.md
%{_bindir}/torchrun
%{python3_sitearch}/%{srcname}*
%{python3_sitearch}/functorch

%changelog
%{?autochangelog}
