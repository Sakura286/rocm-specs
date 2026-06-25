# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Gui-Yue <xiangwei.riscv@isrc.iscas.ac.cn>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname accelerate

# Fork of the Base python-accelerate for the ROCm stack.  Upstream's
# "torch>=2.0.0" is auto-generated as python3dist(torch), which only the CPU
# python-torch flavor provides -- python-torch-rocm filters that provide out --
# so the Base build is uninstallable alongside the ROCm torch (and python-peft,
# which requires accelerate, cannot resolve on a ROCm system).  Here we drop the
# generic torch requirement and instead require python-torch-backend, the
# capability BOTH torch flavors carry.  Epoch bumps over Base's 0:1.13.0-* so
# this copy wins at the same upstream version.
Epoch:          1
Name:           python-accelerate
Version:        1.13.0
Release:        %autorelease
Summary:        Tools for distributed and mixed precision PyTorch training
License:        MIT
URL:            https://pypi.org/project/accelerate/
VCS:            git:https://github.com/huggingface/accelerate
#!RemoteAsset:  sha256:d631b4e0f5b3de4aff2d7e9e6857d164810dfc3237d54d017f075122d057b236
Source0:        https://files.pythonhosted.org/packages/source/a/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname} +auto
BuildOption(check):  -e 'accelerate.test_utils*' -e accelerate.utils.rich

# Replace the auto-generated generic torch requirement with python-torch-backend
# (provided by both the CPU and ROCm torch flavors).
%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Requires:       python-torch-backend >= 2.0.0

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Accelerate provides utilities to run PyTorch training and inference across
different devices and distributed setups with minimal code changes.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
