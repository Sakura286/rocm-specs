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
%global llvm_commit f6ded0be897e2878612dd903f7e8bb85448269e5

# Build everything (the bundled LLVM and the Triton extension) with clang,
# matching the rest of the openRuyi ROCm stack.
%global toolchain clang

# The bundled static LLVM is large; drop LTO and skip the dwz pass which can
# exhaust memory on the giant libtriton.so.
%global _lto_cflags %{nil}
%define _find_debuginfo_dwz_opts %{nil}

Name:           python-%{srcname}
Version:        3.6.0
Release:        %autorelease
Summary:        A language and compiler for custom Deep Learning operations
# Triton itself is MIT.  The statically bundled LLVM/MLIR/LLD is
# "Apache-2.0 WITH LLVM-exception OR NCSA"; pybind11 headers are BSD-3-Clause.
License:        MIT AND (Apache-2.0 WITH LLVM-exception OR NCSA) AND BSD-3-Clause
URL:            https://github.com/triton-lang/triton

# Triton's PyPI sdist does not ship the C++ / third_party sources needed to
# build, so the source is taken from the GitHub release tag instead.
#!RemoteAsset:  sha256:be270ed11ca5a8fbd9d7941c5bbe9a23a9f6e2ffd372c8398346928bee464774
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
# NOTE: codeload generates llvm-project's commit archive on the fly; the
# github.com/.../archive redirect to it times out behind the build proxy, so
# point straight at codeload (identical bytes, same sha256).
#!RemoteAsset:  sha256:f63c624aa63eda73508b9df2be2a6945ea4fddbee58615fbe1cd747b6884dd5e
Source1:        https://github.com/llvm/llvm-project/archive/%{llvm_commit}.tar.gz

# Build only the AMD/ROCm backend and never reach out to the network for the
# NVIDIA CUDA toolchain.
Patch0:         0001-Build-only-the-AMD-ROCm-backend-offline.patch
# Link the X86 codegen libraries on the riscv64 host so that
# llvm::InitializeAllTargets() resolves at import time.
Patch1:         0002-Add-riscv64-host-codegen-libraries.patch
BuildSystem:    pyproject

BuildOption(install):  %{srcname}

# --- Python build backend --------------------------------------------------
BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(pybind11)

# --- Toolchain for the bundled LLVM and the Triton extension ---------------
BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  libstdc++-devel
BuildRequires:  compiler-rt
BuildRequires:  cmake
BuildRequires:  ninja

# --- Libraries the bundled LLVM links against ------------------------------
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libzstd)

# --- Runtime ROCm stack ----------------------------------------------------
# Triton JIT-compiles kernels at runtime: the GPU path uses the statically
# linked LLD + AMDGPU code generator, but the per-kernel CPU launcher shim is
# compiled on the fly (triton/runtime/build.py) with a host C compiler against
# the Python headers, and the HIP runtime is dlopen'd.
Requires:       gcc
Requires:       pkgconfig(python3)
Requires:       cmake(hip)
Requires:       rocm-device-libs

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

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

# Triton's CMake turns warnings into errors; a from-source LLVM occasionally
# emits new warnings, so relax this for both Triton and the embedded
# add_llvm/add_mlir targets.
sed -i -e 's@ -Werror @ @' CMakeLists.txt

# The wheel is built with --no-build-isolation, so cmake/ninja/pybind11 are
# supplied as system BuildRequires.  Strip them from build-system.requires so
# %%pyproject_buildrequires does not emit unsatisfiable python3dist(cmake<4),
# python3dist(ninja) dependencies.
sed -i -e 's@^requires = .*@requires = ["setuptools>=40.8.0", "wheel"]@' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

# Build the pinned LLVM+MLIR+LLD first, then let the pyproject build system
# compile the Triton wheel against it.  Both run in the same shell, so the
# environment exported here reaches %%pyproject_wheel.
%build -p
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
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_USE_LINKER=lld \
    -DLLVM_ENABLE_PROJECTS="mlir;lld" \
    -DLLVM_TARGETS_TO_BUILD="$llvm_targets" \
    -DLLVM_ENABLE_ASSERTIONS=OFF \
    -DBUILD_SHARED_LIBS=OFF \
    -DLLVM_BUILD_LLVM_DYLIB=OFF \
    -DLLVM_INSTALL_UTILS=ON \
    -DLLVM_ENABLE_TERMINFO=OFF \
    -DLLVM_ENABLE_ZSTD=ON \
    -DLLVM_INCLUDE_BENCHMARKS=OFF \
    -DLLVM_INCLUDE_EXAMPLES=OFF \
    -DLLVM_INCLUDE_TESTS=OFF \
    -DLLVM_PARALLEL_COMPILE_JOBS=$compile_jobs \
    -DLLVM_PARALLEL_LINK_JOBS=$link_jobs
cmake --build "$llvm_src/build" --target install -- -j$compile_jobs

# Point Triton at the freshly built LLVM and keep the build offline + ROCm-only.
export LLVM_SYSPATH="$llvm_install"
export PATH="$llvm_install/bin:$PATH"
export CC=clang
export CXX=clang++
export MAX_JOBS=$compile_jobs
export TRITON_PARALLEL_LINK_JOBS=$link_jobs
export TRITON_BUILD_WITH_CLANG_LLD=ON
export TRITON_BUILD_WITH_CCACHE=OFF
# Proton needs CUPTI/roctracer/json; not needed for a plain ROCm backend.
export TRITON_BUILD_PROTON=OFF
# Don't fetch googletest, and don't trip over new LLVM warnings.
export TRITON_APPEND_CMAKE_ARGS="-DTRITON_BUILD_UT=OFF -DLLVM_ENABLE_WERROR=OFF"

%files -f %{pyproject_files}
# Triton's own LICENSE is captured from the wheel metadata by
# %%pyproject_save_files; only the bundled LLVM license must be added by hand.
%license llvm-project-%{llvm_commit}/llvm/LICENSE.TXT
%doc README.md

%changelog
%autochangelog
