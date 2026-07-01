# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           go-pointer
%define go_import_path  github.com/mattn/go-pointer

Name:           go-github-mattn-go-pointer
Version:        0.0.1
Release:        %autorelease
Summary:        Safe utilities for dealing with Go pointers to C
License:        MIT
URL:            https://github.com/mattn/go-pointer
#!RemoteAsset:  sha256:5630a863fa1c2516ea3d2eeab94274768463018778486dddebfcb0fa32ea50fb
Source0:        https://github.com/mattn/go-pointer/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros

Provides:       go(github.com/mattn/go-pointer) = %{version}

%description
pointer is a Go library for dealing with Go pointers to C.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
