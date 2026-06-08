# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           fplus
Version:        0.2.28
Release:        %autorelease
Summary:        Helps you write concise and readable C++ code
Url:            https://github.com/Dobiasd/FunctionalPlus
License:        BSL-1.0
#!RemoteAsset:  sha256:8864a3e9bebde6ebed71b49ac2a036cedf9ae0f02ce758bc28c21e6a2ae15803
Source0:         %{url}/archive/v%{version}.tar.gz
BuildSystem:    cmake

BuildRequires:  cmake

%description
FunctionalPlus is a small header-only library supporting you in
reducing code noise and in dealing with only one single level
of abstraction at a time. By increasing brevity and maintainability
of your code it can improve productivity (and fun!) in the long
run. It pursues these goals by providing pure and easy-to-use
functions that free you from implementing commonly used flows of
control over and over again.

%files
%doc README.md
%license LICENSE
%{_includedir}/fplus/
%{_libdir}/cmake/FunctionalPlus/

%changelog
%autochangelog
