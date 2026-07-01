# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Sakura286 <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_version 7.2.4

Name:           rocm-core
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A utility to get the ROCm release version
License:        MIT
URL:            https://github.com/ROCm/rocm-core
#!RemoteAsset:  sha256:32dab2f00e22fb5462beffae03cc642403925d22a42662e15ac0f68d8e885dea
Source0:        %{url}/archive/refs/tags/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DROCM_VERSION=%{rocm_version}

BuildRequires:  cmake

Provides:       rocm-core = %{version}-%{release}

%description
%{summary}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%install -a
rm -rvf %{buildroot}/%{_exec_prefix}/.info
rm -rvf %{buildroot}/%{_exec_prefix}/libexec/rocm-core
rm -rvf %{buildroot}/%{_exec_prefix}/share/doc/*/LICENSE.md
rm -rvf %{buildroot}/%{_libdir}/rocmmod

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocm-core.so.*
%{_bindir}/rdhc
%{_datadir}/rdhc/

%files devel
%{_includedir}/rocm-core/*.h
%{_libdir}/cmake/rocm-core/*.cmake
%{_libdir}/librocm-core.so

%changelog
%{?autochangelog}
