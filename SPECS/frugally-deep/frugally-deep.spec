# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# This is a header-only library. No compiled runtime library is produced.
# All files (headers + CMake config) go into the base package per SOP rule 6.
%global debug_package %{nil}

Name:           frugally-deep
Version:        0.15.30
Release:        %autorelease
Summary:        Header-only library for Keras model inference using pure C++
Url:            https://github.com/Dobiasd/frugally-deep
VCS:            git:https://github.com/Dobiasd/frugally-deep.git
License:        MIT
#!RemoteAsset:  sha256:8932f7b42612598402269a54f957af09084dc2cb812d32887d991d6e45b280fb
Source:         %{url}/archive/v%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DFDEEP_USE_OPENCV=OFF

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  eigen3-devel
BuildRequires:  cmake(FunctionalPlus)
BuildRequires:  nlohmann-json
BuildRequires:  ninja

# No compiled runtime: provide cmake() so dependents can use cmake(frugally-deep)
Provides:       cmake(frugally-deep) = %{version}

%description
frugally-deep is a small header-only library to run Keras (TensorFlow) models
natively in C++ without any overhead introduced by surrounding frameworks.

%prep -a
# Update cmake minimum required version to avoid policy errors
sed -i -e 's@cmake_minimum_required(VERSION 3.2)@cmake_minimum_required(VERSION 3.5)@' \
    CMakeLists.txt

%files
%doc README.md
%license LICENSE
%{_includedir}/fdeep/
%{_libdir}/cmake/frugally-deep/

%changelog
%autochangelog
