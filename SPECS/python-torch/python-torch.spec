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

%global miniz_version 3.0.2

# For -test subpackage
# suitable only for local testing
# Install and do something like
#   export LD_LIBRARY_PATH=/usr/lib64/python3.12/site-packages/torch/lib
#   /usr/lib64/python3.12/site-packages/torch/bin/test_api, test_lazy
%bcond test 1

# The default flavor builds a CPU-only torch; the "rocm" multibuild flavor
# builds the ROCm backend.  Local builds can also force ROCm with --with rocm.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%bcond rocm 1
%else
%bcond rocm 0
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
Version:        2.13.0
Release:        %autorelease
Summary:        PyTorch AI/ML framework
# See license.txt for license details
License:        BSD-3-Clause AND BSD-2-Clause AND 0BSD AND Apache-2.0 AND MIT AND BSL-1.0 AND GPL-3.0-or-later AND Zlib
URL:            https://pytorch.org/
VCS:            git:https://github.com/pytorch/pytorch.git
# PyTorch publishes only wheels on PyPI.  The GitHub tag archive excludes
# submodules, but the official release asset includes the third_party C++
# sources needed for a distro source build.
#!RemoteAsset:  sha256:66614a19060f69cfd63cd0295f65a1241bd15df2fa65c60ae51066c11c2ce812
Source0:        https://github.com/pytorch/pytorch/releases/download/v%{version}/pytorch-v%{version}.tar.gz

# googletest is provided by the system gtest-devel (openRuyi package) when
# BUILD_TEST=ON; see 2004-use-system-googletest.patch.

# pytorch upstream issue #173707: libtorch_hip.so references the
# const_data_ptr / mutable_data_ptr / data_ptr template family with a
# different (non-SFINAE) mangling than libtorch_cpu.so exports.
# Appended to aten/src/ATen/core/Tensor.cpp in %prep when rocm is enabled.
Source8:       pytorch-rocm-symbol-bridge.cpp

# Functional smoke test for the just-built torch, run by the check phase.
Source11:      pytorch-smoke-test.py

BuildSystem:    pyproject
# Save every importable torch* top-level (torch, torchgen, functorch) plus the
# torchrun entrypoint; consumed by %%files -f %%{pyproject_files}.  -l is omitted
# because torch declares no PEP 639 License-File, so %%license LICENSE stays.
BuildOption(install):  '*torch*'
# The declarative check phase runs %%pyproject_check_import on the saved module
# list; exclude the entries that cannot be imported in the build chroot:
#  - torch.lib.lib*: C++ shared libs in torch/lib (libtorch, libc10, libtorch_cpu,
#    the ROCm-only libtorch_hip, ...) shipped for rpath only -- no PyInit_ symbol.
#  - torchgen.static_runtime.gen_static_runtime_ops: imports Meta-internal libfb;
#    a build-time codegen tool, not part of the installed runtime.
#  - torch.utils.tensorboard*: needs tensorboard, not yet packaged in openRuyi.
BuildOption(check):  -e 'torch.lib.lib*'
BuildOption(check):  -e 'torchgen.static_runtime.gen_static_runtime_ops'
BuildOption(check):  -e 'torch.utils.tensorboard*'

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
BuildRequires:  cmake(fmt)
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
BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(filelock)
BuildRequires:  python3dist(jinja2)
BuildRequires:  python3dist(networkx)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(packaging)
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

%if %{with test}
# System googletest for BUILD_TEST=ON (see 2004-use-system-googletest.patch).
# cmake(GTest) brings
# gtest-devel (which carries the gtest/gmock cmake config and gtest headers);
# gmock's headers ship in the separate gmock-devel package, which
# gtest-devel only runtime-Requires (not -devel), so pull it in explicitly.
BuildRequires:  cmake(GTest)
BuildRequires:  gmock-devel
# urllib3 is needed by torch.distributed.elastic.rendezvous.etcd_rendezvous_backend
# (optional etcd backend, shipped in the package); python-urllib3 is in openRuyi.
BuildRequires:  python3dist(urllib3)
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

