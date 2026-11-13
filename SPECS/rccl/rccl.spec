# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

# Linking AMD device libs code takes too much time
# Set --lto-partitions can accelerate, but even --lto-partitions=4 is killed for OOM on riscv64
%ifarch riscv64
%global lto_partitions 2
%else
%global lto_partitions %(nproc)
%endif

%ifarch x86_64 riscv64
# Large kernel builds need the 32-job workers on both validation architectures.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           rccl
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Communication Collectives Library
# From License.txt the main license is BSD 3
# Modifications from Microsoft is MIT
# The NVIDIA based header files below are Apache-2.0
#  src/include/nvtx3/nv*.h and similar
# The URL for NVIDIA in the License.txt https://github.com/NVIDIA/NVTX is Apache-2.0
License:        BSD-3-Clause AND MIT AND Apache-2.0
URL:            https://github.com/ROCm/rccl
#!RemoteAsset:  sha256:314d0a54e68217efb12eafd2aacd439d4928f443795c778711d846355d262355
Source0:        https://github.com/ROCm/rocm-systems/releases/download/therock-10.1/rccl.tar.gz
# https://github.com/ROCm/rocm-systems/commit/6305765daacadbbef27e921c1907f13674e71fbd
Patch0:         0001-upstream-generic-hip-gdr-read.patch
BuildSystem:    cmake

BuildOption(prep):  -n rccl

BuildOption(conf):  -G Ninja
# Offload bundle IDs require an explicit host environment component.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
%ifarch riscv64
# The native GCC directory omits the GNU environment required by offload IDs.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_ARG1="--gcc-triple=%{_target_platform} -resource-dir=$PWD/clang-resource"
%else
BuildOption(conf):  -DCMAKE_CXX_COMPILER_ARG1="-resource-dir=$PWD/clang-resource"
%endif
%ifarch riscv64
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu --gcc-triple=%{_target_platform} -resource-dir=$PWD/clang-resource"
%else
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu -resource-dir=$PWD/clang-resource"
%endif
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DEXPLICIT_ROCM_VERSION=%{version}
BuildOption(conf):  -DROCM_PATH=%{_prefix}
BuildOption(conf):  -DCMAKE_TRY_COMPILE_PLATFORM_VARIABLES=ROCM_PATH
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DBUILD_TESTS=ON
BuildOption(conf):  -DROCTX=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(fmt)
BuildRequires:  cmake(GTest)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(rocprofiler-register)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  hipify
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
# RCCL uses the ROCTX header path for its NVTX compatibility layer. Without
# the development package CMake silently selects conflicting NVTX stubs.
BuildRequires:  roctracer-devel >= %{rocm_version}

Requires:       %{name}-data = %{version}-%{release}

%global _description %{expand:
RCCL (pronounced "Rickle") is a stand-alone library of standard
collective communication routines for GPUs, implementing all-reduce,
all-gather, reduce, broadcast, reduce-scatter, gather, scatter, and
all-to-all. There is also initial support for direct GPU-to-GPU
send and receive operations. It has been optimized to achieve high
bandwidth on platforms using PCIe, xGMI as well as networking using
InfiniBand Verbs or TCP/IP sockets. RCCL supports an arbitrary
number of GPUs installed in a single node or multiple nodes, and
can be used in either single- or multi-process (e.g., MPI)
applications.

The collective operations are implemented using ring and tree
algorithms and have been optimized for throughput and latency. For
best performance, small operations can be either batched into
larger operations or aggregated through the API.
}

%description
%{_description}

%package        devel
Summary:        Headers and libraries for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       rccl-devel = %{version}-%{release}

%description    devel
Headers and libraries for %{name}

%package        data
Summary:        Data for %{name}
BuildArch:      noarch

