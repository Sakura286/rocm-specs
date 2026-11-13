# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.14
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

%global tensile_version 4.33.0

%bcond test 0

# Keep this in the recipe: server-generated _constraints has a service prefix.
#!BuildConstraint: hardware:jobs 32

Name:           hipsparselt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A SPARSE marshaling library
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:472546ac05a81e32d99c83c645651081c9b2cabbc3c31503cd76caa163acebd6
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/hipsparselt.tar.gz
#!RemoteAsset:  sha256:96c8233f9b4232d8208987232aa11e1f164ad5f97eca94a0f43f0916f8d59ae2
Source1:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/hipblaslt.tar.gz
# Patches applied to the bundled hipBLASLt kernel generator.
Source2:        0001-hipblaslt-tensilelite-use-system-paths.patch
Source3:        0001-hipblaslt-find-origami-package.patch
Source4:        2001-hipblaslt-tensilelite-use-system-nanobind.patch
Source5:        2000-tensilelite-add-heartbeat-during-parallel-map.patch
Source6:        2003-use-installed-stinkytofu-conversion-sources.patch
# -mf16c is an x86-only clang flag (F16C intrinsics); guard it on x86 so the
# hipSPARSELt library builds on non-x86 hosts like riscv64. cf. ollama PR #8129
Patch2000:      2000-hipsparselt-guard-mf16c-to-x86.patch
BuildSystem:    cmake

# LLVM 23's HIP bundler requires the host triple's environment field.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DCMAKE_HIP_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DBLAS_INCLUDE_DIR=%{_includedir}/flexiblas
BuildOption(conf):  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF
%if %{with test}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DHIPSPARSELT_ENABLE_CLIENT=ON
%else
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=OFF
BuildOption(conf):  -DHIPSPARSELT_ENABLE_CLIENT=OFF
%endif
BuildOption(conf):  -DBUILD_VERBOSE=ON
BuildOption(conf):  -DCMAKE_Fortran_COMPILER=gcc-fortran
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DGPU_TARGETS="gfx942;gfx950"
BuildOption(conf):  -DTensile_COMPILER=clang++
BuildOption(conf):  -DTensile_LIBRARY_FORMAT=msgpack
BuildOption(conf):  -DTensile_VERBOSE=1
BuildOption(conf):  -DHIPSPARSELT_HIPBLASLT_PATH=%{_builddir}/%{buildsubdir}/hipblaslt
BuildOption(conf):  -DHIPBLASLT_BUNDLE_PYTHON_DEPS=ON
BuildOption(conf):  -DHIPBLASLT_ENABLE_ROCROLLER=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_MXDATAGENERATOR=OFF
BuildOption(conf):  -DHIPSPARSELT_ENABLE_OPENMP=OFF
BuildOption(conf):  -DHIPSPARSELT_BUILD_TESTING=OFF
BuildOption(conf):  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/..
BuildOption(conf):  -Dnanobind_ROOT=%(python3 -m nanobind --cmake_dir)
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  rocm-hip-devel >= 7.14.1
BuildRequires:  cmake(hipsparse)
BuildRequires:  hipsparse-devel >= 7.14.1
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocr-runtime-devel >= 7.14.1
BuildRequires:  cmake(stinkytofu)
BuildRequires:  stinkytofu-devel >= 7.14.1
BuildRequires:  cmake(origami)
BuildRequires:  rocm-origami-devel >= 7.14.1
BuildRequires:  cmake(rocm_smi)
BuildRequires:  cmake(rocsparse)
BuildRequires:  rocsparse-devel >= 7.14.1
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  gcc-fortran
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  libomp-devel(major) = %{llvm_maj_ver}
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(msgpack)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(msgpack)
# nanobind is used to build the rocisa native module (build-time only)
BuildRequires:  python3dist(nanobind)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(setuptools)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocminfo
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel

%if %{with test}
BuildRequires:  chrpath
BuildRequires:  pkgconfig(openblas)
BuildRequires:  pkgconfig(gtest)
BuildRequires:  pkgconfig(gmock)
%endif

%global _description %{expand:
hipSPARSELt is a SPARSE marshaling library that provides general sparse
matrix-matrix multiplication using structured sparsity. It offers a flexible
API and supports multiple backends.
}

%description
%{_description}

%package        devel
Summary:        The hipSPARSELt development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The hipSPARSELt development package.

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}
%endif

%prep
# hipSPARSELt reuses the matching hipBLASLt source tree for kernel generation.
%autosetup -p1 -n %{name}
tar xf %{SOURCE1}
cd hipblaslt
patch -p1 < %{SOURCE2}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}
patch -p1 < %{SOURCE5}
patch -p1 < %{SOURCE6}
find tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +
cd ..

%conf -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export PATH=%{rocmllvm_bindir}:$PATH

%build -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export PATH=%{rocmllvm_bindir}:$PATH
export TENSILE_ROCM_ASSEMBLER_PATH=%{rocmllvm_bindir}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=%{rocmllvm_bindir}/clang-offload-bundler

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsparselt/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsparselt.so.*
%{_libdir}/hipsparselt/

%files devel
%{_includedir}/hipsparselt/
%{_libdir}/cmake/hipsparselt/
%{_libdir}/libhipsparselt.so

%if %{with test}
%files test
%{_bindir}/hipsparselt*
%endif

%changelog
%autochangelog