%patchlist
# Backport google/benchmark PR #2108 so clang 22 does not fail BUILD_TEST=ON on
# a -Wc2y-extensions diagnostic from benchmark's __COUNTER__ preprocessor check.
1000-benchmark-silence-c2y-counter-warning.patch
# Disable PyTorch's ROCm aotriton ExternalProject hook; openRuyi builds with
# USE_FLASH_ATTENTION=OFF / USE_MEM_EFF_ATTENTION=OFF and must not download
# aotriton artifacts during CMake configure/build.
2000-disable-aotriton-download.patch
# torch.dot()/torch.vdot() on complex tensors return 0 because ATen's
# BLAS ABI probe misdetects OpenBLAS's cblas_*dot*_sub interface; force
# the CBLAS complex-dot path (see %build: PYTORCH_BLAS_USE_CBLAS_DOT=ON).
2001-force-cblas-complex-dot-for-openblas.patch
# Default to hipBLASLt on gfx1100: upstream lists gfx1100 only as a hipBLASLt-
# supported arch, not a preferred one, so torch defaults to rocBLAS -- whose fp16
# GEMM has no Tensile solution for some shapes on gfx1100, failing with
# HIPBLAS_STATUS_INTERNAL_ERROR.  hipBLASLt handles every shape.
2003-default-to-hipblaslt-on-gfx1100.patch
# Use the system googletest (openRuyi gtest-devel) instead of the vendored
# submodule when BUILD_TEST=ON.  Upstream hardcodes
# add_subdirectory(third_party/googletest) and the test CMakeLists link the
# bare target names gtest / gtest_main / gmock / gmock_main; switch to
# find_package(GTest) and alias the GTest:: targets to those bare names so
# the distro's shared gtest/gmock are used and not statically vendored.
2004-use-system-googletest.patch
# Append openRuyi ROCm CMAKE_HIP_FLAGS (offload jobs, the simm16 long-branch
# fix, clang warning silencing).
2005-append-hip-clang-flags.patch
# Use the system fmt instead of vendored third_party/fmt.
2006-use-system-fmt.patch
# Skip PreBuildSteps.cmake submodule sanity checks for vendored directories the
# openRuyi build intentionally prunes because system libraries or disabled
# features are used.
2007-skip-unused-submodule-prebuild-checks.patch

%description
PyTorch is a Python package that provides two high-level features:

 * Tensor computation (like NumPy) with strong GPU acceleration
 * Deep neural networks built on a tape-based autograd system

You can reuse your favorite Python packages such as NumPy, SciPy,
and Cython to extend PyTorch when needed.

%prep
%autosetup -p1 -n pytorch-v%{version}

# GitHub release tarballs identify the version as an alpha, so replace that
echo "%{version}" > version.txt

# Remove bundled egg-info
rm -rf %{srcname}.egg-info

%if %{without system_tensorpipe}
# gcc 15 include cstdint
sed -i '/#include <tensorpipe.*/a#include <cstdint>' third_party/tensorpipe/tensorpipe/common/allocator.h
sed -i '/#include <tensorpipe.*/a#include <cstdint>' third_party/tensorpipe/tensorpipe/common/memory.h
%endif

# GPU-arch / default-BLAS-backend handling is done in
# 2003-default-to-hipblaslt-on-gfx1100.patch.  The arch
# lists moved from Blas.cpp to CUDAHooks.cpp in torch 2.11, so the old in-place
# seds here silently became no-ops; a patch fails the build loudly if upstream
# moves them again.

# Need to pip this
sed -i -e '/fsspec/d' setup.py

# %%pyproject_buildrequires (run by BuildSystem: pyproject) turns pyproject.toml's
# build-system.requires into RPM BuildRequires.  On openRuyi cmake/ninja are
# system packages, not python3dist(...); requests/six are not needed for the
# --no-build-isolation wheel build; and setuptools<82 conflicts with the distro's
# 82.x.  Drop those from the [build-system] table (only there, not the identical
# [dependency-groups] copy) so only satisfiable backend deps are generated -- the
# real build deps come from the static BuildRequires above.
sed -i '/^\[build-system\]/,/^build-backend/ {
  /"cmake>=3.27",/d
  /"ninja",/d
  /"requests",/d
  /"six",/d
  s@"setuptools>=77.0.0,<82",@"setuptools>=77.0.0",@
}' pyproject.toml

# Use system sympy
sed -i -e 's@sympy==1.13.1@sympy>=1.13.1@' setup.py

# HIP_CLANG_FLAGS additions (--offload-compress / --offload-jobs=8, the
# amdgpu-s-branch-bits=15 + long-branch-factor=2 simm16 fix, and clang warning
# silencing) are applied by 2005-append-hip-clang-flags.patch.
# Need to link with librocm_smi64 (intra_node_comm.cpp calls rsmi_init /
# rsmi_is_P2P_accessible). The target string is "hiprtc::hiprtc" — the previous
# pattern "hipzrtc::hiprtc" had a stray 'z' so the sed was a no-op and
# libtorch_hip.so ended up with an undefined rsmi_init symbol.
sed -i -e 's@hiprtc::hiprtc@hiprtc::hiprtc rocm_smi64@' cmake/Dependencies.cmake

