# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           go-sqlite3
%define go_import_path  github.com/mattn/go-sqlite3
%define go_test_ignore_failure 1

Name:           go-github-mattn-go-sqlite3
Version:        1.14.24
Release:        %autorelease
Summary:        SQLite3 driver for Go using CGO
License:        MIT
URL:            https://github.com/mattn/go-sqlite3
#!RemoteAsset:  sha256:8fa3b0b66914ae2dd4ddef9a954f614c5b3eb6ac9d80ee61ae2d08e3178507ec
Source0:        https://github.com/mattn/go-sqlite3/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros
BuildRequires:  pkgconfig(sqlite3)

Provides:       go(github.com/mattn/go-sqlite3) = %{version}

Requires:       pkgconfig(sqlite3)

%description
sqlite3 driver conforming to the built-in database/sql interface.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
