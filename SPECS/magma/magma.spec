# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocm toolchain uses the hipcc wrapper of clang
%global toolchain clang

%bcond test 0

Name:           magma
Version:        2.10.0
Release:        %autorelease
Summary:        Matrix Algebra on GPU and Multi-core Architectures
License:        BSD-3-Clause
Url:            https://icl.utk.edu/magma/
VCS:            git:https://github.com/icl-utk-edu/magma.git
#!RemoteAsset:  sha256:26347adbccbe7a6693d6b3f3c0ab5620037eb3a62b5ef69d05e40289472a82a4
Source0:        https://github.com/icl-utk-edu/%{name}/archive/v%{version}.tar.gz

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DBLA_VENDOR=OpenBLAS
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DMAGMA_ENABLE_HIP=ON
BuildOption(conf):  -DUSE_FORTRAN=OFF

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  compiler-rt
BuildRequires:  gcc-c++
BuildRequires:  hipcc
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  pkgconfig(openblas)
BuildRequires:  python3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
Matrix Algebra on GPU and Multi-core Architectures (MAGMA) is a collection
of next-generation linear algebra libraries for heterogeneous computing.
The MAGMA package supports interfaces for current linear algebra packages
and standards (e.g., LAPACK and BLAS) to enable computational scientists
to easily port any linear algebra–reliant software component to
heterogeneous computing systems. MAGMA enables applications to fully
exploit the power of current hybrid systems of many-core CPUs and
multi-GPUs/coprocessors to deliver the fastest possible time to accurate
solutions within given energy constraints.

MAGMA features LAPACK-compliant routines for multi-core CPUs enhanced with
NVIDIA or AMD GPUs. MAGMA 2.7.2 now includes more than 400 routines that
cover one-sided dense matrix factorizations and solvers, two-sided
factorizations, and eigen/singular-value problem solvers, as well as a
subset of highly optimized BLAS for GPUs. A MagmaDNN package has been
added and further enhanced to provide high-performance data analytics,
including functionalities for machine learning applications that use MAGMA
as their computational back end. The MAGMA Sparse and MAGMA Batched
packages have been included since MAGMA 1.6.

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%prep -a
# Add newer gfx targets to Makefile's valid arch whitelist
# https://bitbucket.org/icl/magma/issues/76/a-few-new-rocm-gpus
sed -i -e 's@1032 1033@1032 1033 1100 1101 1102 1103 1150 1151 1152 1153 1200 1201@' Makefile

%if %{with test}
# Remove a test that fails to link (undefined magma_generate_matrix)
sed -i -e '/testing_zgenerate.cpp/d' testing/Makefile.src
%else
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

# python to python3, need env to find local bits like magmasubs.py
sed -i -e 's@env python@env python3@' tools/checklist_run_tests.py
sed -i -e 's@env python@env python3@' tools/check-style.py
sed -i -e 's@env python@env python3@' tools/parse-magma.py

# Remove some files we do not need to similify licenses
# GPL, results for cuda
rm -rf results/*
# ICS, Copy of strlcpy - just use strlcpy
sed -i -e '/strlcpy/d' control/Makefile.src
sed -i -e '/strlcpy/d' include/magma_auxiliary.h
sed -i -e 's@magma_strlcpy@strlcpy@' control/trace.cpp
rm control/strlcpy.cpp

%build -p
echo "BACKEND = hip"                          > make.inc
echo "FORT = false"                          >> make.inc
echo "GPU_TARGET = gfx1100;gfx1200;gfx1201"  >> make.inc

make generate
%if %{with test}
%check
%{_vpath_builddir}/testing/testing_sgemm
%endif

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
