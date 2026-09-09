# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global toolchain clang
%global llvm_commit 2d26d272a0ff74b8c81eac0607b07f98b82ecc46
%global buddy_prefix %{_libdir}/buddy-compiler
%global llvm_prefix %{buddy_prefix}/llvm

# LLVM and MLIR are linked statically into Buddy and its Python CAPI library.
# Avoid a second LTO pass and the memory cost of dwz on these large binaries.
%global _lto_cflags %{nil}
%global _find_debuginfo_dwz_opts %{nil}
# The private SDK must not satisfy system LLVM/MLIR dependency requests.
%global __provides_exclude_from ^%{buddy_prefix}/.*$
# These DSOs and their consumers are shipped together in the private LLVM RPM.
# Match its hidden Provides with Requires filtering, retaining system library deps.
%global __requires_exclude ^lib((MLIRPythonCAPI|clang|mlir_float16_utils)\.so\.24\.0git|(MLIRPythonSupport-mlir|nanobind-mlir)\.so).*$

Name:           buddy-compiler
Version:        0.0.8
Release:        %autorelease
Summary:        MLIR-based compiler framework for domain-specific architectures
License:        Apache-2.0 AND (Apache-2.0 WITH LLVM-exception OR NCSA) AND MIT AND BSD-3-Clause
URL:            https://github.com/buddy-compiler/buddy-mlir
#!RemoteAsset:  sha256:35e508e883f5ca33c8c6177476fddda58f3e6a257e2c21427247712270a02982
Source0:        %{url}/archive/refs/tags/release/v%{version}.tar.gz
# This is the LLVM submodule pinned by the release, not a system LLVM ABI.
# LLVM 24 has no matching release tarball for this development revision.
#!RemoteAsset:  sha256:b5b208a5217744bcafa73dbc26bf58d737936401cf4306206ad3a04a424859be
Source1:        https://github.com/llvm/llvm-project/archive/%{llvm_commit}.tar.gz
# Match system Clang GCC discovery for the bootstrapped OpenMP compiler.
Patch2000:      2000-clang-find-openruyi-gcc.patch
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DBUILD_SHARED_LIBS=OFF
BuildOption(conf):  -DCMAKE_INSTALL_PREFIX=%{buddy_prefix}
BuildOption(conf):  -DCMAKE_INSTALL_BINDIR=%{_bindir}
BuildOption(conf):  -DCMAKE_INSTALL_LIBDIR=lib
BuildOption(conf):  -DCMAKE_INSTALL_INCLUDEDIR=include
BuildOption(conf):  -DLLVM_DIR="$PWD/llvm-build/lib/cmake/llvm"
BuildOption(conf):  -DMLIR_DIR="$PWD/llvm-build/lib/cmake/mlir"
BuildOption(conf):  -DLLVM_EXTERNAL_LIT="$PWD/llvm-build/bin/llvm-lit"
BuildOption(conf):  -DLLVM_ENABLE_ASSERTIONS=ON
BuildOption(conf):  -DLLVM_PARALLEL_LINK_JOBS=2
BuildOption(conf):  -DBUDDY_PACKAGE_VERSION=%{version}
BuildOption(conf):  -DBUDDY_MLIR_ENABLE_PYTHON_PACKAGES=ON
BuildOption(conf):  -DBUDDY_ENABLE_TESTS=ON
BuildOption(conf):  -DPython3_EXECUTABLE=%{__python3}
BuildOption(conf):  -DPython_EXECUTABLE=%{__python3}
# Do not specialize installed DIP/DAP kernels for the OBS worker's CPU.
BuildOption(conf):  -DHAVE_SSE=OFF
BuildOption(conf):  -DHAVE_AVX2=OFF
BuildOption(conf):  -DHAVE_AVX512=OFF
BuildOption(conf):  -DHAVE_AMX=OFF
BuildOption(conf):  -DHAVE_NEON=OFF
BuildOption(conf):  -DHAVE_LOCAL_RVV=OFF
BuildOption(conf):  -DBUDDY_DIP_OPT_STRIP_MINING=1

BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  flatbuffers
BuildRequires:  lld
BuildRequires:  ninja
BuildRequires:  pkgconfig(flatbuffers)
BuildRequires:  pkgconfig(numa)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  (python3dist(nanobind) >= 2.9 with python3dist(nanobind) < 3)
BuildRequires:  (python3dist(numpy) >= 2 with python3dist(numpy) < 2.5)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(torch) >= 2.10
BuildRequires:  python3-rpm-macros

Requires:       %{name}-llvm%{?_isa} = %{version}-%{release}
Provides:       bundled(llvm) = 24.0.0~git2d26d27

%description
Buddy is an MLIR-based compiler framework connecting domain-specific languages
with domain-specific architectures. It includes optimization and translation
tools, custom MLIR dialects, RAX model utilities and inference entry points.

%package        llvm
Summary:        Private LLVM and MLIR SDK for Buddy Compiler

%description    llvm
The exact LLVM/MLIR source revision required by Buddy Compiler, built from
source and installed in a private prefix. It includes Clang, MLIR tools,
OpenMP, headers and libraries for use with Buddy without replacing system LLVM.

%package        devel
Summary:        C++ interfaces and libraries for Buddy Compiler
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(flatbuffers)

%description    devel
C++ interface headers, static libraries and CMake configuration for Buddy.
The matching LLVM headers and libraries are provided by buddy-compiler-llvm.

