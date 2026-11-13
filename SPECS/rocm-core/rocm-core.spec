# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_version 10.1.0

Name:           rocm-core
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A utility to get the ROCm release version
License:        MIT
URL:            https://github.com/ROCm/rocm-core
# ROCm 10.1.0 source release uses the therock-10.1 tag.
#!RemoteAsset:  sha256:3fbbe95aacb3ca9613f549ecdbee457c09c686ecd524ebe19160026e2fa56248
Source0:        https://github.com/ROCm/rocm-systems/releases/download/therock-10.1/rocm-core.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n rocm-core

BuildOption(conf):  -DROCM_VERSION=%{version}

BuildRequires:  cmake

%global _description %{expand:
A utility to get the ROCm release version
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%install -a
# ROCm version is maintained by packager
# No need to use rocmmod to switch ROCm version
rm -rvf %{buildroot}/%{_exec_prefix}/.info
rm -rvf %{buildroot}/%{_libdir}/rocmmod
# Use RUNPATH instead of RPATH on Linux distribution
rm -vf %{buildroot}/%{_exec_prefix}/libexec/rocm-core/runpath_to_rpath.py
rm -rvf %{buildroot}/%{_exec_prefix}/share/doc/*/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_bindir}/rdhc
%{_libdir}/librocm-core.so.*
%{_libexecdir}/rocm-core/
%{_datadir}/rdhc/

%files devel
%{_includedir}/rocm-core/*.h
%{_libdir}/cmake/rocm-core/*.cmake
%{_libdir}/librocm-core.so

%changelog
%autochangelog
