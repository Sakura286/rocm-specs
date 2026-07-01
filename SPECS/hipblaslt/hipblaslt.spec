# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

%global toolchain clang

%bcond build_test 0
%if %{with build_test}
%global cmake_test ON
%else
%global cmake_test OFF
%endif

%global tensile_version 4.33.0
# The upstream hipBLASTLt project has a hard fork of the python-tensile package
# The rocBLAS uses.  The two versions are incompatible.  It appears that the
# fork happened around version 4.33.0.  Unfortunately hipBLASLt can no longer be
# build without using this fork.
# https://github.com/ROCm/hipBLASLt/issues/535
# The problem with the fork has been raised here.
# https://github.com/ROCm/hipBLASLt/issues/908

%global tensile_verbose 1

Name:           hipblaslt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm general matrix operations beyond BLAS
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:72ad0a8db025c6d47397791a9fce5c80cde1b89fc830523d0b34e5138329de63
Source0:        %{url}/releases/download/rocm-%{version}/%{name}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{cmake_test}
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DHIPBLASLT_ENABLE_CLIENT=%{cmake_test}
BuildOption(conf):  -DHIPBLASLT_ENABLE_MARKER=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_OPENMP=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_ROCROLLER=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_SAMPLES=OFF
BuildOption(conf):  -DTensile_LIBRARY_FORMAT=msgpack
BuildOption(conf):  -DTensile_VERBOSE=%{tensile_verbose}
BuildOption(conf):  -DVIRTUALENV_BIN_DIR=%{_bindir}
BuildOption(conf):  -Dnanobind_ROOT=%(python3 -m nanobind --cmake_dir)
BuildOption(conf):  -G Ninja

# yappi is used in tensilelite to generate profiling data, we are not using that in the build
Patch0:         0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
# Patch from Fedora, change hard coded vendor paths
Patch1:         0001-hipblaslt-tensilelite-use-system-paths.patch
# https://github.com/ROCm/rocm-libraries/issues/2422
Patch2:         0001-hipblaslt-find-origami-package.patch
# use the distribution-provided nanobind instead of fetching/bundling it
Patch3:         2001-hipblaslt-tensilelite-use-system-nanobind.patch

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(msgpack)
BuildRequires:  cmake(origami)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  compiler-rt
BuildRequires:  gcc-fortran
BuildRequires:  hipcc
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
# https://github.com/ROCm/hipBLASLt/issues/1734
BuildRequires:  python3dist(msgpack)
# nanobind is used to build the rocisa native module (build-time only)
BuildRequires:  python3dist(nanobind)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocminfo

%if %{with build_test}
BuildRequires:  cmake(openblas)
BuildRequires:  cmake(GMock)
BuildRequires:  cmake(GTest)
%endif

%description
hipBLASLt is a library that provides general matrix-matrix
operations. It has a flexible API that extends functionalities
beyond a traditional BLAS library, such as adding flexibility
to matrix data layouts, input types, compute types, and
algorithmic implementations and heuristics.

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%if %{with build_test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep -a
# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g'            tensilelite/Tensile/cmake/TensileConfig.cmake

# defer to cmdline
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# Do not use virtualenv_install
sed -i -e 's@virtualenv_install@#virtualenv_install@'                          CMakeLists.txt

# Disable trying to download rocm-cmake
sed -i -e 's@if(NOT ROCmCMakeBuildTools_FOUND)@if(FALSE)@' cmake/dependencies.cmake

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

%build -p
# Do a manual install instead of cmake's virtualenv
cd tensilelite
TL=$PWD

python3 setup.py install --root $TL
cd ..

# Should not have to do this
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

%install -a
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

%if %{with build_test}
%files test
%{_bindir}/hipblaslt*
%{_bindir}/sequence.yaml
%endif

%changelog
%autochangelog