%package        -n python3-buddy-compiler
Summary:        Python frontend and MLIR bindings for Buddy Compiler
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       (python3dist(numpy) >= 2 with python3dist(numpy) < 2.5)
Requires:       python3dist(torch) >= 2.10
Provides:       python3dist(buddy) = %{version}

%description    -n python3-buddy-compiler
The buddy.compiler Python frontend and buddy_mlir dialect bindings, including
PyTorch graph import and MLIR execution support. Model weights and optional
model-specific Python dependencies are not included.

%prep
%autosetup -N -n buddy-mlir-release-v%{version} -a 1
rmdir llvm
mv llvm-project-%{llvm_commit} llvm
%patch -P 2000 -p1 -d llvm
# nanobind compiles its runtime into the private Python extension libraries.
cp %{_licensedir}/python-nanobind/LICENSE nanobind-LICENSE
# The upstream CMake config assumes its tools are below the install prefix.
sed -i 's|${PACKAGE_PREFIX_DIR}/bin|@CMAKE_INSTALL_BINDIR@|' cmake/BuddyMLIRConfig.cmake.in
# Retain LLVM_LIBS_DIR overrides, but make the installed default independent
# of the upstream source/build tree layout.
sed -i \
    -e 's|../../../../llvm/build/lib/|%{llvm_prefix}/lib/|' \
    -e 's|../../../lib|%{buddy_prefix}/lib|' \
    frontend/Python/frontend.py

%conf -p
# Buddy consumes LLVM's build-tree exports, including MLIR test libraries and
# Python source declarations; build the pinned dependency before configuring it.
%cmake -S llvm/llvm -B llvm-build -G Ninja \
    -DCMAKE_INSTALL_PREFIX=%{llvm_prefix} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_INSTALL_BINDIR=bin \
    -DBUILD_SHARED_LIBS=OFF \
    -DLLVM_ENABLE_PROJECTS='mlir;clang' \
    -DLLVM_ENABLE_RUNTIMES=openmp \
    -DLLVM_ENABLE_PER_TARGET_RUNTIME_DIR=OFF \
    -DLLVM_TARGETS_TO_BUILD='host;RISCV' \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DLLVM_BUILD_LLVM_DYLIB=OFF \
    -DLLVM_LINK_LLVM_DYLIB=OFF \
    -DLLVM_USE_LINKER=lld \
    -DLLVM_INCLUDE_TESTS=ON \
    -DLLVM_BUILD_TESTS=OFF \
    -DLLVM_INCLUDE_BENCHMARKS=OFF \
    -DLLVM_INCLUDE_EXAMPLES=OFF \
    -DLLVM_INSTALL_UTILS=ON \
    -DLLVM_PARALLEL_LINK_JOBS=2 \
    -DMLIR_ENABLE_BINDINGS_PYTHON=ON \
    -DMLIR_INCLUDE_TESTS=ON \
    -DOPENMP_ENABLE_LIBOMPTARGET=OFF \
    -DPython3_EXECUTABLE=%{__python3} \
    -DPython_EXECUTABLE=%{__python3}
cmake --build llvm-build --parallel %{_smp_build_ncpus}

%install -a
DESTDIR=%{buildroot} cmake --install llvm-build
mkdir -p %{buildroot}%{python3_sitearch}
mv %{buildroot}%{buddy_prefix}/python_packages/buddy_mlir %{buildroot}%{python3_sitearch}/
rmdir %{buildroot}%{buddy_prefix}/python_packages
# Upstream installs the common CAPI DSO in lib, but extensions use $ORIGIN.
mv %{buildroot}%{buddy_prefix}/lib/libBuddyMLIRPythonCAPI.so* \
    %{buildroot}%{python3_sitearch}/buddy_mlir/_mlir_libs/
cp -a %{__cmake_builddir}/python_packages/buddy %{buildroot}%{python3_sitearch}/

%check -a
# CTest covers the model-independent server; lit covers native compiler passes.
# Model examples need external weights and optional Python packages.
llvm-build/bin/llvm-lit -v %{__cmake_builddir}/tests --filter='^BUDDY :: (Conversion|Dialect|Interface)/'
PYTHONPATH=%{buildroot}%{python3_sitearch} %{__python3} -c \
    'import buddy.compiler.frontend; import buddy_mlir.ir; from buddy_mlir.dialects import bud, dap, dip, rvv'
%{buildroot}%{_bindir}/buddy-opt --version
%{buildroot}%{_bindir}/buddy-llc --version

%files
%license LICENSE thirdparty/include/AudioFile.h
%doc README.md
%{_bindir}/buddy-*
%{_bindir}/rax-pack
%{_bindir}/rax-inspect
%dir %{buddy_prefix}
%dir %{buddy_prefix}/lib
%{buddy_prefix}/lib/libbuddy_external_rng.so

%files llvm
%license llvm/LICENSE.TXT nanobind-LICENSE
%{llvm_prefix}/

%files devel
%{buddy_prefix}/include/
%{buddy_prefix}/lib/*.a
%{buddy_prefix}/lib/cmake/
%{buddy_prefix}/lib/objects-*/
%{buddy_prefix}/src/

%files -n python3-buddy-compiler
%license nanobind-LICENSE
%{python3_sitearch}/buddy/
%{python3_sitearch}/buddy_mlir/

%changelog
%autochangelog
