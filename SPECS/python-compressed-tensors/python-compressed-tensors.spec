# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname compressed-tensors
%global pypi_name compressed_tensors

# Fork of the Base python-compressed-tensors for the ROCm stack.  Upstream's
# generic "torch>=1.7.0" dependency is auto-generated as python3dist(torch),
# which only the CPU python-torch flavor provides -- python-torch-rocm filters
# that provide out.  So the Base build is uninstallable alongside the ROCm
# torch, and python-vllm-rocm (which pulls compressed-tensors) cannot resolve.
# Here we drop the generic torch requirement and instead require
# python-torch-backend, the capability BOTH torch flavors carry, so this builds
# install against whichever torch backend is present (CPU or ROCm).
# Epoch bumps over Base's 0:0.15.0.1-* so this copy wins at the same upstream
# version (otherwise Base's higher release would be preferred).
Epoch:          1
Name:           python-%{srcname}
Version:        0.15.0.1
Release:        %autorelease
Summary:        Library for utilization of compressed safetensors of neural network models
License:        Apache-2.0
URL:            https://github.com/vllm-project/compressed-tensors
#!RemoteAsset:  sha256:a8e93054e8a5ec49c980b09ed36c4c1249b4a8ee167920a8e461c4da26e78d99
Source0:        https://files.pythonhosted.org/packages/source/c/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{pypi_name}

# Replace the auto-generated generic torch requirement with python-torch-backend
# (provided by both the CPU and ROCm torch flavors).
%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(psutil)

Requires:       python-torch-backend >= 1.7.0
Requires:       python3dist(psutil)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
A safetensors extension to efficiently store sparse quantized tensors on disk.

%prep -a
sed -i 's/setuptools_scm==8.2.0/setuptools_scm>=8.2.0/g' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
