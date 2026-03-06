# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstreamname hipBLAS
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

%bcond_with test
%if %{with test}
%global build_test ON
%global __brp_check_rpaths %{nil}
# test parallel building broken
%global _smp_mflags -j1
%else
%global build_test OFF
%endif

Name:           hipblas
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm BLAS marshalling library
License:        MIT
Url:            https://github.com/ROCmSoftwarePlatform/%{upstreamname}
#!RemoteAsset
Source0:        %{url}/archive/refs/tags/rocm-%{rocm_version}.tar.gz
BuildSystem:    cmake

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  gcc-fortran
BuildRequires:  hipblas-common-devel
BuildRequires:  rocblas-devel
BuildRequires:  rocm-cmake
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocm-hip-devel
BuildRequires:  rocr-runtime-devel
# BuildRequires:  rocm-rpm-macros
BuildRequires:  rocsolver-devel

BuildRequires:  llvm
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  hipcc

%if %{with test}
BuildRequires:  gtest-devel
BuildRequires:  blas-static
BuildRequires:  lapack-static
BuildRequires:  python3-pyyaml
%endif

Provides:       hipblas = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
hipBLAS is a Basic Linear Algebra Subprograms (BLAS) marshalling
library, with multiple supported backends. It sits between the
application and a 'worker' BLAS library, marshalling inputs into
the backend library and marshalling results back to the
application. hipBLAS exports an interface that does not require
the client to change, regardless of the chosen backend. Currently,
hipBLAS supports rocBLAS and cuBLAS as backends.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       hipblas-common-devel

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/hipblas
%else
%autosetup -p1 -n %{upstreamname}-rocm-%{version}
%endif

# This is a tarball, no .git to query
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' library/CMakeLists.txt

%build
%if %{with gitcommit}
cd projects/hipblas
%endif

%cmake \
    -DCMAKE_CXX_COMPILER=hipcc \
    -DCMAKE_C_COMPILER=hipcc \
    -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \
    -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \
    -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \
    -DCMAKE_BUILD_TYPE=%build_type \
    -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \
    -DCMAKE_SKIP_RPATH=ON \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DROCM_SYMLINK_LIBS=OFF \
    -DHIP_PLATFORM=amd \
    -DAMDGPU_TARGETS=%{rocm_gpu_list_default} \
    -DCMAKE_INSTALL_LIBDIR=%_libdir \
    -DBUILD_CLIENTS_BENCHMARKS=%{build_test} \
    -DBUILD_CLIENTS_TESTS=%{build_test} \
    -DBUILD_CLIENTS_TESTS_OPENMP=OFF \
    -DBUILD_FORTRAN_CLIENTS=OFF \
    -DBLAS_LIBRARY=cblas

%cmake_build

%install
%if %{with gitcommit}
cd projects/hipblas
%endif
%cmake_install

rm -f %{buildroot}%{_prefix}/share/doc/hipblas/LICENSE.md

%files
%license LICENSE.md
%doc README.md
%{_libdir}/libhipblas.so.3{,.*}

%files devel
%{_includedir}/hipblas/
%{_libdir}/libhipblas.so
%{_libdir}/cmake/hipblas/

%if %{with test}
%files test
%{_bindir}/hipblas*
%endif

%changelog
* Mon Dec 15 2025 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
