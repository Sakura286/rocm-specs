# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           rocm-origami
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Analytical GEMM Solution Selection

Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/rocm-libraries.git
License:        MIT
#!RemoteAsset:  sha256:1fb56e620a06e198aeec2cf37c11e6879d0c67c62e295b48779b7f486e34acb4
Source:         %{url}/releases/download/rocm-%{version}/origami.tar.gz

# License file is not included in the release tarball
Source1:        https://raw.githubusercontent.com/ROCm/rocm-libraries/develop/shared/origami/LICENSE.md

# Workaround hipblaslt build issue:
#   origami::origami target is missing
# https://github.com/ROCm/rocm-libraries/issues/2422
Patch1:         0001-rocm-origami-remove-scope-for-variables.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(hip)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  ninja

%description
The name "origami" still evokes the elegance of transforming
a flat (2-D) sheet into intricate higher dimensional
structures. In this context, however, Origami has evolved
into a tool set for GEMM solution selection and optimization.
Inspired by the art of paper folding, the library now enables
users to explore a range of tiling and mapping configurations
and to make informed decisions on data and computation mapping
for high-performance GEMM operations.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%prep
%autosetup -p3 -n origami

# License file is not in the tarball
cp %{SOURCE1} .

# Use system rocm-cmake, no downloading
sed -i -e 's@if(NOT ROCM_FOUND)@if(FALSE)@' cmake/dependencies.cmake

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/dependencies.cmake

%build
%cmake -G Ninja \
       -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang \
       -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ \
       -DCMAKE_INSTALL_LIBDIR=%{_lib} \
       -DCMAKE_INSTALL_PREFIX=%{_prefix} \
       -DCMAKE_VERBOSE_MAKEFILE=ON \
       %{nil}

%cmake_build

%install
%cmake_install

rm -f %{buildroot}%{_datadir}/doc/origami/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/liborigami.so.0{,.*}

%files devel
%{_includedir}/origami/
%{_libdir}/cmake/origami/
%{_libdir}/liborigami.so

%changelog
%autochangelog

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}
%global pkg_suffix -%{rocm_release}
%global pkg_module rocm%{pkg_suffix}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%global pkg_module default
%endif
%global origami_name rocm-origami%{pkg_suffix}

Name:       rocm-origami%{pkg_suffix}
Version:    %{rocm_version}
Release:    1%{?dist}
Summary:    Analytical GEMM Solution Selection

License:    MIT
URL:        https://github.com/ROCm/rocm-libraries
Source0:    %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz
# License file is not in the 7.1.0 tag, but is here
Source2:    https://github.com/ROCm/rocm-libraries/tree/develop/shared/origami/LICENSE.md

#
# Workaround this hipblaslt build issue
# CMake Error at /usr/lib64/cmake/origami/origami-config.cmake:11 (message):
#   origami::origami target is missing
#
# hipblaslt from rocm-libraries does not use cmake to find origami
# https://github.com/ROCm/rocm-libraries/issues/2422
# So they would not have run into this issue.
Patch1:     0001-rocm-origami-remove-scope-for-variables.patch

ExclusiveArch: x86_64 riscv64

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: rocm-cmake%{pkg_suffix}
BuildRequires: rocm-comgr%{pkg_suffix}-devel
BuildRequires: rocm-llvm%{pkg_suffix}-macros
BuildRequires: rocm-hip%{pkg_suffix}-devel
BuildRequires: rocr-runtime%{pkg_suffix}-devel

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  hipcc
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs
BuildRequires:  git

%description
The name "origami" still evokes the elegance of transforming
a flat (2-D) sheet into intricate higher dimensional
structures. In this context, however, Origami has evolved
into a tool set for **GEMM solution selection and
optimization**. Inspired by the art of paper folding, the
library now enables users to explore a range of tiling and
mapping configurations and to make informed decisions on
data and computation mapping for high-performance GEMM
operations.

%package devel
Summary: Libraries and headers for %{name}
Requires: %{origami_name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%prep
%autosetup -p3 -n %{upstreamname}

# The license file
cp %{SOURCE2} .

# Use system rocm-cmake, no downloading
sed -i -e 's@if(NOT ROCM_FOUND)@if(FALSE)@' cmake/dependencies.cmake

%build
%cmake \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix}

%cmake_build

%install
%cmake_install

# Extra license
rm -f %{buildroot}%{pkg_prefix}/share/doc/origami/LICENSE.md

%files -n %{origami_name}
%doc README.md
%license LICENSE.md
%{pkg_prefix}/%{pkg_libdir}/liborigami.so.0{,.*}

%files devel
%{pkg_prefix}/include/origami/
%{pkg_prefix}/%{pkg_libdir}/cmake/origami/
%{pkg_prefix}/%{pkg_libdir}/liborigami.so

%changelog
* Mon Feb 23 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
