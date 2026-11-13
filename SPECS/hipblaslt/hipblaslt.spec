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

# hipBLASlt needs GPU to run
%bcond test 0

%global tensile_version 4.33.0
# The upstream hipBLASTLt project has a hard fork of the python-tensile package
# The rocBLAS uses.  The two versions are incompatible.  It appears that the
# fork happened around version 4.33.0.  Unfortunately hipBLASLt can no longer be
# build without using this fork.
# https://github.com/ROCm/hipBLASLt/issues/535
# The problem with the fork has been raised here.
# https://github.com/ROCm/hipBLASLt/issues/908

%ifarch x86_64 riscv64
# Large kernel builds need the 32-job workers on both validation architectures.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           hipblaslt
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm general matrix operations beyond BLAS
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:5b2bf3102ef1c04f9e5afad61f8da077e8fb6f34d6395d32d11906f7987d04ff
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipblaslt.tar.gz
# rocisa compiles the release-matched conversion glue into its Python module.
#!RemoteAsset:  sha256:acc43368e45179c66492e90ba766f4a1001342f3eb244e378291baa4afa160ca
Source1:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/stinkytofu.tar.gz
Source2:        2003-upstream-true16-stinkytofu.patch
BuildSystem:    cmake

BuildOption(prep):  -n hipblaslt

%if %{with test}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DHIPBLASLT_ENABLE_CLIENT=ON
%else
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_CLIENT=OFF
%endif
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DCMAKE_SKIP_INSTALL_RPATH=ON
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DHIPBLASLT_ENABLE_MARKER=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_OPENMP=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_ROCROLLER=OFF
BuildOption(conf):  -DHIPBLASLT_ENABLE_SAMPLES=OFF
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
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
# Keep the upstream true16 conversion glue and installed library paired.
BuildRequires:  rocm-stinkytofu-devel >= %{rocm_version}-5
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  hipblas-devel >= %{rocm_version}
BuildRequires:  cmake(hipblas-common)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(msgpack)
BuildRequires:  cmake(origami)
BuildRequires:  rocblas-devel >= %{rocm_version}
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  gcc-fortran
BuildRequires:  hipcc
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
# https://github.com/ROCm/hipBLASLt/issues/1734
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(filelock)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(msgpack)
BuildRequires:  python3dist(nanobind)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(pytest)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocminfo

%if %{with test}
BuildRequires:  cmake(openblas)
BuildRequires:  cmake(GMock)
BuildRequires:  cmake(GTest)
%endif

%patchlist
# Patch from Fedora, change hard coded vendor paths
1000-hipblaslt-tensilelite-use-system-paths.patch
# https://github.com/ROCm/rocm-libraries/issues/2422
1001-hipblaslt-find-origami-package.patch
# use the distribution-provided nanobind instead of fetching/bundling it
2001-hipblaslt-tensilelite-use-system-nanobind.patch
# Heartbeat during tensilelite ParallelMap2 kernel generation: without periodic
# output the silent phase trips OBS's logidlelimit and times out on slow workers
# (riscv64 emulation). Same fix as mainline rocm-specs hipblaslt.
2002-tensilelite-add-heartbeat-during-parallel-map.patch
# Complete hipBLASLt side of merged upstream true16 operand support.
2004-upstream-true16-hipblaslt.patch

%global _description %{expand:
hipBLASLt is a library that provides general matrix-matrix
operations. It has a flexible API that extends functionalities
beyond a traditional BLAS library, such as adding flexibility
to matrix data layouts, input types, compute types, and
algorithmic implementations and heuristics.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}
%endif

%prep -a
# Restore the monorepo sibling source layout for rocisa conversion glue only.
# find_package still links the separately built system StinkyTofu library.
mkdir -p ../../shared
tar -xf %{SOURCE1} -C ../../shared
(cd ../../shared/stinkytofu && patch --fuzz=0 -p1 < %{SOURCE2})
# Use the system compiler names in source-tree Tensile invocations.
find tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH
export TENSILE_ROCM_ASSEMBLER_PATH=%{rocmllvm_bindir}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=%{rocmllvm_bindir}/clang-offload-bundler

%build
export PATH=%{rocmllvm_bindir}:$PATH
# Check upstream host-only true16 regressions before generating the full library.
%cmake_build --target _rocisa
export PYTHONPATH="$PWD/%{_vpath_builddir}/tensilelite/rocisa:$PWD/tensilelite${PYTHONPATH:+:$PYTHONPATH}"
ROCISA_BACKEND=rocisa python3 -m pytest -q -o addopts= \
    --confcutdir=tensilelite/Tensile/Tests/unit \
    tensilelite/Tensile/Tests/unit/test_amax_true16_activation.py
%cmake_build

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipblaslt/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipblaslt.so.*
%{_libdir}/hipblaslt/

%files devel
%{_includedir}/hipblaslt/
%{_includedir}/hipblaslt-export.h
%{_includedir}/hipblaslt-version.h
%{_libdir}/cmake/hipblaslt/
%{_libdir}/libhipblaslt.so

%if %{with test}
%files test
%{_bindir}/hipblaslt*
%{_bindir}/sequence.yaml
%endif

%changelog
%autochangelog
