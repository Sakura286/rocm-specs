# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipSPARSE need to download about 19 testing matrix
# It is verbose to add them to SOURCE and %%prep section
%bcond build_test 0
%if %{with build_test}
%global cmake_test ON
%else
%global cmake_test OFF
%endif

# hipSPARSE needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU.
%bcond run_test 0

# This ROCm package is built with clang by default
%global toolchain clang

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           hipsparse
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm SPARSE marshalling library
License:        MIT
Url:            https://github.com/ROCm/hipSPARSE
#!RemoteAsset:  sha256:c6ba07bd940b2678ba8a087333f103c1846efb7ffffffc5ed9174aca78d9f090
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_CLIENTS_SAMPLES=OFF
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=ON
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{cmake_test}

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
%if %{with build_test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocsparse)
BuildRequires:  compiler-rt
BuildRequires:  gcc-fortran
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
hipSPARSE is a SPARSE marshalling library with multiple
supported backends. It sits between your application and
a 'worker' SPARSE library, where it marshals inputs to
the backend library and marshals results to your
application. hipSPARSE exports an interface that doesn't
require the client to change, regardless of the chosen
backend. Currently, hipSPARSE supports rocSPARSE and
cuSPARSE backends.

%package        benchmark
Summary:        Benchmark for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    benchmark
%{summary}

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

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsparse/LICENSE.md

%check -p
export LD_LIBRARY_PATH=$PWD/%{__cmake_builddir}/library:$LD_LIBRARY_PATH

%if %{without run_test}
%check
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsparse.so.4{,.*}

%files benchmark
%{_bindir}/hipsparse-bench

%files devel
%{_includedir}/hipsparse/
%{_libdir}/cmake/hipsparse/
%{_libdir}/libhipsparse.so

%if %{with build_test}
%files test
%{_bindir}/hipsparse*
%{_datadir}/hipsparse/
%endif

%changelog
%autochangelog
