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

%global tensile_version 4.33.0
%global tensile_verbose 1

%bcond build_test 0
%if %{with build_test}
%global cmake_test ON
%else
%global cmake_test OFF
%endif

Name:           hipsparselt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A SPARSE marshaling library
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:9ebd347b9b0fab350ce48c27aa848fe8f99c8b743ecf5213965618fa4f9a25ba
Source0:        %{url}/releases/download/rocm-%{version}/%{name}.tar.gz
#!RemoteAsset:  sha256:72ad0a8db025c6d47397791a9fce5c80cde1b89fc830523d0b34e5138329de63
Source1:        %{url}/releases/download/rocm-%{version}/hipblaslt.tar.gz
# Patches for hipBLASLt's tensilelite (applied during prep inside hipBLASLt/)
Source2:        0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
Source3:        0001-hipblaslt-tensilelite-use-system-paths.patch
Source4:        0001-hipblaslt-find-origami-package.patch
BuildSystem:    cmake

BuildOption(conf):  -DBLAS_INCLUDE_DIR=%{_includedir}/flexiblas
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{cmake_test}
BuildOption(conf):  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF
BuildOption(conf):  -DBUILD_VERBOSE=ON
BuildOption(conf):  -DCMAKE_Fortran_COMPILER=gcc-fortran
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DTensile_COMPILER=clang++
BuildOption(conf):  -DTensile_LIBRARY_FORMAT=msgpack
BuildOption(conf):  -DTensile_VERBOSE=%{tensile_verbose}
BuildOption(conf):  -DVIRTUALENV_BIN_DIR=%{_bindir}
BuildOption(conf):  -Dnanobind_ROOT=%(python3 -m nanobind --cmake_dir)
BuildOption(conf):  -G Ninja

BuildRequires:  clang22
BuildRequires:  clang22-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(origami)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  cmake(rocsparse)
BuildRequires:  compiler-rt22
BuildRequires:  gcc-fortran
BuildRequires:  lld22
BuildRequires:  llvm22
BuildRequires:  ninja
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(msgpack)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(msgpack)
# nanobind is used to build the rocisa native module (build-time only)
BuildRequires:  python3dist(nanobind)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(setuptools)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocminfo
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel

%if %{with build_test}
BuildRequires:  chrpath
BuildRequires:  pkgconfig(openblas)
BuildRequires:  pkgconfig(gtest)
BuildRequires:  pkgconfig(gmock)
%endif

%description
hipSPARSELt is a SPARSE marshaling library that provides general sparse
matrix-matrix multiplication using structured sparsity. It offers a flexible
API and supports multiple backends.

%package        devel
Summary:        The hipSPARSELt development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The hipSPARSELt development package.

%if %{with build_test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep
%autosetup -p1 -n %{name}

tar xf %{SOURCE1}
cd hipblaslt

patch -p1 < %{SOURCE2}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g' \
    tensilelite/Tensile/cmake/TensileConfig.cmake

# Make sure hip/hip_runtime.h is found
sed -i -e 's@-x hip @-I%{_includedir} -x hip @' device-library/matrix-transform/CMakeLists.txt
sed -i -e 's@"-D__HIP_HCC_COMPAT_MODE__=1"@"-D__HIP_HCC_COMPAT_MODE__=1","-I%{_includedir}"@' \
    tensilelite/Tensile/Toolchain/Component.py

# Use the distribution-provided nanobind instead of fetching/bundling it
sed -i -e 's@FetchContent_MakeAvailable(nanobind)@find_package(nanobind CONFIG REQUIRED)@' \
    tensilelite/rocisa/CMakeLists.txt

# disable openmp in hipBLASLt
sed -i -e 's@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." ON)@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." OFF)@' CMakeLists.txt

cd ..

# Point hipBLASLt path at the bundled in-source copy (default looks in ../hipblaslt)
sed -i -e 's@${CMAKE_CURRENT_SOURCE_DIR}/../hipblaslt@${CMAKE_CURRENT_SOURCE_DIR}/hipblaslt@' CMakeLists.txt

# Prevent the virtualenv install from cmake
sed -i -e 's@virtualenv_install@#virtualenv_install@' CMakeLists.txt

# Unforce the setting of libdir
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# Change looking for cblas to flexiblas
sed -i -e 's@find_package( cblas REQUIRED CONFIG )@#find_package( cblas REQUIRED CONFIG )@' clients/CMakeLists.txt
sed -i -e 's@set( BLAS_LIBRARY "blas" )@set( BLAS_LIBRARY "flexiblas" )@' clients/CMakeLists.txt
sed -i -e 's@lapack cblas@flexiblas@' clients/gtest/CMakeLists.txt

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' hipblaslt/cmake/dependencies.cmake
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/Dependencies.cmake

# Replace all mentions of 'amdclang' with 'clang' in Tensile Python files
find hipblaslt/tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%build -p
# Do a manual install of tensilelite instead of cmake's virtualenv, then point
# Tensile at it for build-time kernel generation (same approach as hipblaslt)
cd hipblaslt/tensilelite
TL=$PWD
python3 setup.py install --root $TL
cd ../..

export PATH=%{_prefix}/bin:%{rocmllvm_bindir}:$PATH
CLANG_PATH=`hipconfig --hipclangpath`
ROCM_CLANG=${CLANG_PATH}/clang
RESOURCE_DIR=`${ROCM_CLANG} -print-resource-dir`
export DEVICE_LIB_PATH=${RESOURCE_DIR}/amdgcn/bitcode
export TENSILE_ROCM_ASSEMBLER_PATH=${CLANG_PATH}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=${CLANG_PATH}/clang-offload-bundler
export PATH=${TL}/%{_bindir}:$PATH
export PYTHONPATH=${TL}%{python3_sitelib}:$PYTHONPATH
export Tensile_DIR=${TL}%{python3_sitelib}/Tensile

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsparselt/LICENSE.md

# Strip and fix permissions on hsaco kernel files
%{rocmllvm_bindir}/llvm-strip %{buildroot}%{_libdir}/hipsparselt/library/Kernels*.hsaco
chmod a+x %{buildroot}%{_libdir}/hipsparselt/library/Kernels*.hsaco

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsparselt.so.*
%{_libdir}/hipsparselt/

%files devel
%{_includedir}/hipsparselt/
%{_libdir}/cmake/hipsparselt/
%{_libdir}/libhipsparselt.so

%if %{with build_test}
%files test
%{_bindir}/hipsparselt*
%endif

%changelog
%autochangelog
