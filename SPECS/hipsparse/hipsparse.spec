# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipSPARSE need GPU to run tests
# Also, it need to download about 19 testing matrix
# It is verbose to add them to SOURCE and %%prep section
%bcond test 0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

Name:           hipsparse
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm SPARSE marshalling library
License:        MIT
URL:            https://github.com/ROCm/hipSPARSE
#!RemoteAsset:  sha256:0c564ecaf1a468992020431292baffa64baaeb22958d17eabbe73c0ea5dcc34b
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipsparse.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n hipsparse

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
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DCMAKE_INSTALL_RPATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DHIPSPARSE_ENABLE_CLIENT=ON
BuildOption(conf):  -DHIPSPARSE_ENABLE_SAMPLES=OFF
BuildOption(conf):  -DHIPSPARSE_ENABLE_BENCHMARKS=ON
%if %{with test}
BuildOption(conf):  -DHIPSPARSE_BUILD_TESTING=ON
%else
BuildOption(conf):  -DHIPSPARSE_BUILD_TESTING=OFF
%endif
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
# The benchmark also links clients-common, which requires GTest in 10.1.
BuildRequires:  cmake(GTest)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocprim-devel >= %{rocm_version}
BuildRequires:  cmake(rocprim)
BuildRequires:  rocsparse-devel >= %{rocm_version}
BuildRequires:  cmake(rocsparse)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  gcc-fortran
BuildRequires:  libomp-devel(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%global _description %{expand:
hipSPARSE is a SPARSE marshalling library with multiple
supported backends. It sits between your application and
a 'worker' SPARSE library, where it marshals inputs to
the backend library and marshals results to your
application. hipSPARSE exports an interface that doesn't
require the client to change, regardless of the chosen
backend. Currently, hipSPARSE supports rocSPARSE and
cuSPARSE backends.
}

%description
%{_description}

%package        benchmark
Summary:        Benchmark for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    benchmark
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

%conf -p
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}
export PATH=%{rocmllvm_bindir}:$PATH

%build -p
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}

%install -a
rm -f %{buildroot}%{_datadir}/doc/hipsparse/LICENSE.md

%check
%if %{with test}
%ctest
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipsparse.so.4{,.*}

%files benchmark
%{_bindir}/hipsparse-bench

%files devel
%{_includedir}/hipsparse/
%{_libdir}/cmake/hipsparse/
%{_libdir}/libhipsparse.so

%if %{with test}
%files test
%{_bindir}/hipsparse*
%{_datadir}/hipsparse/
%{_libexecdir}/hipsparse/
%endif

%changelog
%autochangelog
