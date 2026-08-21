# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Originally extracted from Fedora Project
# Authors: The Fedora Project Contributors
# riscv64 build hints contributed by the openRuyi AI working group.

%global srcname triton

# Triton pins an exact, in-development LLVM *commit* (not a release version).
# It calls unstable MLIR/LLVM C++ internals, so it only builds against that one
# revision; no released distro LLVM (nor ROCm's bundled LLVM) matches it, and it
# additionally needs MLIR and LLD.  We therefore build LLVM from source at the
# pinned commit and link it statically into the Triton extension, exactly like
# upstream's CI does.
#
# !!! WHEN BUMPING %%{version} !!!
# Triton and LLVM must move together.  Set %%{llvm_commit} to the value of
# cmake/llvm-hash.txt for the new Triton tag and refresh Source1's sha256.  A
# mismatched LLVM will fail to compile or crash at runtime.
%global llvm_commit 1f126a6dea50d185c0781743a667390037ae88bd

# openRuyi clang/lld 22 bootstraps the private LLVM snapshot.  They are
# build-only and must not become RPM runtime dependencies of python-triton.
%global bootstrap_llvm_maj_ver 22
%global bootstrap_llvm_bindir %{_libdir}/llvm%{bootstrap_llvm_maj_ver}/bin

# Build the bundled LLVM and the Triton extension with clang.
%global toolchain clang

# The bundled static LLVM is large; drop LTO and skip the dwz pass which can
# exhaust memory on the giant libtriton.so.
%global _lto_cflags %{nil}
%define _find_debuginfo_dwz_opts %{nil}

Name:           python-%{srcname}
Version:        3.7.1
Release:        %autorelease
Summary:        A language and compiler for custom Deep Learning operations
# Triton itself is MIT.  The statically bundled LLVM/MLIR/LLD is
# "Apache-2.0 WITH LLVM-exception OR NCSA"; pybind11 headers are BSD-3-Clause.
License:        MIT AND (Apache-2.0 WITH LLVM-exception OR NCSA) AND BSD-3-Clause
URL:            https://github.com/triton-lang/triton
VCS:            git:%{url}.git

#!RemoteAsset:  sha256:21cab714d4fc9579b728f4d597660c9598fbbd52c1154896c71d2d42f9b61626
Source0:        %{url}/releases/download/v%{version}/%{srcname}-%{version}.tar.gz
# NOTE: codeload generates llvm-project's commit archive on the fly; the
# github.com/.../archive redirect to it times out behind the build proxy, so
# point straight at codeload (identical bytes, same sha256).
#!RemoteAsset:  sha256:b6aa9fbc954895bbd69374529593bbcdc4342b0812d8884698bbfd3d92d3426d
Source1:        https://codeload.github.com/llvm/llvm-project/tar.gz/%{llvm_commit}#/llvm-project-%{llvm_commit}.tar.gz

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

