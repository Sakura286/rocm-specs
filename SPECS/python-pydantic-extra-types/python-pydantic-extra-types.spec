# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname pydantic-extra-types
%global pypi_name pydantic_extra_types

Name:           python-%{srcname}
Version:        2.11.1
Release:        %autorelease
Summary:        Extra Pydantic types
License:        MIT
URL:            https://github.com/pydantic/pydantic-extra-types
#!RemoteAsset:  sha256:46792d2307383859e923d8fcefa82108b1a141f8a9c0198982b3832ab5ef1049
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  %{pypi_name}
# semver is an optional dependency that is not packaged
BuildOption(check):  -e 'pydantic_extra_types.semver'

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(hatchling)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Extra Pydantic types provides a collection of additional field types and
validators for Pydantic, such as country codes, phone numbers, colors,
coordinates and currency codes.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
