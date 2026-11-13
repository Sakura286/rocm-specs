# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipSOLVER tests require a GPU.
%bcond test 0

%global rocm_release 7.14
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

Name:           hipsolver
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm SOLVER marshalling library (LAPACK)
License:        MIT
URL:            https://github.com/ROCm/hipSOLVER
#!RemoteAsset:  sha256:dff6cad875aced2d1264709c8f0560738d2059705fd29f13262c41ab35bb5a12
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/hipsolver.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n hipsolver

# LLVM 23's HIP bundler requires the host triple's environment field.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DCMAKE_HIP_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -G Ninja
# Use distribution LAPACK for the CPU geev fallback; do not clone OpenBLAS.
BuildOption(conf):  -DHIPSOLVER_INTERNAL_LAPACK_BUILD=OFF
%if %{with test}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=ON
%else
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=OFF
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=OFF
%endif
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  rocm-hip-devel >= 7.14.1
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocr-runtime-devel >= 7.14.1
BuildRequires:  cmake(rocblas)
BuildRequires:  rocblas-devel >= 7.14.1
BuildRequires:  cmake(rocsolver)
BuildRequires:  rocsolver-devel >= 7.14.1
BuildRequires:  cmake(rocsparse)
BuildRequires:  rocsparse-devel >= 7.14.1
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  gcc-fortran
BuildRequires:  lapack-devel >= 3.7
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%if %{with test}
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(hipsparse)
BuildRequires:  hipsparse-devel >= 7.14.1
BuildRequires:  pkgconfig(openblas)
%endif

%global _description %{expand:
hipSOLVER is a LAPACK marshalling library, with multiple supported backends.
It sits between the application and a "worker" SOLVER library, marshalling
inputs into the backend library and results back to the application. hipSOLVER
exports an interface that does not require the client to change, regardless of
the chosen backend.
}

%description
%{_description}

%package        devel
Summary:        The hipSOLVER development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(rocblas)
Requires:       cmake(rocsolver)
Requires:       cmake(rocsparse)

%description    devel
The hipSOLVER development package.

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}
%endif

%build -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"

%conf -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsolver/LICENSE.md

%check
%if %{with test}
%ctest
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

%if %{with test}
%files test
%{_datadir}/hipsolver/
%{_bindir}/hipsolver*
%endif

%changelog
%autochangelog
