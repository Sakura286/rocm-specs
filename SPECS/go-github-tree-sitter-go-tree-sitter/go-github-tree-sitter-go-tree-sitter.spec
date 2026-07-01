# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           go-tree-sitter
%define go_import_path  github.com/tree-sitter/go-tree-sitter
# v0.25.0 tag was deleted upstream; use a commit from 2025-02-02
%define commit_id       adc13ffd8b2c0b01b878fda9f7c422ce0df5fad3
%define go_test_ignore_failure 1

Name:           go-github-tree-sitter-go-tree-sitter
Version:        0+git20250202.adc13ff
Release:        %autorelease
Summary:        Go bindings for tree-sitter
License:        MIT
URL:            https://github.com/tree-sitter/go-tree-sitter
#!RemoteAsset:  sha256:d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed
Source0:        https://github.com/tree-sitter/go-tree-sitter/archive/%{commit_id}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros
BuildRequires:  go(github.com/mattn/go-pointer)

Provides:       go(github.com/tree-sitter/go-tree-sitter) = %{version}

Requires:       go(github.com/mattn/go-pointer)

%description
Go bindings for tree-sitter, the incremental parsing library.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
