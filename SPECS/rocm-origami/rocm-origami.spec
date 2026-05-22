# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

Name:           rocm-origami
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Analytical GEMM Solution Selection for ROCm
Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/rocm-libraries.git
License:        MIT
#!RemoteAsset:  sha256:1fb56e620a06e198aeec2cf37c11e6879d0c67c62e295b48779b7f486e34acb4
Source:         %{url}/releases/download/rocm-%{version}/origami.tar.gz
# The LICENSE.md is not bundled in the release tarball
Source2:        https://raw.githubusercontent.com/ROCm/rocm-libraries/rocm-%{version}/shared/origami/LICENSE.md
# Patch paths are relative to shared/origami/ in the monorepo, so strip 3 levels (-p3)
Patch1:         0001-rocm-origami-remove-scope-for-variables.patch
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DCMAKE_SKIP_RPATH=ON
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
rocm-origami (Origami) is an analytical GEMM solution selection library
for ROCm. It provides fast GPU-based general matrix multiply performance
estimation without requiring actual kernel execution.

%package devel
Summary:        The rocm-origami development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The rocm-origami development package.

%prep
# The tarball extracts to "origami/" and the patch needs -p3
# (strips a/shared/origami/ prefix from the monorepo patch context)
%autosetup -p3 -n origami
# Use system rocm-cmake, do not try to download it
sed -i -e 's@if(NOT ROCM_FOUND)@if(FALSE)@' cmake/dependencies.cmake
# Install the license file that is absent from the release tarball
cp %{SOURCE2} .

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
