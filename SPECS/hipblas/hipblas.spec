# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_version 10.1.0

%global llvm_maj_ver 24

Name:           hipblas
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm BLAS marshalling library
License:        MIT
URL:            https://github.com/ROCm/hipBLAS
#!RemoteAsset:  sha256:453fa4099c8d5419fc2e2f03fd17c4b69b7d67a39259fa1841719189024d9fe0
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipblas.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n hipblas

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas-common)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocblas-devel >= %{rocm_version}
BuildRequires:  cmake(rocblas)
BuildRequires:  rocsolver-devel >= %{rocm_version}
BuildRequires:  cmake(rocsolver)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  gcc-c++
BuildRequires:  gcc-fortran
BuildRequires:  hipcc
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros

Provides:       hipblas = %{version}-%{release}

%description
hipBLAS is a Basic Linear Algebra Subprograms (BLAS) marshalling
library, with multiple supported backends. It sits between the
application and a 'worker' BLAS library, marshalling inputs into
the backend library and marshalling results back to the
application. hipBLAS exports an interface that does not require
the client to change, regardless of the chosen backend. Currently,
hipBLAS supports rocBLAS and cuBLAS as backends.

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(hip)
Requires:       cmake(hipblas-common)

%description    devel
%{summary}

%prep -a
# This is a tarball, no .git to query
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' library/CMakeLists.txt

%install -a
rm -f %{buildroot}%{_prefix}/share/doc/hipblas/LICENSE.md

%files
%license LICENSE.md
%doc README.md
%{_libdir}/libhipblas.so.3{,.*}

%files devel
%{_includedir}/hipblas/
%{_libdir}/libhipblas.so
%{_libdir}/cmake/hipblas/

%changelog
%autochangelog
