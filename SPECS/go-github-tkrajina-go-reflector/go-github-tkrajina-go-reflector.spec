# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           go-reflector
%define go_import_path  github.com/tkrajina/go-reflector
%define go_test_ignore_failure 1

Name:           go-github-tkrajina-go-reflector
Version:        0.5.5
Release:        %autorelease
Summary:        Go reflection utilities
License:        MIT
URL:            https://github.com/tkrajina/go-reflector
#!RemoteAsset:  sha256:fa4e04b3db3335447fc1e8da9fc4ea7843ab780ee9bd82a0176bc9c908905eee
Source0:        https://github.com/tkrajina/go-reflector/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros

Provides:       go(github.com/tkrajina/go-reflector) = %{version}

%description
Go reflection utilities for inspecting and manipulating struct fields.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
