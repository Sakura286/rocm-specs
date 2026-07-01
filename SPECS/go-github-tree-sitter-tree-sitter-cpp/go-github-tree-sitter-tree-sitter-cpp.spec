# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           tree-sitter-cpp
%define go_import_path  github.com/tree-sitter/tree-sitter-cpp/bindings/go
%define go_test_ignore_failure 1

Name:           go-github-tree-sitter-tree-sitter-cpp
Version:        0.23.4
Release:        %autorelease
Summary:        Tree-sitter C++ grammar
License:        MIT
URL:            https://github.com/tree-sitter/tree-sitter-cpp
#!RemoteAsset:  sha256:7a2c55afe3028f4105f25762ea58cc16537d1f5a1dcd9cca90410b3cd5d46051
Source0:        https://github.com/tree-sitter/tree-sitter-cpp/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros

Provides:       go(github.com/tree-sitter/tree-sitter-cpp/bindings/go) = %{version}

%description
Tree-sitter grammar for C++.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/github.com/tree-sitter/tree-sitter-cpp

%changelog
%{?autochangelog}
