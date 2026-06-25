# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname peft

# Fork of the Base python-peft for the ROCm stack.  Upstream's "torch>=1.13.0"
# is auto-generated as python3dist(torch), which only the CPU python-torch
# flavor provides -- python-torch-rocm filters that provide out -- so the Base
# build is uninstallable alongside the ROCm torch.  Here we drop the generic
# torch requirement and instead require python-torch-backend, the capability
# BOTH torch flavors carry, so this installs against whichever torch backend is
# present (CPU or ROCm).  Epoch bumps over Base's 0:0.19.1-* so this copy wins
# at the same upstream version (otherwise Base's higher release is preferred).
Epoch:          1
Name:           python-%{srcname}
Version:        0.19.1
Release:        %autorelease
Summary:        State-of-the-art Parameter-Efficient Fine-Tuning
License:        Apache-2.0
URL:            https://github.com/huggingface/peft
#!RemoteAsset:  sha256:0d97542fe96dcdaa20d3b81c06f26f988618f416a73544ab23c3618ccb674a40
Source0:        https://files.pythonhosted.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}
BuildOption(check):  -e peft.tuners.*.bnb

# Replace the auto-generated generic torch requirement with python-torch-backend
# (provided by both the CPU and ROCm torch flavors).
%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(attrs)

Requires:       python-torch-backend >= 1.13.0

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
State-of-the-art Parameter-Efficient Fine-Tuning (PEFT) methods.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
%autochangelog
