# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define python_exec python3
%define python_expand python3

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# hipSPARSELt uses hipcc-based compilation via Tensile from hipBLASLt
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

# The tensilelite that hipSPARSELt uses comes from hipBLASLt
# This is the hipblaslt 7.1.1 repo tag commit
%global hipblaslt_commit 7c0ea90bd75ec971502a9232373f8ae7484a5cfa
%global hipblaslt_scommit %(c=%{hipblaslt_commit}; echo ${c:0:7})

%global tensile_version 4.33.0
%global tensile_verbose 1
%global tensile_library_format msgpack
%global nanobind_version 2.9.2
%global nanobind_giturl https://github.com/wjakob/nanobind
%global robinmap_version 1.3.0
%global robinmap_giturl https://github.com/Tessil/robin-map

# Use system nanobind (if available) or bundled
%bcond nanobind 0

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global gpu_list %{rocm_gpu_list_default}

Name:           hipsparselt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A SPARSE marshaling library
Url:            https://github.com/ROCm/hipSPARSELt
VCS:            git:https://github.com/ROCm/hipSPARSELt.git
License:        MIT
#!RemoteAsset:  sha256:31047a7187c128cf85fdbd822ba057ab1f9ae2f5ceceb230ca428042a96e24d4
Source:         %{url}/archive/rocm-%{version}.tar.gz
Source1:        https://github.com/ROCm/hipBLASLt/archive/%{hipblaslt_commit}/hipBLASLt-%{hipblaslt_scommit}.tar.gz
# Patches for hipBLASLt's tensilelite (applied during prep inside hipBLASLt/)
Source2:        0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
Source3:        0001-hipblaslt-tensilelite-use-fedora-paths.patch
Source4:        0001-hipblaslt-find-origami-package.patch
Source5:        0001-hipblaslt-tensilelite-use-nanobind-tarball.patch
Source6:        0001-hipblaslt-tensilelite-use-clang.patch
Source10:       %{nanobind_giturl}/archive/v%{nanobind_version}/nanobind-%{nanobind_version}.tar.gz
Source11:       %{robinmap_giturl}/archive/v%{robinmap_version}/robin-map-%{robinmap_version}.tar.gz

BuildRequires:  ninja
BuildRequires:  llvm
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  lld
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipsparse)
BuildRequires:  libzstd-devel
BuildRequires:  rocminfo
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm-origami)
BuildRequires:  rocm-smi-lib-devel
BuildRequires:  cmake(rocsparse)
BuildRequires:  cmake(roctracer)
BuildRequires:  zlib-devel
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(msgpack)
BuildRequires:  msgpack-devel
BuildRequires:  chrpath
BuildRequires:  flexiblas-devel
BuildRequires:  gcc-gfortran
BuildRequires:  rocm-omp-devel
%if %{with test}
BuildRequires:  gtest-devel
BuildRequires:  gmock-devel
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
hipSPARSELt is a SPARSE marshaling library that provides general sparse
matrix-matrix multiplication using structured sparsity. It offers a flexible
API and supports multiple backends.

%package devel
Summary:        The hipSPARSELt development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The hipSPARSELt development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n hipSPARSELt-rocm-%{version}

# Extract and set up hipBLASLt (for its Tensile)
tar xf %{SOURCE1}
mv hipBLASLt-%{hipblaslt_commit} hipBLASLt
cd hipBLASLt

patch -p1 < %{SOURCE2}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}
patch -p1 < %{SOURCE5}

# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g' \
    tensilelite/Tensile/cmake/TensileConfig.cmake

# Make sure hip/hip_runtime.h is found
sed -i -e 's@-x hip @-I%{_includedir} -x hip @' device-library/matrix-transform/CMakeLists.txt
sed -i -e 's@"-D__HIP_HCC_COMPAT_MODE__=1"@"-D__HIP_HCC_COMPAT_MODE__=1","-I%{_includedir}"@' \
    tensilelite/Tensile/Toolchain/Component.py

%if %{with nanobind}
# Disable download of nanobind
sed -i -e 's@FetchContent_MakeAvailable(nanobind)@find_package(nanobind)@' \
    tensilelite/rocisa/CMakeLists.txt
%else
# Use bundled nanobind
tar xf %{SOURCE10}
mv nanobind-* nanobind
cd nanobind
tar xf %{SOURCE11}
cp -r robin-map-*/* ext/robin_map/
cd ..
tar czf nanobind.tar.gz nanobind
%endif

cd ..

# Prevent the virtualenv install from cmake
sed -i -e 's@virtualenv_install@#virtualenv_install@' CMakeLists.txt

# Unforce the setting of libdir
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# Change looking for cblas to flexiblas
sed -i -e 's@find_package( cblas REQUIRED CONFIG )@#find_package( cblas REQUIRED CONFIG )@' clients/CMakeLists.txt
sed -i -e 's@set( BLAS_LIBRARY "blas" )@set( BLAS_LIBRARY "flexiblas" )@' clients/CMakeLists.txt
sed -i -e 's@lapack cblas@flexiblas@' clients/gtest/CMakeLists.txt

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' hipBLASLt/cmake/dependencies.cmake
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/Dependencies.cmake

# Replace all mentions of 'amdclang' with 'clang' in Tensile Python files
find hipBLASLt/tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%build
HIPBLASLT_PATH=$PWD/hipBLASLt
cd hipBLASLt

# disable openmp in hipBLASLt
sed -i -e 's@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." ON)@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." OFF)@' CMakeLists.txt

# Do a manual install instead of cmake's virtualenv
cd tensilelite
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

%cmake -G Ninja \
    -DGPU_TARGETS=%{gpu_list} \
    -DBLAS_INCLUDE_DIR=%{_includedir}/flexiblas \
    -DBUILD_CLIENTS_TESTS=%{build_test} \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DBUILD_VERBOSE=ON \
    -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang \
    -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ \
    -DCMAKE_Fortran_COMPILER=gfortran \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_PREFIX_PATH=%{python3_sitelib}/nanobind \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DHIP_PLATFORM=amd \
    -DHIPSPARSELT_HIPBLASLT_PATH=${HIPBLASLT_PATH} \
    -DROCM_SYMLINK_LIBS=OFF \
    -DTensile_COMPILER=clang++ \
    -DTensile_LIBRARY_FORMAT=%{tensile_library_format} \
    -DTensile_TEST_LOCAL_PATH=${TL} \
    -DTensile_VERBOSE=%{tensile_verbose} \
    -DVIRTUALENV_BIN_DIR=%{_bindir} \
    -DVIRTUALENV_SITE_PATH=${TL}%{python3_sitelib} \
    %{nil}

%cmake_build

%install
%cmake_install
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

%if %{with test}
%files test
%{_bindir}/hipsparselt*
%endif

%changelog
%autochangelog