%description    data
Data for %{name}

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%prep -a
# Keep ROCM_PATH as a CMake layout hint: exporting /usr makes Clang skip
# the versioned device-libs directory and invalidates HIP feature probes.
sed -i '/^set(ENV{ROCM_PATH} ${ROCM_PATH})$/d' CMakeLists.txt
# The standalone device-linker commands bypass CMAKE_CXX_COMPILER_TARGET.
# Keep their host bundle triple consistent with CMake's normal HIP commands.
sed -i 's@set(DL_HIP_COMPILER_FLAGS "")@set(DL_HIP_COMPILER_FLAGS "--target=%{_target_cpu}-openruyi-linux-gnu")@' cmake/DeviceLinker.cmake
%ifarch riscv64
sed -i '/^set(DL_HIP_COMPILER_FLAGS /a list(APPEND DL_HIP_COMPILER_FLAGS "--gcc-triple=%{_target_platform}")' cmake/DeviceLinker.cmake
%endif
# Do not force install
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' cmake/Dependencies.cmake
# -amdgpu-s-branch-bits and -amdgpu-long-branch-factor=2 are needed to avoid 'branch size exceed simm16' error
# --lto-partitions parallelizes the GPU LTO codegen (capped on riscv64, see lto_partitions above)
sed -i -e 's@target_link_options(rccl PRIVATE "SHELL:-Xoffload-linker -mllvm=-amdgpu-kernarg-preload-count=16")@target_link_options(rccl PRIVATE "SHELL:-Xoffload-linker -mllvm=-amdgpu-s-branch-bits=15" "SHELL:-Xoffload-linker -mllvm=-amdgpu-long-branch-factor=2" "SHELL:-Xoffload-linker -mllvm=-amdgpu-kernarg-preload-count=16" "SHELL:-Xoffload-linker --lto-partitions=%{lto_partitions}" "SHELL:-Xoffload-linker --verbose")@' CMakeLists.txt

%conf -p
# The explicit GNU host target uses the same native ABI, but compiler-rt is
# installed under the distribution triple without the environment suffix.
# Use Clang's resource-dir option with build-local aliases; retain builtins and
# coverage instrumentation without changing the system LLVM installation.
mkdir -p clang-resource/lib
ln -s %{_libdir}/llvm%{llvm_maj_ver}/lib/clang/%{llvm_maj_ver}/include clang-resource/include
ln -s %{_libdir}/llvm%{llvm_maj_ver}/lib/clang/%{llvm_maj_ver}/amdgcn clang-resource/amdgcn
ln -s %{_libdir}/llvm%{llvm_maj_ver}/lib/clang/%{llvm_maj_ver}/lib/%{_target_platform} clang-resource/lib/%{_target_platform}
ln -s %{_libdir}/llvm%{llvm_maj_ver}/lib/clang/%{llvm_maj_ver}/lib/%{_target_platform} clang-resource/lib/%{_target_cpu}-openruyi-linux-gnu
# Preserve compiler-probe diagnostics when configuration fails.
trap 'status=$?; if [ "$status" -ne 0 ]; then cat %{_vpath_builddir}/CMakeFiles/CMakeConfigureLog.yaml; fi; exit "$status"' EXIT
export PATH=%{rocmllvm_bindir}:$PATH

%build
%ifarch riscv64
# Prevent from being killed by build machine
timeout 20h bash -c 'while sleep 300; do echo "[heartbeat] $(date)"; done' & TIME_OUT=$!
%endif

%cmake_build

%ifarch riscv64
kill $TIME_OUT 2>/dev/null || true
%endif

%install -a
rm -f %{buildroot}%{_datadir}/doc/rccl/LICENSE.txt

%check
# Upstream marks these generator/telemetry checks as CPU-only. Micro-tests
# compile their units directly and satisfy HIP/device symbols with fakes.
ctest --test-dir %{_vpath_builddir} --output-on-failure \
    -R '^(rccl-generate-device-table|rccl-generate-ce-reduce|rccl-UnitTestsNetTelemetry)$'
LLVM_PROFILE_FILE="$PWD/rccl-micro-%%p.profraw" \
    %{_vpath_builddir}/test/host/rccl-UnitTestsMicro --gtest_brief=1

%files
%license LICENSE.txt
%{_libdir}/librccl.so.*
%{_bindir}/rcclras

%files data
%{_datadir}/rccl/tuner/

%files devel
%doc README.md
%{_includedir}/rccl/
%{_includedir}/nccl.h
%{_includedir}/nccl_device.h
%{_includedir}/nccl_device/
%{_libdir}/cmake/rccl/
%{_libdir}/librccl.so

%files test
%{_bindir}/rccl-UnitTests*
%{_bindir}/librccl-test-profiler-stub.so
%{_bindir}/rccl/

%changelog
%autochangelog
