# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Originally extracted from Fedora Project
# Authors: The Fedora Project Contributors
# riscv64 build hints contributed by the openRuyi AI working group.

%global srcname triton
%global llvm_maj_ver 22

# libtriton.so is large even with a shared system LLVM.  Avoid LTO and the dwz
# pass to keep peak link/post-processing memory bounded on OBS workers.
%global _lto_cflags %{nil}
%define _find_debuginfo_dwz_opts %{nil}

Name:           python-%{srcname}
Version:        3.7.1
Release:        %autorelease
Summary:        A language and compiler for custom Deep Learning operations
# Triton itself is MIT; pybind11 headers compiled into the extension are
# BSD-3-Clause.  LLVM 22 is dynamically linked from the distro package.
License:        MIT AND BSD-3-Clause
URL:            https://github.com/triton-lang/triton
VCS:            git:%{url}.git

#!RemoteAsset:  sha256:21cab714d4fc9579b728f4d597660c9598fbbd52c1154896c71d2d42f9b61626
Source0:        %{url}/releases/download/v%{version}/%{srcname}-%{version}.tar.gz

BuildSystem:    pyproject
BuildOption(install):  %{srcname}
# MLIR helper shared libraries are not Python extension modules.
BuildOption(check):  -e 'triton.instrumentation.*'

# Python build backend and import checks.
BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(pybind11)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(torch)
# Select the target project's unversioned OpenMP compatibility package.  It
# provides %%{_libdir}/libomp.so for python-torch and requires the LLVM 22
# runtime, avoiding Base's ambiguous libomp22/libomp23 provider choice.
BuildRequires:  libomp

# Triton host compiler and the distro LLVM/MLIR 22 stack.
BuildRequires:  gcc-c++
BuildRequires:  lld%{llvm_maj_ver}-devel
BuildRequires:  llvm%{llvm_maj_ver}-devel
BuildRequires:  llvm%{llvm_maj_ver}-static
BuildRequires:  mlir%{llvm_maj_ver}-devel
BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  nlohmann-json

# Libraries used by LLVM and Triton.
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libzstd)

# Triton JIT-compiles a small CPU launcher at runtime, loads HIP dynamically,
# and consumes ROCm device bitcode while compiling AMDGPU kernels.
Requires:       gcc
Requires:       pkgconfig(python3)
Requires:       cmake(hip)
Requires:       rocm-device-libs

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

# These openRuyi-specific patches are rebased from the successful
# home:nekorouter/triton-llvm22 OBS build and openRuyi PR #861.
%patchlist
2000-Use-system-build-tools.patch
2001-Adjust-for-MLIR-22-API.patch
2002-Link-dynamically-against-system-LLVM.patch
2003-Build-only-the-AMD-backend.patch
# Keep the pure-Python descriptor types imported by the common native
# specialization code; this does not restore the NVIDIA codegen backend.
2004-Retain-NVIDIA-Gluon-descriptor-types.patch

%description
Triton is a language and compiler for writing highly efficient custom
Deep-Learning primitives. The aim of Triton is to provide an open-source
environment to write fast code at higher productivity than CUDA, but also
with higher flexibility than other existing DSLs.

This build ships the AMD ROCm (HIP) backend.

%generate_buildrequires
%pyproject_buildrequires

%build -p
export LLVM_CONFIG="%{_libdir}/llvm%{llvm_maj_ver}/bin/llvm-config-%{llvm_maj_ver}"
export LLVM_SYSPATH="%{_libdir}/llvm%{llvm_maj_ver}"
export PATH="%{_libdir}/llvm%{llvm_maj_ver}/bin:${PATH}"
export JSON_SYSPATH="%{_prefix}"
export PYBIND11_SYSPATH="%{_prefix}"
export PYBIND11_CMAKE_DIR="%{_datadir}/cmake/pybind11"
export CC=gcc
export CXX=g++
export TRITON_CODEGEN_BACKENDS=amd
export TRITON_BUILD_PROTON=OFF
export TRITON_BUILD_WITH_CCACHE=OFF
export TRITON_OFFLINE_BUILD=1
export MAX_JOBS="${MAX_JOBS:-4}"
export CFLAGS="${CFLAGS} -fuse-ld=lld"
export CXXFLAGS="${CXXFLAGS} -fuse-ld=lld"
export LDFLAGS="${LDFLAGS} -fuse-ld=lld"
export TRITON_APPEND_CMAKE_ARGS="-DTRITON_BUILD_EXAMPLES=OFF -DTRITON_BUILD_TOOLS=OFF -DTRITON_BUILD_UT=OFF -DLLVM_LINK_LLVM_DYLIB=ON -DMLIR_LINK_MLIR_DYLIB=ON -DCMAKE_BUILD_RPATH=%{_libdir}/llvm%{llvm_maj_ver}/lib -DCMAKE_INSTALL_RPATH=%{_libdir}/llvm%{llvm_maj_ver}/lib -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON"

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog
