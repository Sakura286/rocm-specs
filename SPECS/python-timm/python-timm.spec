# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name timm

Name:           python-%{pypi_name}
Version:        1.0.27
Release:        %autorelease
Summary:        PyTorch Image Models
License:        Apache-2.0
URL:            https://github.com/huggingface/pytorch-image-models
#!RemoteAsset:  sha256:315dfe63186ca9fb7ff941268941231fd5be259f2b4bb4afa28560ae1015cb9a
Source0:        https://files.pythonhosted.org/packages/source/t/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  %{pypi_name}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pdm-backend)

%description
timm (PyTorch Image Models) is a collection of image models, layers, utilities,
optimizers, schedulers, data-loaders, augmentations, and training and evaluation
scripts for PyTorch.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
