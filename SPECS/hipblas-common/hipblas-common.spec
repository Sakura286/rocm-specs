# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_version 10.1.0

Name:           hipblas-common
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Common files shared by hipBLAS and hipBLASLt
License:        MIT
URL:            https://github.com/ROCm/hipBLAS-common
# ROCm 10.1.0 source release uses the therock-10.1 tag.
#!RemoteAsset:  sha256:cd34bfe9d3854201dede971fb758df01dc6497dd4e7c17e2cc634f7b240af444
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipblas-common.tar.gz
BuildArch:      noarch
BuildSystem:    cmake

BuildOption(prep):  -n hipblas-common

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rocm-cmake

%description
%summary

%package        devel
Summary:        Libraries and headers for %{name}
Provides:       %{name}-static = %{version}-%{release}

%description    devel
%{summary}

%install -a
rm -f %{buildroot}%{_prefix}/share/doc/hipblas-common/LICENSE.md

%files devel
%license LICENSE.md
%{_includedir}/%{name}
%{_libdir}/cmake/%{name}

%changelog
%autochangelog
