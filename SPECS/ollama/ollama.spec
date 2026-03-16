# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: misaka00251 <liuxin@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%bcond rocm 1

%define _name           ollama
%define go_import_path  github.com/ollama/ollama

# Ollama bundles some ggml libs
# They should be kept private and the scans of these files should be disabled
%global __provides_exclude_from ^%{_exec_prefix}/lib/ollama/.*\\.so(\\..*)?$
%global __requires_exclude ^libggml-base\\.so\\.0\\(\\).*

Name:           ollama
Version:        0.13.5
Release:        %autorelease
Summary:        Get up and running with OpenAI gpt-oss, DeepSeek-R1, Gemma 3 and other models.
License:        Apache-2.0 AND MIT
URL:            https://github.com/ollama/ollama
#!RemoteAsset
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildSystem:    golang

BuildOption(prep):  -n %{_name}-%{version}

BuildRequires:  cmake
BuildRequires:  fdupes
BuildRequires:  gcc-c++
BuildRequires:  go
BuildRequires:  go-rpm-macros
BuildRequires:  go(github.com/agnivade/levenshtein)
BuildRequires:  go(github.com/containerd/console)
BuildRequires:  go(github.com/d4l3k/go-bfloat16)
BuildRequires:  go(github.com/dlclark/regexp2)
BuildRequires:  go(github.com/emirpasic/gods/v2)
BuildRequires:  go(github.com/gin-contrib/cors)
BuildRequires:  go(github.com/gin-gonic/gin)
BuildRequires:  go(github.com/google/go-cmp)
BuildRequires:  go(github.com/google/uuid)
BuildRequires:  go(github.com/mattn/go-runewidth)
BuildRequires:  go(github.com/nlpodyssey/gopickle)
BuildRequires:  go(github.com/olekukonko/tablewriter) < 1.0.0
BuildRequires:  go(github.com/pdevine/tensor)
BuildRequires:  go(github.com/spf13/cobra)
BuildRequires:  go(github.com/stretchr/testify)
BuildRequires:  go(github.com/x448/float16)
BuildRequires:  go(golang.org/x/crypto)
BuildRequires:  go(golang.org/x/image)
BuildRequires:  go(golang.org/x/mod)
BuildRequires:  go(golang.org/x/sync)
BuildRequires:  go(golang.org/x/term)
BuildRequires:  go(golang.org/x/text)
BuildRequires:  go(golang.org/x/tools)
BuildRequires:  go(gonum.org/v1/gonum)
BuildRequires:  go(google.golang.org/protobuf)
BuildRequires:  ninja

%if %{with rocm}
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocsolver)
BuildRequires:  pkgconfig(libdrm_amdgpu)
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(numa)
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocminfo
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra-devel
BuildRequires:  compiler-rt
BuildRequires:  hipcc
BuildRequires:  lld-devel
BuildRequires:  llvm-devel

Requires:       hipblas
Requires:       rocblas
%endif

%patchlist
0001-ollama-0.14.2_add-riscv.patch
0002-go-riscv64.patch
# https://github.com/jkroepke/openvpn-auth-oauth2/pull/706
0003-disable-httpmuxgo121-on-newer-version-of-go.patch
0004-use-lib64-instead-of-lib.patch

%description
Ollama is an open-source platform designed to run large language models locally.
It allows users to generate text, assist with coding, and create content privately
and securely on their own devices.

%prep -a
# Remove bundled dependencies
rm -rf llama/llama.cpp/vendor

# Ollama use a mix build of cmake and go.
# Ollama binary built by go will use dlopen to load *.so built by cmake.
# Building order is not important.
%build -a
%cmake \
    -G Ninja \
    -W no-dev \
%if %{with rocm}
    -DCMAKE_HIP_COMPILER=%{rocmllvm_bindir}/clang++ \
    -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
%endif

%cmake_build

%install
%buildsystem_golang_install
%cmake_install
rm -rvf %{buildroot}%{_bindir}/lib*.so


%files
%license LICENSE*
%doc README*
%{_bindir}/%{_name}
%dir %{_exec_prefix}/lib/ollama
%{_exec_prefix}/lib/ollama/*

%changelog
%{?autochangelog}
