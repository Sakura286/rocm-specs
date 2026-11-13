# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

%global tensile_version 4.33.0

%bcond test 0

%ifarch x86_64 riscv64
# Large kernel builds need the 32-job workers on both validation architectures.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           hipsparselt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A SPARSE marshaling library
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:14f085c3d1868705fc888d5105ee07fcd353800df5dfe62e2ccdb58c3b47171a
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipsparselt.tar.gz
#!RemoteAsset:  sha256:5b2bf3102ef1c04f9e5afad61f8da077e8fb6f34d6395d32d11906f7987d04ff
Source1:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipblaslt.tar.gz
# rocisa compiles the release-matched conversion glue into its Python module.
#!RemoteAsset:  sha256:acc43368e45179c66492e90ba766f4a1001342f3eb244e378291baa4afa160ca
Source2:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/stinkytofu.tar.gz
# Patches for hipBLASLt's tensilelite (applied during prep inside hipBLASLt/)
Source3:        0001-hipblaslt-tensilelite-use-system-paths.patch
Source4:        0001-hipblaslt-find-origami-package.patch
# Heartbeat during tensilelite ParallelMap2 kernel generation: without periodic
# output the silent phase trips OBS's logidlelimit and times out on slow workers
# (riscv64 emulation). Same fix as rocm-specs hipblaslt.
Source5:        2000-tensilelite-add-heartbeat-during-parallel-map.patch
# Use the distribution nanobind for the bundled hipBLASLt sources.
Source6:        2001-hipblaslt-tensilelite-use-system-nanobind.patch
BuildSystem:    cmake

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
BuildOption(conf):  -DCMAKE_Fortran_COMPILER=gfortran
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DCMAKE_INSTALL_RPATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}
BuildOption(conf):  -DGPU_TARGETS="gfx942;gfx950"
BuildOption(conf):  -DTensile_COMPILER=clang++
BuildOption(conf):  -DTensile_LIBRARY_FORMAT=msgpack
BuildOption(conf):  -DTensile_VERBOSE=1
BuildOption(conf):  -DVIRTUALENV_BIN_DIR=%{_bindir}
BuildOption(conf):  -Dnanobind_ROOT=%(python3 -m nanobind --cmake_dir)
BuildOption(conf):  -G Ninja
# Offload bundle IDs require an explicit host environment component.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
%ifarch riscv64
# The native GCC directory omits the GNU environment required by offload IDs.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_ARG1="--gcc-triple=%{_target_platform}"
%endif
%ifarch riscv64
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu --gcc-triple=%{_target_platform}"
%else
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu"
%endif
BuildOption(conf):  -DHIPSPARSELT_HIPBLASLT_PATH=%{_builddir}/%{buildsubdir}/hipblaslt
BuildOption(conf):  -DHIPBLASLT_ENABLE_OPENMP=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  rocm-stinkytofu-devel >= %{rocm_version}
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  hipsparse-devel >= %{rocm_version}
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(origami)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  rocsparse-devel >= %{rocm_version}
BuildRequires:  cmake(rocsparse)
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
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(filelock)
BuildRequires:  python3dist(numpy)
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
%autosetup -p1 -n %{name}
tar xf %{SOURCE1}
cd hipblaslt
# Restore the monorepo sibling source layout for rocisa conversion glue only.
# find_package still links the separately built system StinkyTofu library.
mkdir -p ../../shared
tar -xf %{SOURCE2} -C ../../shared
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}
patch -p1 < %{SOURCE5}
patch -p1 < %{SOURCE6}
find tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +
cd ..

%conf -p
# The GNU host target differs from the distribution LLVM runtime directory.
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}
export PATH=%{rocmllvm_bindir}:$PATH
export TENSILE_ROCM_ASSEMBLER_PATH=%{rocmllvm_bindir}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=%{rocmllvm_bindir}/clang-offload-bundler

%build -p
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}

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
