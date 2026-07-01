# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           typescriptify-golang-structs
%define go_import_path  github.com/tkrajina/typescriptify-golang-structs
%define go_test_ignore_failure 1

Name:           go-github-tkrajina-typescriptify-golang-structs
Version:        0.2.0
Release:        %autorelease
Summary:        Convert Go structs to TypeScript interfaces
License:        Apache-2.0
URL:            https://github.com/tkrajina/typescriptify-golang-structs
#!RemoteAsset:  sha256:0bc43bb0e4e70fb10402be448b58eae7babd19f69e9dcbf4ff77f8f62c1b8abc
Source0:        https://github.com/tkrajina/typescriptify-golang-structs/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros
BuildRequires:  go(github.com/tkrajina/go-reflector)

Provides:       go(github.com/tkrajina/typescriptify-golang-structs) = %{version}

Requires:       go(github.com/tkrajina/go-reflector)

%description
A Go library that converts Go structs to TypeScript interfaces/classes.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
