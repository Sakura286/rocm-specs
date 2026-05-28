# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# This is a header-only library. No compiled runtime library is produced.
# All files (headers + CMake config) go into the base package per SOP rule 6.
%global debug_package %{nil}

Name:           fplus
Version:        0.2.25
Release:        %autorelease
Summary:        Functional Programming Library for C++
Url:            https://github.com/Dobiasd/FunctionalPlus
VCS:            git:https://github.com/Dobiasd/FunctionalPlus.git
License:        BSL-1.0
#!RemoteAsset:  sha256:9b5e24bbc92f43b977dc83efbc173bcf07dbe07f8718fc2670093655b56fcee3
Source:         %{url}/archive/v%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):   -G Ninja
BuildOption(setup):  -n FunctionalPlus-%{version}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja

%description
FunctionalPlus is a small header-only library supporting you in
reducing code noise and in dealing with only one single level
of abstraction at a time. By increasing brevity and maintainability
of your code it can improve productivity (and fun!) in the long
run. It pursues these goals by providing pure and easy-to-use
functions that free you from implementing commonly used flows of
control over and over again.

%prep -a
# License check flags this as BSD 3-Clause
# api_search not distributed, remove to make license simpler
rm -rf api_search

%files
%doc README.md
%license LICENSE
%{_includedir}/fplus/
%{_libdir}/cmake/FunctionalPlus/

%changelog
%autochangelog
