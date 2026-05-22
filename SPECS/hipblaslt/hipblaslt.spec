# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define python_exec python3

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# hipBLASLt uses hipcc-based compilation via Tensile
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

# Fortran is only used in testing
%global build_fflags %{nil}

# Reduce link memory pressure
%global _lto_cflags %{nil}

# Parallelism is set dynamically in %build based on available memory/cores
%global _smp_mflags %{nil}

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

# Use system nanobind (if available) or bundled
%bcond nanobind 0
%global tensile_version 4.33.0
%global tensile_verbose 1
%global nanobind_version 2.9.2
%global nanobind_giturl https://github.com/wjakob/nanobind
%global robinmap_version 1.3.0
%global robinmap_giturl https://github.com/Tessil/robin-map

%global gpu_list %{rocm_gpu_list_default}

Name:           hipblaslt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm general matrix operations beyond BLAS
Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipBLASLt.git
License:        MIT AND BSD-3-Clause
#!RemoteAsset:  sha256:05d73038b1b4f66f3df4eb595b7cb0c8935f7aa18d0e07dbe5cc740a4b691898
Source:         %{url}/releases/download/rocm-%{version}/hipblaslt.tar.gz
Source1:        %{nanobind_giturl}/archive/v%{nanobind_version}/nanobind-%{nanobind_version}.tar.gz
Source2:        %{robinmap_giturl}/archive/v%{robinmap_version}/robin-map-%{robinmap_version}.tar.gz
Patch1:         0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
Patch2:         0001-hipblaslt-tensilelite-use-fedora-paths.patch
Patch3:         0001-hipblaslt-find-origami-package.patch
Patch4:         0001-hipblaslt-tensilelite-use-nanobind-tarball.patch
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
BuildRequires:  libzstd-devel
BuildRequires:  cmake(rocblas)
BuildRequires:  rocminfo
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm-origami)
BuildRequires:  rocm-smi-lib-devel
BuildRequires:  zlib-devel
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(msgpack)
BuildRequires:  msgpack-devel
BuildRequires:  blis-devel
BuildRequires:  lapack-devel
BuildRequires:  ninja
%if %{with test}
BuildRequires:  gmock-devel
BuildRequires:  gtest-devel
%endif
%if %{with nanobind}
BuildRequires:  python3dist(nanobind)
%endif

Provides:       bundled(python-tensile) = %{tensile_version}
%if %{without nanobind}
Provides:       bundled(nanobind) = %{nanobind_version}
Provides:       bundled(robin-map) = %{robinmap_version}
%endif

%description
hipBLASLt is a library that provides general matrix-matrix operations with a
flexible API and extends the functionalities of hipBLAS with the support of
working with more general matrix data-types and function parameters.

%package devel
Summary:        The hipBLASLt development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The hipBLASLt development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n hipblaslt

# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g' \
    tensilelite/Tensile/cmake/TensileConfig.cmake

# defer to cmdline
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# Do not use virtualenv_install
sed -i -e 's@virtualenv_install@#virtualenv_install@' CMakeLists.txt

# Disable trying to download rocm-cmake
sed -i -e 's@if(NOT ROCmCMakeBuildTools_FOUND)@if(FALSE)@' cmake/dependencies.cmake

%if %{with nanobind}
# Disable download of nanobind
sed -i -e 's@FetchContent_MakeAvailable(nanobind)@find_package(nanobind)@' \
    tensilelite/rocisa/CMakeLists.txt
%else
# Use bundled nanobind
tar xf %{SOURCE1}
mv nanobind-* nanobind
cd nanobind
tar xf %{SOURCE2}
cp -r robin-map-*/* ext/robin_map/
cd ..
tar czf nanobind.tar.gz nanobind
%endif

# Disable OpenMP (HIPBLASLT_ENABLE_OPENMP=OFF but still referenced)
# https://github.com/ROCm/rocm-libraries/issues/3201
sed -i -e '/OpenMP::OpenMP_CXX/d' clients/CMakeLists.txt
sed -i -e '/omp/d'                clients/common/src/blis_interface.cpp
sed -i -e '/#include <omp.h>/d'   clients/common/include/testing_matmul.hpp
sed -i -e '/#include <omp.h>/d'   clients/common/include/hipblaslt_init.hpp
sed -i -e '/#include <omp.h>/d'   clients/common/src/cblas_interface.cpp

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/dependencies.cmake

# Replace all mentions of 'amdclang' with 'clang' in Tensile Python files
find tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%build
# Do a manual install instead of cmake's virtualenv
cd tensilelite
TL=$PWD

%python_exec setup.py install --root $TL
cd ..

export PATH=%{_prefix}/bin:$PATH
CLANG_PATH=`hipconfig --hipclangpath`
ROCM_CLANG=${CLANG_PATH}/clang
RESOURCE_DIR=`${ROCM_CLANG} -print-resource-dir`
export DEVICE_LIB_PATH=${RESOURCE_DIR}/amdgcn/bitcode
export TENSILE_ROCM_ASSEMBLER_PATH=${CLANG_PATH}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=${CLANG_PATH}/clang-offload-bundler

export PATH=${TL}/%{_bindir}:$PATH
export PYTHONPATH=${TL}%{python3_sitelib}:$PYTHONPATH
export Tensile_DIR=${TL}%{python3_sitelib}/Tensile

# Calculate compile/link parallelism based on available memory and cores
COMPILE_JOBS=`lscpu | grep 'Core(s)' | awk '{ print $4 }'`
if [ ${COMPILE_JOBS}x = x ]; then
    COMPILE_JOBS=1
fi
if [ ${COMPILE_JOBS} = 1 ]; then
    COMPILE_JOBS=`lscpu | grep '^CPU(s)' | awk '{ print $2 }'`
    if [ ${COMPILE_JOBS}x = x ]; then
        COMPILE_JOBS=4
    fi
fi
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
    -DGPU_TARGETS=%{gpu_list} \
    -DBLIS_INCLUDE_DIR=%{_includedir}/blis \
    -DBLIS_LIB=%{_libdir}/libblis.so \
    -DBUILD_CLIENTS_TESTS=%{build_test} \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DBUILD_VERBOSE=ON \
    -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang \
    -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_PREFIX_PATH=%{python3_sitelib}/nanobind \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DHIP_PLATFORM=amd \
    -DHIPBLASLT_ENABLE_CLIENT=%{build_test} \
    -DHIPBLASLT_ENABLE_MARKER=OFF \
    -DHIPBLASLT_ENABLE_OPENMP=OFF \
    -DHIPBLASLT_ENABLE_ROCROLLER=OFF \
    -DHIPBLASLT_ENABLE_SAMPLES=OFF \
    -DROCM_SYMLINK_LIBS=OFF \
    -DTensile_LIBRARY_FORMAT=msgpack \
    -DTensile_VERBOSE=%{tensile_verbose} \
    -DVIRTUALENV_BIN_DIR=%{_bindir} \
    -DHIPBLASLT_PARALLEL_COMPILE_JOBS=${COMPILE_JOBS} \
    -DHIPBLASLT_PARALLEL_LINK_JOBS=${JOBS} \
    %{nil}

%cmake_build

%install
%cmake_install
rm -f %{buildroot}%{_datadir}/doc/hipblaslt/LICENSE.md

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
