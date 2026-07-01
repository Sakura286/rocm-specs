# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%define _name           go-localereader
%define go_import_path  github.com/mattn/go-localereader

Name:           go-github-mattn-go-localereader
Version:        0.0.1
Release:        %autorelease
Summary:        Read from a locale-aware stdin on Windows
License:        MIT
URL:            https://github.com/mattn/go-localereader
#!RemoteAsset:  sha256:03bd5a512b593c793cccd3a1f507e3a5ba6f92681b1fa4f812a53eddbc3751dc
Source0:        https://github.com/mattn/go-localereader/archive/v%{version}.tar.gz#/%{_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    golangmodules

BuildRequires:  go
BuildRequires:  go-rpm-macros

Provides:       go(github.com/mattn/go-localereader) = %{version}

%description
go-localereader is a Go library to read from a locale-aware stdin on Windows.

%files
%license LICENSE*
%doc README*
%{go_sys_gopath}/%{go_import_path}

%changelog
%{?autochangelog}
