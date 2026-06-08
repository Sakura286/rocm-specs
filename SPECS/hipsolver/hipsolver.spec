# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# TODO: hipSOLVER need lapack to build test/benchmark/sample
# But openblas on openRuyi does not provide this
%bcond build_test 0
%if %{with build_test}
%global cmake_test ON
%else
%global cmake_test OFF
%endif

# hipSOLVER needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU.
%bcond run_test 0

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

# Fortran is only used in testing
# clang and gfortran fedora toolchain args do not mix
%global build_fflags %{nil}

Name:           hipsolver
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm SOLVER marshalling library (LAPACK)
License:        MIT
Url:            https://github.com/ROCm/hipSOLVER
#!RemoteAsset:  sha256:bd664e3cd43bfcc7e94d5a387c27262c4b218d6d2e71e086992b174349dd1c10
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{cmake_test}
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=%{cmake_test}

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocsolver)
BuildRequires:  cmake(rocsparse)
BuildRequires:  compiler-rt
BuildRequires:  gcc-fortran
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%if %{with build_test}
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(hipsparse)
BuildRequires:  pkgconfig(openblas)
%endif

%description
hipSOLVER is a LAPACK marshalling library, with multiple supported backends.
It sits between the application and a "worker" SOLVER library, marshalling
inputs into the backend library and results back to the application. hipSOLVER
exports an interface that does not require the client to change, regardless of
the chosen backend.

%package        devel
Summary:        The hipSOLVER development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(rocblas)
Requires:       cmake(rocsolver)
Requires:       cmake(rocsparse)

%description    devel
The hipSOLVER development package.

%if %{with build_test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsolver/LICENSE.md

%check -p
export LD_LIBRARY_PATH=$PWD/%{__cmake_builddir}/library:$LD_LIBRARY_PATH

%if %{without test}
%check
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsolver.so.1{,.*}
%{_libdir}/libhipsolver_fortran.so.1{,.*}

%files devel
%{_includedir}/hipsolver/
%{_libdir}/libhipsolver.so
%{_libdir}/libhipsolver_fortran.so
%{_libdir}/cmake/hipsolver/

%if %{with build_test}
%files test
%{_datadir}/hipsolver/
%{_bindir}/hipsolver*
%endif

%changelog
%autochangelog
