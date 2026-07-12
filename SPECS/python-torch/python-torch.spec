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

# LibTorch and the installed native-test helpers live below Python's private
# module directory. Do not expose their SONAMEs as system-wide capabilities,
# and suppress only the matching in-package requirements.
%global torch_privlibs libaoti_custom_ops|libbackend_with_compiler|libc10|libc10_hip
%global torch_privlibs %{torch_privlibs}|libcaffe2_nvrtc|libjitbackend_test|libshm
%global torch_privlibs %{torch_privlibs}|libtorch|libtorch_cpu|libtorch_global_deps
%global torch_privlibs %{torch_privlibs}|libtorch_hip|libtorch_python|libtorchbind_test
%global __provides_exclude_from ^%{python3_sitearch}/torch/lib/.*\\.so$
%global __requires_exclude ^(%{torch_privlibs})\\.so

# Build the installed native-test payload. These tests are split from the
# runtime package and are intended for post-install checks on suitable hosts.
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
# This is upstream's PEP 639 expression for the installed distribution; the
# build prunes unused third-party trees before constructing the wheel.
License:        Apache-2.0 AND (Apache-2.0 WITH LLVM-exception) AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT
URL:            https://pytorch.org/
VCS:            git:https://github.com/pytorch/pytorch.git
# PyTorch publishes only wheels on PyPI.  The GitHub tag archive excludes
# submodules, but the official release asset includes the third_party C++
# sources needed for a distro source build.
#!RemoteAsset:  sha256:66614a19060f69cfd63cd0295f65a1241bd15df2fa65c60ae51066c11c2ce812
Source0:        https://github.com/pytorch/pytorch/releases/download/v%{version}/pytorch-v%{version}.tar.gz

# googletest is provided by the system gtest-devel (openRuyi package) when
# BUILD_TEST=ON; see 2004-use-system-googletest.patch.

# Functional smoke test for the just-built torch, run by the check phase.
Source1:        pytorch-smoke-test.py

BuildSystem:    pyproject
BuildOption(prep):  -n pytorch-v%{version}
# Save every importable torch* top-level (torch, torchgen, functorch) plus the
# torchrun entrypoint; -l records the PEP 639 license files in the generated
# manifest consumed by %%files -f %%{pyproject_files}.
BuildOption(install):  -l '*torch*'
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
# ZLIB::ZLIBSTATIC target referencing %%{_libdir}/libz.a; cmake configure aborts
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
BuildRequires:  python3dist(fsspec)
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
BuildRequires:  amdsmi-devel
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel
%endif

Requires:       python3dist(dill)
Requires:       python3dist(pyyaml)
# torch links -fopenmp with the unversioned SONAME libomp.so; the auto-generated
# soname dep is satisfied by bare libomp22/libomp23 whose real runtime lives
# outside the loader path, so require the llvm-defaults libomp symlink package
# explicitly (our fixed rebuild wins in-project; see SPECS/llvm-defaults).
Requires:       libomp
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

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%if %{with test}
%package test
Summary:        Installed native test payload for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
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
# Use the system fmt instead of vendored third_party/fmt.
2006-use-system-fmt.patch
# Skip PreBuildSteps.cmake submodule sanity checks for vendored directories the
# openRuyi build intentionally prunes because system libraries or disabled
# features are used.
2007-skip-unused-submodule-prebuild-checks.patch
# Work around a system llvm22 AMDGPU SelectionDAG codegen bug: Loss.hip
# miscompiles for gfx11xx (S_ADD_U64_PSEUDO reaches MC unexpanded; reproduces at
# -O3 and -O1 alike).  Build only that one TU at -O0, switching it to GlobalISel.
# ROCm-only (the changed block is inside if(USE_ROCM)); no-op for cpu.
2008-loss-hip-O0-workaround-llvm22-codegen.patch
# Use satisfiable distro build-backend requirements while preserving PEP 639.
2009-use-system-pyproject-build-dependencies.patch
# Use packaged concurrentqueue and link the ROCm RSMI dependency.
2010-use-system-cmake-dependencies.patch
# Adapt shared CUDA/HIP declarations to the ROCm 7.2 clang ABI.
2011-fix-rocm-compatibility.patch
# Configure bundled benchmark for the non-executable OBS probe environment.
2012-configure-benchmark-for-obs.patch

%description
PyTorch is a Python package that provides two high-level features:

 * Tensor computation (like NumPy) with strong GPU acceleration
 * Deep neural networks built on a tape-based autograd system

