%global upstreamname RCCL
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}/
%global pkg_suffix -%{rocm_release}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%endif
%global rccl_name rccl%{pkg_suffix}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-flto=thin//' -e 's/-flto=auto//' -e 's/-ffat-lto-objects//' -e 's/-mtls-dialect=gnu2//')

%global _lto_cflags %{nil}

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# downloads tests, use mock --enable-network
%bcond test 0
%if %{with test}
%global build_test ON
%global __brp_check_rpaths %{nil}
%else
%global build_test OFF
%endif

%bcond export 0
%if %{with export}
%global build_compile_db ON
%else
%global build_compile_db OFF
%endif

# rccl is not supported on gfx1103
# On 6.1.1
# lld: error: ld-temp.o <inline asm>:1:25: specified hardware register is not supported on this GPU
#        s_getreg_b32 s1, hwreg(HW_REG_HW_ID)
#
# On 6.2
# Problems reported with gfx10, removing gfx10 and default (gfx10 and gfx11) from build list
#
%global gpu_list %{rocm_gpu_list_rccl}
%global _gpu_list gfx1100

Name:           %{rccl_name}
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        ROCm Communication Collectives Library

Url:            https://github.com/ROCm/rccl
License:        BSD-3-Clause AND MIT AND Apache-2.0
# From License.txt the main license is BSD 3
# Modifications from Microsoft is MIT
# The NVIDIA based header files below are Apache-2.0
#  src/include/nvtx3/nv*.h and similar
# The URL for NVIDIA in the License.txt https://github.com/NVIDIA/NVTX is Apache-2.0

Source0:        %{url}/archive/rocm-%{rocm_version}.tar.gz#/%{upstreamname}-%{rocm_version}.tar.gz

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  hipcc
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  cmake
BuildRequires:  hipify%{pkg_suffix}
BuildRequires:  gcc-c++
BuildRequires:  fmt-devel
BuildRequires:  python3
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-core%{pkg_suffix}-devel
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
BuildRequires:  rocm-smi%{pkg_suffix}-devel

%if %{with test}
BuildRequires:  gtest-devel
%endif

Requires:       %{name}-data = %{version}-%{release}
Provides:       rccl%{pkg_suffix} = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
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

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%package devel
Summary:        Headers and libraries for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       rccl%{pkg_suffix}-devel = %{version}-%{release}

%description devel
Headers and libraries for %{name}

%package data
Summary:        Data for %{name}
BuildArch:      noarch

%description data
Data for %{name}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n rccl-rocm-%{version}

# Allow user to set AMDGPU_TARGETS
sed -i -e '/AMD GPU targets to compile for/d' CMakeLists.txt

# No /opt/rocm/.info/version
sed -i -e 's@cat ${ROCM_PATH}/.info/version@echo %{rocm_version}@' CMakeLists.txt

# Problems building on SUSE
# ENABLE_MSCCLPP=OFF
sed -i -e 's@if (ENABLE_MSCCLPP AND NOT(${HOST_OS_ID} STREQUAL "ubuntu" OR ${HOST_OS_ID} STREQUAL "centos"))@if (ENABLE_MSCCLPP)@' CMakeLists.txt

# Building --with test
# .../test/common/TestBed.cpp:607:16: error: no member named 'setfill' in namespace 'std'
#   607 |     ss << std::setfill(' ') << std::setw(20) << ncclFuncNames[funcType] << " ";
# https://github.com/ROCm/rccl/issues/1749
sed -i '/#include <map.*/a#include <iomanip>' test/common/TestBed.hpp

# On Tumbleweed Q3,2025
# /usr/include/gtest/internal/gtest-port.h:273:2: error: C++ versions less than C++17 are not supported.
# Convert the c++14 to c++17
sed -i -e 's@set(CMAKE_CXX_STANDARD   14)@set(CMAKE_CXX_STANDARD 17)@' CMakeLists.txt

# Do not force install
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' cmake/Dependencies.cmake

# RCCL uses -parallel-jobs for both compiling and linking
# compiling is set to 12, which may be more than the cores on the build machine.
# linking is set by reserving 16GB pre thread, can be too little.
# Use our own heuristics here
# Real cores, No hyperthreading
COMPILE_JOBS=`cat /proc/cpuinfo | grep -m 1 'cpu cores' | awk '{ print $4 }'`
if [ ${COMPILE_JOBS}x = x ]; then
    COMPILE_JOBS=1
fi
# Try again..
if [ ${COMPILE_JOBS} = 1 ]; then
    COMPILE_JOBS=`lscpu | grep '^CPU(s)' | awk '{ print $2 }'`
    if [ ${COMPILE_JOBS}x = x ]; then
        COMPILE_JOBS=4
    fi
fi

# Take into account memmory usage per core, do not thrash real memory
# inflate this to prevent competing with normal compile jobs
BUILD_MEM=16
MEM_KB=0
MEM_KB=`cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'`
MEM_MB=`eval "expr ${MEM_KB} / 1024"`
MEM_GB=`eval "expr ${MEM_MB} / 1024"`
COMPILE_JOBS_MEM=`eval "expr 1 + ${MEM_GB} / ${BUILD_MEM}"`
if [ "$COMPILE_JOBS_MEM" -lt "$COMPILE_JOBS" ]; then
    COMPILE_JOBS=$COMPILE_JOBS_MEM
fi
LINK_MEM=65
LINK_JOBS=`eval "expr 1 + ${MEM_GB} / ${LINK_MEM}"`

sed -i -e "s@rccl PRIVATE -parallel-jobs=12@rccl PRIVATE -parallel-jobs=${COMPILE_JOBS}@" CMakeLists.txt
sed -i -e "s@-parallel-jobs=\${num_linker_jobs}@-parallel-jobs=${LINK_JOBS}@" CMakeLists.txt

%build
%cmake \
    -DGPU_TARGETS=%{gpu_list} \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DBUILD_TESTS=%{build_test} \
    -DCMAKE_BUILD_TYPE=%{build_type} \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=%{build_compile_db} \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
    -DCMAKE_SKIP_RPATH=ON \
    -DENABLE_MSCCLPP=OFF \
    -DEXPLICIT_ROCM_VERSION=%{rocm_version} \
    -DHIP_PLATFORM=amd \
    -DRCCL_ROCPROFILER_REGISTER=OFF \
    -DROCM_PATH=%{pkg_prefix} \
    -DROCM_SYMLINK_LIBS=OFF

(while true; do echo "[heartbeat] $(date) - build still running..."; sleep 300; done) &
HEARTBEAT_PID=$!

%cmake_build

kill $HEARTBEAT_PID 2>/dev/null || true

%install
%cmake_install

rm -f %{buildroot}%{pkg_prefix}/share/doc/rccl/LICENSE.txt

%files
%license LICENSE.txt
%{pkg_prefix}/%{pkg_libdir}/librccl.so.*
%{pkg_prefix}/bin/rcclras

%files data
%{pkg_prefix}/share/rccl/msccl-algorithms/
%{pkg_prefix}/share/rccl/msccl-unit-test-algorithms/

%files devel
%doc README.md
%{pkg_prefix}/include/rccl/
%{pkg_prefix}/%{pkg_libdir}/cmake/rccl/
%{pkg_prefix}/%{pkg_libdir}/librccl.so

%if %{with test}
%files test
%{pkg_prefix}/bin/rccl-UnitTests
%endif

%changelog
* Mon Jan 26 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
