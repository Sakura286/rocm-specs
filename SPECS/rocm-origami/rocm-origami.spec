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
License:        MIT
Url:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:1fb56e620a06e198aeec2cf37c11e6879d0c67c62e295b48779b7f486e34acb4
Source0:         %{url}/releases/download/rocm-%{version}/origami.tar.gz
# License file is not included in the release tarball
#!RemoteAsset
Source1:        https://raw.githubusercontent.com/ROCm/rocm-libraries/develop/shared/origami/LICENSE.md
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON

# Workaround hipblaslt build issue:
#   origami::origami target is missing
# https://github.com/ROCm/rocm-libraries/issues/2422
Patch0:         0001-rocm-origami-remove-scope-for-variables.patch

BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  cmake(hip)
BuildRequires:  lld
BuildRequires:  llvm
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

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%prep -a
# License file is not in the tarball
cp %{SOURCE1} .
# Use system rocm-cmake, no downloading
sed -i -e 's@if(NOT ROCM_FOUND)@if(FALSE)@' cmake/dependencies.cmake
# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/dependencies.cmake

%install -a
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
