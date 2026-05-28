# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define python_exec python3

%global upstreamname hipblaslt
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

# Fortran is only used in testing
# clang and gfortran fedora toolchain args do not mix
%global build_fflags %{nil}

# Reduce link memory pressure
%global _lto_cflags %{nil}

# may run out of memory for both compile and link
# Calculate a good -j number below
%global _smp_mflags %{nil}

# gfx90a: 10343 pass, 152 fail
%bcond test 0
# Disable rpatch checks for a local build
%if %{with test}
%global __brp_check_rpaths %{nil}
%global build_test ON
%else
%global build_test OFF
%endif

%global tensile_version 4.33.0
# The upstream hipBLASTLt project has a hard fork of the python-tensile package
# The rocBLAS uses.  The two versions are incompatible.  It appears that the
# fork happened around version 4.33.0.  Unfortunately hipBLASLt can no longer be
# build without using this fork.
# https://github.com/ROCm/hipBLASLt/issues/535
# The problem with the fork has been raised here.
# https://github.com/ROCm/hipBLASLt/issues/908

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

%global tensile_verbose 1

%global nanobind_version 2.9.2
%global nanobind_giturl https://github.com/wjakob/nanobind
%global robinmap_version 1.3.0
%global robinmap_giturl https://github.com/Tessil/robin-map

Name:           hipblaslt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm general matrix operations beyond BLAS
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipBLASLt.git
#!RemoteAsset:  sha256:05d73038b1b4f66f3df4eb595b7cb0c8935f7aa18d0e07dbe5cc740a4b691898
Source:         %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz

Source1:        %{nanobind_giturl}/archive/v%{nanobind_version}/nanobind-%{nanobind_version}.tar.gz
Source2:        %{robinmap_giturl}/archive/v%{robinmap_version}/robin-map-%{robinmap_version}.tar.gz

# yappi is used in tensilelite to generate profiling data, we are not using that in the build
Patch1:         0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
# change hard coded vendor paths to fedoras
Patch2:         0001-hipblaslt-tensilelite-use-fedora-paths.patch
# https://github.com/ROCm/rocm-libraries/issues/2422
Patch3:         0001-hipblaslt-find-origami-package.patch
# do not try to fetch, point to the nanobind tarball
Patch4:         0001-hipblaslt-tensilelite-use-nanobind-tarball.patch
# compile and link jobpools
Patch5:         0001-hipblaslt-cmake-compile-and-link-pools.patch

BuildRequires:  llvm
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  lld
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  gcc-fortran
BuildRequires:  cmake(hipblas)
BuildRequires:  hipcc
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  cmake(rocblas)
BuildRequires:  rocminfo
BuildRequires:  rocm-cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-llvm-macros
BuildRequires:  cmake(hip)
BuildRequires:  cmake(origami)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  ninja

# For tensilelite
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
# https://github.com/ROCm/hipBLASLt/issues/1734
BuildRequires:  python3dist(msgpack)
BuildRequires:  msgpack-devel

%if %{with test}
BuildRequires:  blis-devel
BuildRequires:  lapack-devel
BuildRequires:  cmake(GMock)
BuildRequires:  cmake(GTest)
%endif

Provides:       bundled(python-tensile) = %{tensile_version}
Provides:       bundled(nanobind) = %{nanobind_version}
Provides:       bundled(robin-map) = %{robinmap_version}

%description
hipBLASLt is a library that provides general matrix-matrix
operations. It has a flexible API that extends functionalities
beyond a traditional BLAS library, such as adding flexibility
to matrix data layouts, input types, compute types, and
algorithmic implementations and heuristics.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n %{upstreamname}

# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g'            tensilelite/Tensile/cmake/TensileConfig.cmake

# defer to cmdline
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# Do not use virtualenv_install
sed -i -e 's@virtualenv_install@#virtualenv_install@'                          CMakeLists.txt

# Disable trying to download rocm-cmake
sed -i -e 's@if(NOT ROCmCMakeBuildTools_FOUND)@if(FALSE)@' cmake/dependencies.cmake

