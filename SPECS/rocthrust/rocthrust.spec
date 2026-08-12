# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocThrust's test client is HIP device-test code: it compiles on a GPU-less
# builder but needs a GPU to run. Build and package the test binaries so
# packagers can run them on hardware; keep the run behind run_test (default
# off) so OBS never executes device tests. cf. hiprand/rocfft.
%bcond run_test 0

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 22

Name:           rocthrust
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Thrust library

URL:            https://github.com/ROCm/rocThrust
VCS:            git:https://github.com/ROCm/rocThrust.git
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT
# All files are Apache 2.0 with some exceptions:
# ./cmake contains only files under MIT
# ./internal/benchmark/*.py are dual licensed Apache 2.0 and Boost 1.0
# ./thrust/ contain some header files that are Boost 1.0 licensed
# ./thrust/ contain some headers that are dual Apache 2.0 and Boost 1.0
# ./thrust/cmake/FindTBB.cmake is public domain
# ./thrust/detail/allocator/allocator_traits.h is dual Apache 2.0 and MIT
# ./thrust/detail/complex contains BSD 2 clause licensed headers
#!RemoteAsset:  sha256:b49bac5243d33092b242823cdf1d33fe7f05556bbbd2ca9ac4d5394e49f68b1c
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TEST=ON
# BUILD_TEST pulls in SQLite (for run-to-run reproducibility tests); use the
# system package instead of the upstream FetchContent download, which a
# network-isolated OBS builder cannot fetch. cf. rocfft.
BuildOption(conf):  -DSQLITE_USE_SYSTEM_PACKAGE=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(rocprim)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%global _description %{expand:
Thrust is a parallel algorithm library. This library has been
ported to HIP/ROCm platform, which uses the rocPRIM library.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%prep -a
# ROCMExportTargetsHeaderOnly.cmake hardcodes 'lib' as the library directory.
# Change it to the correct platform-specific library directory.
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{_lib}/' cmake/ROCMExportTargetsHeaderOnly.cmake

%install -a
rm -f %{buildroot}%{_docdir}/rocthrust/LICENSE

# rocThrust registers its gtest binaries as ctest tests, so the buildsystem's
# default %%check would run them and fail on a GPU-less builder. Only run when
# a packager opts in with run_test.
%check
%if %{with run_test}
%ctest
%endif

%files
%doc README.md
%license LICENSE
%license NOTICES.txt

%files devel
%{_includedir}/thrust/
%{_libdir}/cmake/rocthrust/

%files test
# rocThrust builds two test suites under BUILD_TEST: its own tests in test/
# (installed as <name>.hip) and the ported upstream thrust tests in testing/
# (installed as test_thrust_<name>). Package both, plus the install-time
# CTestTestfile tree under %{_bindir}/rocthrust/.
%{_bindir}/*.hip
%{_bindir}/test_*
%{_bindir}/rocthrust/

%changelog
%autochangelog
