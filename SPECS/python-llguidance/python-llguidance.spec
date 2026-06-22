# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname llguidance

Name:           python-%{srcname}
Version:        1.7.5
Release:        %autorelease
Summary:        Bindings for the Low-level Guidance (llguidance) Rust library
License:        MIT
URL:            https://pypi.org/project/llguidance/
VCS:            git:https://github.com/microsoft/llguidance

#!RemoteAsset:  sha256:afaa8f979708cd546c762f06a4fe4748e5ef7f06ed45875dabe7db8f07b73645
Source0:        https://files.pythonhosted.org/packages/source/l/%{srcname}/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:9d4625166510b605da281e16c88e91a23d631cc2082db345dd45e7283e48db20
Source1:        https://github.com/software-vendor/python-%{srcname}-vendor/releases/download/vendor-%{version}/%{srcname}-%{version}-vendor.tar.bz2

BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(huggingface-hub)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(torch)
BuildRequires:  python3dist(transformers)
BuildRequires:  rust
BuildRequires:  cargo

# TODO: llama_cpp not yet packaged
# mlx is Apple-specific
BuildOption(check):  -e "llguidance.llamacpp" -e "llguidance.mlx"

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Low-level Guidance (llguidance) is a Rust library providing fast
structured outputs for LLM inference and guidance.

%prep
%autosetup -n %{srcname}-%{version} -a1

mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
%autochangelog
