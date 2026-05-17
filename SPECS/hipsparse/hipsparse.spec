# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipSPARSE needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU, so make it optional.
%bcond test 1

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           hipsparse
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm SPARSE marshalling library

Url:            https://github.com/ROCm/hipSPARSE
VCS:            git:https://github.com/ROCm/hipSPARSE.git
License:        MIT
#!RemoteAsset:  sha256:b001834d8e65c3878d1a69d08803d5b6ce4fe623e78099fe51cb146d0ffa10e7
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

# https://github.com/ROCm/hipSPARSE (upstream patch)
Patch0:         0001-hipsparse-change-test-download-dir.patch

BuildOption(prep):  -p1 -n hipSPARSE-rocm-%{version}

BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DCMAKE_SKIP_RPATH=ON
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF
BuildOption(conf):  -DBUILD_CLIENTS_SAMPLES=OFF
BuildOption(conf):  -DBUILD_CLIENTS_TESTS_OPENMP=OFF
BuildOption(conf):  -DBUILD_FORTRAN_CLIENTS=OFF
%if %{with test}
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=ON
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DCMAKE_MATRICES_DIR=%{_builddir}/hipsparse-test-matrices/
%else
BuildOption(conf):  -DBUILD_CLIENTS_BENCHMARKS=OFF
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=OFF
%endif

BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocsparse)
BuildRequires:  gcc-fortran
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

%prep -a
# A better default for the matrices dir
sed -i -e 's@hipsparse_exepath() + "../matrices/"@"%{_datadir}/hipsparse/matrices/"@' clients/include/utility.hpp

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsparse/LICENSE.md

%if %{with test}
mkdir -p %{buildroot}%{_datadir}/hipsparse/matrices
install -pm 644 %{_builddir}/hipsparse-test-matrices/* %{buildroot}%{_datadir}/hipsparse/matrices
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsparse.so.4{,.*}

%files devel
%{_includedir}/hipsparse/
%{_libdir}/cmake/hipsparse/
%{_libdir}/libhipsparse.so

%if %{with test}
%files test
%{_bindir}/hipsparse*
%{_datadir}/hipsparse/
%endif

%changelog
%autochangelog