# Bootstrap compiler for the private LLVM snapshot and the Triton extension.
# These are build-only; the finished RPM must not Require llvm22/mlir22/lld22.
BuildRequires:  clang(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  lld(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  libstdc++-devel
BuildRequires:  cmake
BuildRequires:  ninja
# JSON_SYSPATH still uses the distro header even with Proton disabled.
BuildRequires:  nlohmann-json

# Libraries used by the bundled LLVM.
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libzstd)

# Triton JIT-compiles a small CPU launcher at runtime, loads HIP dynamically,
# and consumes ROCm device bitcode while compiling AMDGPU kernels.  The GPU
# path uses the statically linked LLD + AMDGPU code generator.
Requires:       gcc
Requires:       pkgconfig(python3)
Requires:       cmake(hip)
Requires:       rocm-device-libs

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%patchlist
# Distro cmake/ninja/pybind11; disable -Werror.  Does not require system LLVM.
2000-Use-system-build-tools.patch
# Link X86 codegen libs on riscv64 so llvm::InitializeAllTargets() resolves.
2001-Add-riscv64-host-codegen-libraries.patch
# AMD-only/offline packaging.
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

%prep -a
# Unpack the pinned LLVM next to the Triton tree (built in %%build).
tar -xf %{SOURCE1}

# Drop any pre-generated metadata shipped in the tarball.
rm -rf %{srcname}.egg-info

%generate_buildrequires
%pyproject_buildrequires

# Build the pinned LLVM+MLIR+LLD first, then let the pyproject build system
# compile the Triton wheel against it.  Both run in the same shell, so the
# environment exported here reaches %%pyproject_wheel.
%build -p
# Point PATH/CC/CXX at the compat clang 22 prefix so OBS does not pick an
# ambiguous default compiler.  None of these become runtime dependencies.
export PATH="%{bootstrap_llvm_bindir}:${PATH}"
export CC="%{bootstrap_llvm_bindir}/clang"
export CXX="%{bootstrap_llvm_bindir}/clang++"

llvm_src="$(pwd)/llvm-project-%{llvm_commit}"
llvm_install="$(pwd)/llvm-install"

# Cap parallelism by available memory: LLVM/MLIR compile units and the final
# Triton link are memory hungry and will thrash or OOM otherwise.
mem_gb=$(awk '/MemTotal/ {print int($2/1024/1024)}' /proc/meminfo)
compile_jobs=$(nproc)
mem_jobs=$(( 1 + mem_gb / 2 ))
[ "$mem_jobs" -lt "$compile_jobs" ] && compile_jobs=$mem_jobs
[ "$compile_jobs" -lt 1 ] && compile_jobs=1
# Linking the static archives needs far more memory per job.
link_jobs=$(( 1 + mem_gb / 16 ))
[ "$link_jobs" -lt 1 ] && link_jobs=1

%ifarch x86_64
llvm_targets="X86;AMDGPU;NVPTX"
%endif
%ifarch riscv64
# X86 is required by the riscv64 codegen-libs patch; AMDGPU drives the ROCm
# backend; NVPTX is always linked by Triton's core; RISCV is the host.
llvm_targets="RISCV;X86;AMDGPU;NVPTX"
%endif

cmake -S "$llvm_src/llvm" -B "$llvm_src/build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$llvm_install" \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DLLVM_USE_LINKER=lld \
    -DLLVM_ENABLE_PROJECTS="mlir;lld" \
    -DLLVM_TARGETS_TO_BUILD="$llvm_targets" \
    -DLLVM_ENABLE_ASSERTIONS=OFF \
    -DBUILD_SHARED_LIBS=OFF \
    -DLLVM_BUILD_LLVM_DYLIB=OFF \
    -DLLVM_INSTALL_UTILS=ON \
    -DLLVM_ENABLE_ZSTD=ON \
    -DLLVM_INCLUDE_BENCHMARKS=OFF \
    -DLLVM_INCLUDE_EXAMPLES=OFF \
    -DLLVM_INCLUDE_TESTS=OFF \
    -DLLVM_PARALLEL_COMPILE_JOBS=$compile_jobs \
    -DLLVM_PARALLEL_LINK_JOBS=$link_jobs
cmake --build "$llvm_src/build" --target install -- -j$compile_jobs

# Point Triton at the freshly built LLVM.  Do not leak system LLVM 22 paths.
export LLVM_SYSPATH="$llvm_install"
export PATH="$llvm_install/bin:$PATH"
export JSON_SYSPATH="%{_prefix}"
export PYBIND11_SYSPATH="%{_prefix}"
export PYBIND11_CMAKE_DIR="%{_datadir}/cmake/pybind11"
export MAX_JOBS=$compile_jobs
export TRITON_PARALLEL_LINK_JOBS=$link_jobs
export TRITON_BUILD_WITH_CLANG_LLD=ON
export TRITON_BUILD_WITH_CCACHE=OFF
export TRITON_BUILD_PROTON=OFF
export TRITON_CODEGEN_BACKENDS=amd
export TRITON_OFFLINE_BUILD=1
export TRITON_APPEND_CMAKE_ARGS="-DTRITON_BUILD_EXAMPLES=OFF -DTRITON_BUILD_TOOLS=OFF -DTRITON_BUILD_UT=OFF"

%files -f %{pyproject_files}
%doc README.md
%license llvm-project-%{llvm_commit}/llvm/LICENSE.TXT

%changelog
%autochangelog
