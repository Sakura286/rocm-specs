# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# magma uses hipcc-based compilation
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//' -e 's/-flto=thin//' )

%global _lto_cflags %nil

%bcond test 0
%if %{with test}
%global gpu_list gfx1201
%else
%global gpu_list %{rocm_gpu_list_default}
%endif

Name:           magma
Version:        2.9.0
Release:        %autorelease
Summary:        Matrix Algebra on GPU and Multi-core Architectures
Url:            https://icl.utk.edu/magma/
VCS:            git:https://github.com/icl-utk-edu/magma.git
License:        BSD-3-Clause AND MIT
#!RemoteAsset:  sha256:c9307e3e10dd89cb0b8d00653e78291a868aef2c1a1c56956325600cc38f7284
Source:         https://github.com/icl-utk-edu/%{name}/archive/v%{version}.tar.gz
Patch0:         0001-Prepare-magma-cmake-for-fedora.patch
Patch1:         0001-magma-ROCm-7-changes.patch

BuildRequires:  llvm
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  lld
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  openblas-devel
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipsparse)
BuildRequires:  ninja
BuildRequires:  python3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)

%description
MAGMA is a collection of next-generation dense linear algebra libraries for
heterogeneous systems with multicore CPUs and GPUs. It supports HIP/ROCm for
AMD GPUs.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Libraries and headers for the MAGMA GPU linear algebra library.

%prep
%autosetup -p1

%if %{with test}
# Just the test gpu gfx1201
sed -i -e 's@1032 1033@1201@' Makefile
# Remove some tests
sed -i -e '/testing_zgenerate.cpp/d' testing/Makefile.src
%else
# Add some more gfx's
sed -i -e 's@1032 1033@950 1032 1033 1100 1101 1102 1103 1150 1151 1152 1153 1200 1201@' Makefile
# Disable building tests
sed -i -e 's@include_directories( testing )@#include_directories( testing )@' CMakeLists.txt
sed -i -e 's@foreach( filename ${testing_all} )@foreach( filename ${no_testing_all} )@' CMakeLists.txt
sed -i -e 's@add_custom_target( testing DEPENDS ${testing} )@#add_custom_target( testing DEPENDS ${testing} )@' CMakeLists.txt
sed -i -e 's@foreach( TEST ${sparse_testing_all} )@foreach( TEST ${no_sparse_testing_all} )@' CMakeLists.txt
sed -i -e 's@add_custom_target( sparse-testing DEPENDS ${sparse-testing} )@#add_custom_target( sparse-testing DEPENDS ${sparse-testing} )@' CMakeLists.txt
%endif

# Change the bin,lib install locations
sed -i -e 's@DESTINATION lib@DESTINATION ${CMAKE_INSTALL_LIBDIR}@' CMakeLists.txt
sed -i -e 's@DESTINATION bin@DESTINATION ${CMAKE_INSTALL_BINDIR}@' CMakeLists.txt

# Version *.so
sed -i -e 's@magma_VERSION@"%{version}"@g' CMakeLists.txt

# python to python3
sed -i -e 's@env python@env python3@' tools/checklist_run_tests.py
sed -i -e 's@env python@env python3@' tools/check-style.py
sed -i -e 's@env python@env python3@' tools/parse-magma.py

# Remove some files we do not need to simplify licenses
rm -rf results/*
sed -i -e '/strlcpy/d' control/Makefile.src
sed -i -e '/strlcpy/d' include/magma_auxiliary.h
sed -i -e 's@magma_strlcpy@strlcpy@' control/trace.cpp
rm control/strlcpy.cpp

sed -i -e 's@cmake_policy( SET CMP0037 OLD)@#cmake_policy( SET CMP0037 OLD)@' CMakeLists.txt

# Add offload-compress compile flags
sed -i -e 's@-DROCM_VERSION@--offload-compress -DROCM_VERSION@' CMakeLists.txt

%build
echo "BACKEND = hip"  > make.inc
echo "FORT = false"  >> make.inc
%if %{with test}
echo "GPU_TARGET = gfx1201" >> make.inc
%else
echo "GPU_TARGET = gfx900;gfx906:xnack-;gfx908:xnack-;gfx90a:xnack+;gfx90a:xnack-;gfx942;gfx950;gfx1010;gfx1012;gfx1030;gfx1031;gfx1035;gfx1100;gfx1101;gfx1102;gfx1103;gfx1150;gfx1151;gfx1152;gfx1153;gfx1200;gfx1201" >> make.inc
%endif

make generate

%cmake -G Ninja \
    -DBLA_VENDOR=OpenBLAS \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DAMDGPU_TARGETS=%{gpu_list} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DMAGMA_ENABLE_HIP=ON \
    -DUSE_FORTRAN=OFF

%cmake_build

%install
%cmake_install

%files
%license COPYRIGHT
%{_libdir}/libmagma.so{,.*}
%{_libdir}/libmagma_sparse.so{,.*}

%files devel
%{_includedir}/*.h
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/libmagma.so
%{_libdir}/libmagma_sparse.so

%changelog
%autochangelog
