# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# TEMPORARY DEBUG SHIM -- not for production.
#
# python-torch-rocm deliberately drops the auto-generated python3dist(torch)
# provide (python-torch.spec %__provides_exclude) so the generic torch identity
# resolves to CPU torch.  As a side effect, every Base package that requires
# python3dist(torch) becomes uninstallable alongside the ROCm torch.
#
# This empty package re-supplies that capability AND pulls in python-torch-rocm,
# so unmodified Base torch-consumers resolve against the ROCm torch without a
# per-package fork.  Caveat: it opens python3dist(torch) globally, so a package
# carrying a compiled torch C++ extension would also install but be ABI-broken;
# pure-python consumers are fine.  See [[rocm-torch-backend-fork-recipe]] for the
# per-package alternative.

# Track the real torch version so version-bounded requires (>=1.7, >=2.0, ...)
# are satisfied.
%global torch_version 2.11.0

Name:           python-torch-rocm-shim
Version:        %{torch_version}
Release:        %autorelease
Summary:        Debug shim that satisfies python3dist(torch) via python-torch-rocm
License:        MulanPSL-2.0
URL:            https://github.com/Sakura286/rocm-specs
BuildArch:      noarch

Requires:       python-torch-rocm

# Both the generic and the ABI-specific dist names -- Base consumers require the
# ABI-specific python3.13dist(torch), so the second provide is the one that
# actually matters.  Hardcoded to 3.13 (the current openRuyi python ABI): the
# %%{python3_version} macro expands to empty in this metapackage's buildroot,
# which silently produced a useless "pythondist(torch)" provide.
Provides:       python3dist(torch) = %{version}
Provides:       python3.13dist(torch) = %{version}

%description
Empty compatibility shim that makes python3dist(torch) resolvable on a ROCm
system by depending on python-torch-rocm.  Intended for temporary debugging
only -- prefer per-package forks for anything lasting.

%files

%changelog
%autochangelog
