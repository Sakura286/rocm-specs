# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           frugally-deep
Version:        0.20.0
Release:        %autorelease
Summary:        Header-only library for Keras model inference using pure C++
License:        MIT
Url:            https://github.com/Dobiasd/frugally-deep
#!RemoteAsset:  sha256:8932f7b42612598402269a54f957af09084dc2cb812d32887d991d6e45b280fb
Source:         %{url}/archive/v%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DFDEEP_USE_OPENCV=OFF

BuildRequires:  cmake
BuildRequires:  cmake(FunctionalPlus)
BuildRequires:  nlohmann-json
BuildRequires:  ninja
BuildRequires:  pkgconfig(eigen3)

%description
frugally-deep is a small header-only library to run Keras (TensorFlow) models
natively in C++ without any overhead introduced by surrounding frameworks.

%files
%doc README.md
%license LICENSE
%{_includedir}/fdeep/
%{_libdir}/cmake/frugally-deep/

%changelog
%autochangelog
