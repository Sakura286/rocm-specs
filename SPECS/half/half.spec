# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           half
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm half-precision floating point library
License:        MIT
URL:            https://github.com/ROCm/half
# TheRock 10.1 pins the same half commit as the previous collection.
#!RemoteAsset:  sha256:a0b486f91ca2e60a9e8b22dcdb08c56d0306fed3c97d11ffb19638caf6939421
Source0:        https://github.com/ROCm/half/archive/207ee58595a64b5c4a70df221f1e6e704b807811/half-207ee58595a64b5c4a70df221f1e6e704b807811.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n half-207ee58595a64b5c4a70df221f1e6e704b807811

BuildRequires:  cmake
BuildRequires:  rocm-cmake

%description
half is a C++ header-only library providing an IEEE-754 conformant
half-precision floating point type along with arithmetic operators,
type conversions, and common mathematical functions. It is part of
the ROCm software stack.

%install -a
rm -f %{buildroot}%{_datadir}/doc/half/LICENSE.txt

%files
%doc README.txt
%license LICENSE.txt
%{_includedir}/half/

%changelog
%autochangelog