You can reuse your favorite Python packages such as NumPy, SciPy,
and Cython to extend PyTorch when needed.

%description devel
Headers and CMake metadata for building C++ and HIP extensions against the
matching %{name} runtime.

%if %{with test}
%description test
Native test programs, helper libraries, and fixtures for post-install
validation of %{name}. This is not the complete upstream Python test suite.
%endif

%prep -a

# GitHub release tarballs identify the version as an alpha, so replace that
echo "%{version}" > version.txt

# Remove bundled egg-info
rm -rf %{srcname}.egg-info

# GPU-arch / default-BLAS-backend handling is done in
# 2003-default-to-hipblaslt-on-gfx1100.patch.  The arch
# lists moved from Blas.cpp to CUDAHooks.cpp in torch 2.11, so the old in-place
# seds here silently became no-ops; a patch fails the build loudly if upstream
# moves them again.

# %%pyproject_buildrequires (run by BuildSystem: pyproject) turns pyproject.toml's
# build-system.requires into RPM BuildRequires.  On openRuyi cmake/ninja are
# system packages, not python3dist(...); requests/six are not needed for the
# --no-build-isolation wheel build; and setuptools<82 conflicts with the distro's
# 82.x.  Drop those from the [build-system] table (only there, not the identical
# [dependency-groups] copy) so only satisfiable backend deps are generated -- the
# real build deps come from the static BuildRequires above.
# Applied by 2009-use-system-pyproject-build-dependencies.patch.

# System CMake dependencies and fmt compatibility are applied by patches 2006
# and 2010. The other historical edits in this block no longer match 2.13.0 or
# are disabled by the configured feature set, so they have been removed.

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

# Benchmark configuration is applied by patch 2012.
%endif

# Fake out pocketfft, and system header will be used
mkdir third_party/pocketfft
cp %{_includedir}/pocketfft_hdronly.h third_party/pocketfft/