# Use bundled nanobind
tar xf %{SOURCE1}
mv nanobind-* nanobind
cd nanobind
tar xf %{SOURCE2}
cp -r robin-map-*/* ext/robin_map/
cd ..
tar czf nanobind.tar.gz nanobind

# As of 6.4, there is a long poll
# compile_code_object.sh gfx90a,gfx1100,gfx1101,gfx1151,gfx1200,gfx1201 RelWithDebInfo sha1 hipblasltTransform.hsaco
# This compiles a large file with multiple gpus.
GPUS=`echo %{rocm_gpu_list_default} | grep -o 'gfx' | wc -l`

HIP_JOBS=`lscpu | grep 'Core(s)' | awk '{ print $4 }'`
if [ ${HIP_JOBS}x = x ]; then
    HIP_JOBS=1
fi
# Try again..
if [ ${HIP_JOBS} = 1 ]; then
    HIP_JOBS=`lscpu | grep '^CPU(s)' | awk '{ print $2 }'`
    if [ ${HIP_JOBS}x = x ]; then
        HIP_JOBS=4
    fi
fi
if [ "$GPUS" -lt "$HIP_JOBS" ]; then
    HIP_JOBS=$GPUS
fi

# HIPBLASLT_ENABLE_OPENMP is OFF yet it is still being used
# https://github.com/ROCm/rocm-libraries/issues/3201
sed -i -e '/OpenMP::OpenMP_CXX/d' clients/CMakeLists.txt
sed -i -e '/omp/d'                clients/common/src/blis_interface.cpp
sed -i -e '/#include <omp.h>/d'   clients/common/include/testing_matmul.hpp
sed -i -e '/#include <omp.h>/d'   clients/common/include/hipblaslt_init.hpp
sed -i -e '/#include <omp.h>/d'   clients/common/src/cblas_interface.cpp

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/dependencies.cmake

# Forcefully replace all mentions of 'amdclang' with 'clang' in the Tensile Python files
find tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%build

# Do a manual install instead of cmake's virtualenv
cd tensilelite
TL=$PWD

%python_exec setup.py install --root $TL
cd ..

# Should not have to do this
export PATH=%{_prefix}/bin:$PATH
CLANG_PATH=`hipconfig --hipclangpath`
ROCM_CLANG=${CLANG_PATH}/clang
RESOURCE_DIR=`${ROCM_CLANG} -print-resource-dir`
export DEVICE_LIB_PATH=${RESOURCE_DIR}/amdgcn/bitcode
export TENSILE_ROCM_ASSEMBLER_PATH=${CLANG_PATH}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=${CLANG_PATH}/clang-offload-bundler

# Look for the just built tensilelite
export PATH=${TL}/%{_bindir}:$PATH
export PYTHONPATH=${TL}%{python3_sitelib}:$PYTHONPATH
export Tensile_DIR=${TL}%{python3_sitelib}/Tensile

cat /proc/cpuinfo
cat /proc/meminfo
lscpu

# Real cores, No hyperthreading
COMPILE_JOBS=`lscpu | grep 'Core(s)' | awk '{ print $4 }'`
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
BUILD_MEM=8
MEM_KB=0
MEM_KB=`cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'`
MEM_MB=`eval "expr ${MEM_KB} / 1024"`
MEM_GB=`eval "expr ${MEM_MB} / 1024"`
COMPILE_JOBS_MEM=`eval "expr 1 + ${MEM_GB} / ${BUILD_MEM}"`
if [ "$COMPILE_JOBS_MEM" -lt "$COMPILE_JOBS" ]; then
    COMPILE_JOBS=$COMPILE_JOBS_MEM
fi
LINK_MEM=32
LINK_JOBS=`eval "expr 1 + ${MEM_GB} / ${LINK_MEM}"`
JOBS=${COMPILE_JOBS}
if [ "$LINK_JOBS" -lt "$JOBS" ]; then
    JOBS=$LINK_JOBS
fi

%cmake -G Ninja \
       -DGPU_TARGETS=%{rocm_gpu_list_default} \
       -DBUILD_CLIENTS_TESTS=%{build_test} \
       -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang \
       -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ \
       -DCMAKE_INSTALL_LIBDIR=%{_lib} \
       -DCMAKE_INSTALL_PREFIX=%{_prefix} \
       -DCMAKE_VERBOSE_MAKEFILE=ON \
       -DHIPBLASLT_ENABLE_CLIENT=%{build_test} \
       -DHIPBLASLT_ENABLE_MARKER=OFF \
       -DHIPBLASLT_ENABLE_OPENMP=OFF \
       -DHIPBLASLT_ENABLE_ROCROLLER=OFF \
       -DHIPBLASLT_ENABLE_SAMPLES=OFF \
       -DTensile_LIBRARY_FORMAT=msgpack \
       -DTensile_VERBOSE=%{tensile_verbose} \
       -DVIRTUALENV_BIN_DIR=%{_bindir} \
       -DHIPBLASLT_PARALLEL_COMPILE_JOBS=${COMPILE_JOBS} \
       -DHIPBLASLT_PARALLEL_LINK_JOBS=${LINK_JOBS} \
       %{nil}

%cmake_build

%install

%cmake_install

# Extra license
rm -f %{buildroot}%{_datadir}/doc/hipblaslt/LICENSE.md

%post  -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipblaslt.so.*
%{_libdir}/hipblaslt/

%files devel
%{_includedir}/hipblaslt/
%{_includedir}/hipblaslt-export.h
%{_includedir}/hipblaslt-version.h
%{_libdir}/cmake/hipblaslt/
%{_libdir}/libhipblaslt.so

%if %{with test}
%files test
%{_bindir}/hipblaslt*
%{_bindir}/sequence.yaml
%endif

%changelog
%autochangelog
