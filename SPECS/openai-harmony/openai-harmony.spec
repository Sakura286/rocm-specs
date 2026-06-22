# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname openai-harmony
%global pypi_name openai_harmony

# Vendored crate sources generated from Cargo.lock:
#   cd <source> && cargo vendor --versioned-dirs vendor/ && tar czf ... vendor/
%global vendor_tarball %{srcname}-%{version}-vendor.tar.gz

Name:           python-%{srcname}
Version:        0.0.8
Release:        %autorelease
Summary:        OpenAI's response format for its open-weight model series gpt-oss
License:        Apache-2.0
URL:            https://github.com/openai/harmony
#!RemoteAsset:  sha256:6e43f98e6c242fa2de6f8ea12eab24af63fa2ed3e89c06341fb9d92632c5cbdf
Source0:        https://files.pythonhosted.org/packages/source/o/%{srcname}/%{pypi_name}-%{version}.tar.gz
Source1:        %{vendor_tarball}
BuildSystem:    pyproject

BuildOption(install):  -l %{pypi_name} -L

BuildRequires:  cargo
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(maturin)
BuildRequires:  python3dist(pip)
BuildRequires:  rust
BuildRequires:  rust-rpm-macros

Requires:       python3dist(pydantic) >= 2.11.7

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
OpenAI's response format for its open-weight model series gpt-oss. The harmony
format enables the model to output to multiple different channels for chain of
thought, and tool calling preambles along with regular responses. The majority
of the rendering and parsing is built in Rust for performance and exposed to
Python through thin pyo3 bindings.

%prep -a
tar -xf %{SOURCE1}
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor/"
EOF

# target-lexicon 0.13.2 does not recognise the riscv64a23 target triple used on
# openRuyi riscv64 builders (-march=rva23u64).  Map it to Riscv64gc which is a
# close superset of the RVA23 profile.
sed -i 's/"riscv64gc" => Riscv64gc,/"riscv64a23" => Riscv64gc,\n            "riscv64gc" => Riscv64gc,/' \
    vendor/target-lexicon-0.13.2/src/targets.rs

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
