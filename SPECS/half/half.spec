# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.1
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           half
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm half-precision floating point library
Url:            https://github.com/ROCm/half
VCS:            git:https://github.com/ROCm/half.git
License:        MIT
#!RemoteAsset:  sha256:1b5de9e50513560265a79022fd74322b77216f9bf938be688709a8e7d1d8d09d
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja

BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  rocm-cmake

Provides:       cmake(half) = %{version}

%description
half is a C++ header-only library providing an IEEE-754 conformant
half-precision floating point type along with arithmetic operators,
type conversions, and common mathematical functions. It is part of
the ROCm software stack.

%files
%license LICENSE.txt
%doc README.txt
%{_includedir}/half/
%{_libdir}/cmake/half/

%changelog
%autochangelog
