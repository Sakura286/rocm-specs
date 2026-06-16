# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Gui-Yue <xiangwei.riscv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# openRuyi base ships transformers 5.2.0, which falls inside vLLM 0.22.1's
# excluded 5.0-5.5.0 range; carry 5.12.1 here (vLLM allows >=5.5.1, and its
# huggingface-hub >=1.5.0,<2.0 floor matches base's hub 1.5.0). Drop once base
# bumps past 5.5.0.

%global srcname transformers

Name:           python-transformers
Version:        5.12.1
Release:        %autorelease
Summary:        Model-definition framework for state-of-the-art machine learning
License:        Apache-2.0
URL:            https://pypi.org/project/transformers/
VCS:            git:https://github.com/huggingface/transformers
#!RemoteAsset:  sha256:679ee731c8225347889ad4fb3b2c926a62e9da3b7d284e9d12c791da7272466b
Source0:        https://files.pythonhosted.org/packages/source/t/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}
BuildOption(check):  -e 'transformers.*'

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Transformers provides model definitions for state-of-the-art machine learning
across text, vision, audio, video, and multimodal tasks for inference and
training.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/transformers

%changelog
%autochangelog
