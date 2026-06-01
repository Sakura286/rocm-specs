# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname mistral-common
%global pypi_name mistral_common

Name:           python-%{srcname}
Version:        1.11.2
Release:        %autorelease
Summary:        Library of common utilities for Mistral AI
License:        Apache-2.0
URL:            https://github.com/mistralai/mistral-common
#!RemoteAsset:  sha256:79f68fc2d1190f28637f40e053f919c8c2697e00b2aa679ddee562a95183f4ad
Source0:        https://files.pythonhosted.org/packages/source/m/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
# Upstream does not ship the license file in the sdist, fetch it separately
#!RemoteAsset:  sha256:5ed6f79e77734b5a60740dd821af5ecac9a6f33709c860eea4e20fcb6cca7fcc
Source1:        https://raw.githubusercontent.com/mistralai/mistral-common/v%{version}/LICENCE
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  %{pypi_name}
# These modules require the optional "server" extra (fastapi, click, pydantic-settings)
BuildOption(check):  -e 'mistral_common.experimental.app.*'

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
mistral-common is a library of common utilities for Mistral AI, providing
tokenizers, request and response schemas, and validation helpers used across
Mistral's models and tooling.

%prep -a
cp -p %{SOURCE1} LICENCE
# Relax jsonschema lower bound to match the version available in the repo
sed -i 's/jsonschema>=4.21.1/jsonschema>=4.17.3/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENCE
%{_bindir}/mistral_common

%changelog
%autochangelog
