# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Sakura286 <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_version 7.1.1

Name:           rocm-core
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A utility to get the ROCm release version
License:        MIT
URL:            https://github.com/ROCm/rocm-core
#!RemoteAsset:  sha256:0171b82a4d028d57035d0d57a01a058f50f1a23959d230cdeab14972dcd94da8
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

%files devel
%{_includedir}/rocm-core/*.h
%{_libdir}/cmake/rocm-core/*.cmake
%{_libdir}/librocm-core.so

%changelog
%{?autochangelog}