# Use the system valgrind headers
mkdir third_party/valgrind-headers
cp %{_includedir}/valgrind/* third_party/valgrind-headers

%if %{with rocm}
# Patch 2011 fixes the HIP occupancy API gate and the clang CUDABlas template
# mangling mismatch before this hipify step.
./tools/amd_build/build_amd.py
%endif

%generate_buildrequires
# -R: only the wheel's build-backend deps (the stripped [build-system].requires);
# skip torch's large runtime requirement set -- those are the static Requires and
# the extras, not build dependencies.  Overrides the BuildSystem's default
# %%pyproject_buildrequires, which runs with --generate-extras and would emit
# unsatisfiable optional-extra deps.
export PYTORCH_BUILD_VERSION=%{version}
export PYTORCH_BUILD_NUMBER=1
%pyproject_buildrequires -R

%build -p
export PYTORCH_BUILD_VERSION=%{version}
export PYTORCH_BUILD_NUMBER=1
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

# The system clang used as the HIP device compiler does not auto-detect the
# rocm-device-libs bitcode, which lives in clang's own resource dir under
# amdgcn/bitcode.  Seed HIPFLAGS so both CMake's enable_language(HIP) compiler
# probe and the real device compile get --rocm-device-lib-path (CMAKE_HIP_FLAGS
# inherits HIPFLAGS via CMAKE_HIP_FLAGS_INIT); without it configure fails with
# "cannot find ROCm device library".
export HIPFLAGS="--rocm-device-lib-path=$(%{rocmllvm_bindir}/clang -print-resource-dir)/amdgcn/bitcode"

export CMAKE_NO_SYSTEM_FROM_IMPORTED=ON

# export CMAKE_BUILD_TYPE=Debug
%endif

export CMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES="%{_includedir}"
export CMAKE_C_IMPLICIT_INCLUDE_DIRECTORIES="%{_includedir}"

export LDFLAGS="-fuse-ld=lld %{build_ldflags}"
export CMAKE_LIBRARY_PATH=%{_libdir}
export CMAKE_PREFIX_PATH="%{_prefix}:%{_libdir}/cmake:%{python3_sitearch}"

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
export HIPFLAGS="--rocm-device-lib-path=$(%{rocmllvm_bindir}/clang -print-resource-dir)/amdgcn/bitcode"
%endif

%install -a
%if %{with rocm}
# On the HIP build, ProcessGroupGloo{,Async}Test link the libc10d_hip_test.so
# helper that the wheel does not install, leaving a dangling soname Requires
# that makes the package uninstallable; they cannot run without it, so drop
# them.  %%pyproject_save_files has already recorded them by name, so scrub the
# generated manifest as well or 'Processing files' fails on the missing paths.
rm -f %{buildroot}%{python3_sitearch}/torch/bin/ProcessGroupGlooTest \
      %{buildroot}%{python3_sitearch}/torch/bin/ProcessGroupGlooAsyncTest
# Anchor to the bin paths: the c10d ProcessGroupGloo*.hpp headers stay packaged.
sed -i '\#/torch/bin/ProcessGroupGlooTest$#d;\#/torch/bin/ProcessGroupGlooAsyncTest$#d' %{pyproject_files}
%endif

# Development SDK files belong to -devel, not the Python runtime package.
sed -i '\#%{python3_sitearch}/torch/include/#d;\#%{python3_sitearch}/torch/share/cmake/#d' \
    %{pyproject_files}

%if %{with test}
# Move the explicitly installed native tests and fixtures out of the runtime
# manifest. Keep torch/bin/torch_shm_manager in the runtime package.
sed -i \
    -e '\#%{python3_sitearch}/torch/bin/\(FileStoreTest\|HashStoreTest\|ProcessGroupGlooAsyncTest\|ProcessGroupGlooTest\|TCPStoreTest\|test_aoti_abi_check\|test_api\|test_cpp_rpc\|test_dist_autograd\|test_jit\|test_lazy\|test_shim\)$#d' \
    -e '\#%{python3_sitearch}/torch/bin/\(script_module_v4\.ptl\|test_interpreter_async\.pt\)$#d' \
    -e '\#%{python3_sitearch}/torch/bin/upgrader_models#d' \
    -e '\#%{python3_sitearch}/torch/lib/\(libaoti_custom_ops\|libbackend_with_compiler\|libjitbackend_test\|libtorchbind_test\)\.so$#d' \
    %{pyproject_files}
%endif

%check -a
%if %{with test}
# The declarative import check (BuildOption(check)) only proves modules load.
# Additionally run a small functional smoke (Source1) against the just-built
# tree: real matmul, autograd, a training step, and a guard that complex
# torch.dot/torch.vdot do not collapse to 0 (the CBLAS complex-dot path forced
# on by 2001-force-cblas-complex-dot-for-openblas.patch).  Other distros do
# not run PyTorch's own test/*.py suite at
# build time either; a smoke is enough to catch a numerically broken build.
PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}" \
PYTHONDONTWRITEBYTECODE=1 \
%{__python3} -sP %{SOURCE1}
%endif

%files -f %{pyproject_files}
%doc README.md NOTICE
# torchrun is a console_scripts entry point; %%pyproject_save_files captures the
# importable modules under sitearch but not the bindir wrapper, so list it here.
%{_bindir}/torchrun

%files devel
%{python3_sitearch}/torch/include/
%{python3_sitearch}/torch/share/cmake/

%if %{with test}
%files test
%{python3_sitearch}/torch/bin/FileStoreTest
%{python3_sitearch}/torch/bin/HashStoreTest
%if %{without rocm}
%{python3_sitearch}/torch/bin/ProcessGroupGlooAsyncTest
%{python3_sitearch}/torch/bin/ProcessGroupGlooTest
%endif
%{python3_sitearch}/torch/bin/TCPStoreTest
%{python3_sitearch}/torch/bin/script_module_v4.ptl
%{python3_sitearch}/torch/bin/test_aoti_abi_check
%{python3_sitearch}/torch/bin/test_api
%{python3_sitearch}/torch/bin/test_cpp_rpc
%{python3_sitearch}/torch/bin/test_dist_autograd
%{python3_sitearch}/torch/bin/test_interpreter_async.pt
%{python3_sitearch}/torch/bin/test_jit
%{python3_sitearch}/torch/bin/test_lazy
%{python3_sitearch}/torch/bin/test_shim
%{python3_sitearch}/torch/bin/upgrader_models/
%{python3_sitearch}/torch/lib/libaoti_custom_ops.so
%{python3_sitearch}/torch/lib/libbackend_with_compiler.so
%{python3_sitearch}/torch/lib/libjitbackend_test.so
%{python3_sitearch}/torch/lib/libtorchbind_test.so
%endif

%changelog
%autochangelog