# Use the system fmt instead of the vendored third_party/fmt in the main source
# tree: applied by 2006-use-system-fmt.patch.  The vendored kineto CMakeLists
# carries the same fmt::fmt-header-only reference, so patch it here with a sed.
sed -i -e 's@fmt::fmt-header-only@fmt::fmt@g' third_party/kineto/libkineto/CMakeLists.txt

# When BUILD_TEST=ON, test cmake files reference fmt::fmt-header-only.
# Our global fmt::fmt-header-only -> fmt::fmt replacement also applies to generator
# expressions ($<TARGET_PROPERTY:fmt,...>) which fail if the system fmt target
# differs from what pytorch expects. Replace the generator expression with a
# hardcoded /usr/include (fmt is header-only and installed there).
find test -name CMakeLists.txt -exec sed -i -e 's@fmt::fmt-header-only@fmt::fmt@g' {} +
sed -i 's@\$<TARGET_PROPERTY:fmt::fmt,INTERFACE_INCLUDE_DIRECTORIES>@/usr/include@g' test/cpp/c10d/CMakeLists.txt

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

mv third_party/gloo .
%if %{with test}
mv third_party/benchmark .
%endif
mv third_party/mslk .

# Remove everything
rm -rf third_party/*
# Put stuff back
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

mv gloo third_party

%if %{with test}
# googletest is provided by the system gtest-devel (openRuyi package) instead
# of the vendored submodule -- see 2004-use-system-googletest.patch, which makes
# PyTorch's cmake call find_package(GTest) and alias the GTest:: targets to the
# bare names the test CMakeLists link against.
mv benchmark third_party

# benchmark's cmake uses try_run to detect regex backend, which fails
# in this build environment.  Predefine HAVE_STD_REGEX so the
# cxx_feature_check macro skips the probe and uses std::regex.
# Also enable position-independent code: the vendored benchmark static
# library must be compiled with -fPIE so it can be linked into PIE
# test executables (we pass -pie in CMAKE_EXE_LINKER_FLAGS).
sed -i '/cmake_minimum_required/a\set(HAVE_STD_REGEX 1)\nset(CMAKE_POSITION_INDEPENDENT_CODE ON)' third_party/benchmark/CMakeLists.txt
%endif

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

%generate_buildrequires
# -R: only the wheel's build-backend deps (the stripped [build-system].requires);
# skip torch's large runtime requirement set -- those are the static Requires and
# the extras, not build dependencies.  Overrides the BuildSystem's default
# %%pyproject_buildrequires, which runs with --generate-extras and would emit
# unsatisfiable optional-extra deps.
%pyproject_buildrequires -R

%build -p
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

# Opt into the CBLAS complex-dot path (2001-force-cblas-complex-dot-for-openblas.patch).
# Without this ATen's BLAS
# ABI probe leaves AT_BLAS_USE_CBLAS_DOT=0 and torch.dot()/torch.vdot() on
# complex tensors return 0.
export PYTORCH_BLAS_USE_CBLAS_DOT=ON

%install -p
%if %{with rocm}
export USE_ROCM=ON
export USE_ROCM_CK=OFF
export HIP_PATH=`hipconfig -p`
export ROCM_PATH=`hipconfig -R`

# pytorch uses clang, not hipcc
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
%endif

%check -a
%if %{with test}
# The declarative import check (BuildOption(check)) only proves modules load.
# Additionally run a small functional smoke (Source11) against the just-built
# tree: real matmul, autograd, a training step, and a guard that complex
# torch.dot/torch.vdot do not collapse to 0 (the CBLAS complex-dot path forced
# on by 2001-force-cblas-complex-dot-for-openblas.patch).  Other distros do
# not run PyTorch's own test/*.py suite at
# build time either; a smoke is enough to catch a numerically broken build.
PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}" \
PYTHONDONTWRITEBYTECODE=1 \
%{__python3} -sP %{SOURCE11}
%endif

%files -f %{pyproject_files}
%license LICENSE
%doc README.md
# torchrun is a console_scripts entry point; %%pyproject_save_files captures the
# importable modules under sitearch but not the bindir wrapper, so list it here.
%{_bindir}/torchrun

%changelog
%autochangelog
