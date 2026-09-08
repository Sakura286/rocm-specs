# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tilelang
%global toolchain clang
%global buddy_llvm_prefix %{_libdir}/buddy-compiler/llvm
# TVM and the MLIR backend are large native libraries.
%global _lto_cflags %{nil}

Name:           python-%{srcname}
# First release after the RuyiAI-Stack backend's upstream base (0924dab6).
Version:        0.1.9
Release:        %autorelease
Summary:        Tile programming language with ROCm and RISC-V MLIR backends
License:        MIT AND Apache-2.0 AND BSD-3-Clause
URL:            https://github.com/tile-ai/tilelang
VCS:            git:https://github.com/tile-ai/tilelang.git
#!RemoteAsset:  sha256:287f727c913bb648fcf6c1968809ba3390e55eeed257a5c6bb9a80bc05966af4
Source0:        https://github.com/tile-ai/tilelang/releases/download/v%{version}/%{srcname}-%{version}.tar.gz
# RuyiAI-Stack/tilelang-riscv through 0b7d66eb, rebased onto this release.
Patch1000:      1000-riscv-mlir-backend.patch
Patch1001:      1001-riscv-mlir-codegen.patch
Patch1002:      1002-riscv-tests.patch
Patch2000:      2000-openruyi-toolchain.patch
Patch2001:      2001-system-tvm-ffi.patch
BuildSystem:    pyproject

BuildOption(build):  -Ccmake.define.USE_CUDA=OFF
BuildOption(build):  -Ccmake.define.USE_ROCM=%{_prefix}
BuildOption(build):  -Ccmake.define.USE_LLVM=OFF
BuildOption(build):  -Ccmake.define.USE_PYPI_Z3=OFF
BuildOption(build):  -Ccmake.define.TILELANG_USE_HIP_STUBS=ON
BuildOption(build):  -Ccmake.define.TILELANG_RISCV_MLIR_MODE=ON
BuildOption(build):  -Ccmake.define.TILELANG_RISCV_LLVM_ROOT=%{buddy_llvm_prefix}
BuildOption(build):  -Ccmake.define.CMAKE_SKIP_INSTALL_RPATH=OFF
BuildOption(install):  %{srcname}
# Submodules include optional GPU integrations and vendored TVM utilities;
# the root import plus dedicated RISC-V tests cover the supported build.
BuildOption(check):  -t

BuildRequires:  buddy-compiler-llvm = 0.0.8
BuildRequires:  clang
BuildRequires:  cmake >= 3.26.1
BuildRequires:  ninja
BuildRequires:  patchelf
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(z3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(apache-tvm-ffi) >= 0.1.10
BuildRequires:  python3dist(cython) >= 3.1
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(scikit-build-core)
BuildRequires:  cmake(hip)
Requires:       buddy-compiler-llvm = 0.0.8
# JIT host wrappers need native headers and the system linker.
Requires:       gcc-c++
Requires:       rocm-hip-devel
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
TileLang is a domain-specific language for GPU and CPU kernels. This package
uses the official TileLang release sources with the RuyiAI-Stack RISC-V
backend, which lowers TileLang kernels through structured MLIR to native
RISC-V code. ROCm support is also enabled. The experimental RISC-V backend
is selected explicitly with target="riscv".

%prep
%autosetup -p1 -n %{srcname}-%{version}
sed -i 's|@BUDDY_LLVM_PREFIX@|%{buddy_llvm_prefix}|g' tilelang/tladapter/toolchain.py
# Run the backend tests against the installed wheel without the source-tree
# import override in testing/conftest.py.
cp -a testing/python/riscv rpm-tests

%generate_buildrequires
export NO_VERSION_LABEL=1
%pyproject_buildrequires

%build -p
export NO_VERSION_LABEL=1
export CMAKE_GENERATOR=Ninja
export CMAKE_BUILD_PARALLEL_LEVEL=%{_smp_build_ncpus}
export TVM_FFI_DISABLE_TORCH_C_DLPACK=1

%check -p
export TVM_FFI_DISABLE_TORCH_C_DLPACK=1
export TILELANG_CACHE_DIR="$PWD/rpm-cache"

%check -a
%pytest --confcutdir=rpm-tests rpm-tests/test_riscv_target_parse.py rpm-tests/test_riscv_toolchain.py rpm-tests/test_riscv_tladapter_pipeline.py rpm-tests/codegen_ops

%files -f %{pyproject_files}
%doc README.md docs/get_started/BuildOnSG2044.md
%license LICENSE THIRDPARTYNOTICES.txt

%changelog
%autochangelog
