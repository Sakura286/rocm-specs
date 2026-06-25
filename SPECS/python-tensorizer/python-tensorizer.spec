# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tensorizer

# Fork of the Base python-tensorizer for the ROCm stack.  Upstream's
# "torch>=1.9.0" is auto-generated as python3dist(torch), which only the CPU
# python-torch flavor provides -- python-torch-rocm filters that provide out --
# so the Base build is uninstallable alongside the ROCm torch.  Here we drop the
# generic torch requirement and instead require python-torch-backend, the
# capability BOTH torch flavors carry.  Epoch bumps over Base's 0:2.12.1-* so
# this copy wins at the same upstream version.
Epoch:          1
Name:           python-%{srcname}
Version:        2.12.1
Release:        %autorelease
Summary:        Module, Model, and Tensor Serialization/Deserialization
License:        MIT
URL:            https://github.com/coreweave/tensorizer
#!RemoteAsset:  sha256:8af9b3be54f31d08d1928e3f25bfaaa963cdc8d716d09559c68ec014f8beb440
Source0:        https://files.pythonhosted.org/packages/source/t/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

# Replace the auto-generated generic torch requirement with python-torch-backend
# (provided by both the CPU and ROCm torch flavors).
%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(boto3)
BuildRequires:  python3dist(hiredis)
BuildRequires:  python3dist(libnacl)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(protobuf)
BuildRequires:  python3dist(psutil)
BuildRequires:  python3dist(redis)
BuildRequires:  python3dist(torch)

Requires:       python-torch-backend >= 1.9.0

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Module, Model, and Tensor Serialization/Deserialization.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
