%global upstreamname rocthrust
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}
%global pkg_suffix -%{rocm_release}
%global pkg_module rocm%{pkg_suffix}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%global pkg_module default
%endif

# Compiler is hipcc, which is clang based:
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')
# there is no debug package
%global debug_package %{nil}

# Option to test suite for testing on real HW:
%bcond check 0
%if %{with check}
%global build_test ON
%else
%global build_test OFF
%endif

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
# Threaded compression reduces the build time.
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

Name:           rocthrust%{pkg_suffix}
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        ROCm Thrust libary

License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT AND LicenseRef-Fedora-Public-Domain
# All files are Apache 2.0 with some exceptions:
# ./cmake contains only files under MIT
# ./internal/benchmark/*.py are dual licensed Apache 2.0 and Boost 1.0
# ./thrust/ contain some headers files that are Boost 1.0 licensed
# ./thrust/ contain some headers that are dual Apache 2.0 and Boost 1.0
# ./thrust/cmake/FindTBB.cmake is public domain
# ./thrust/detail/allocator/allocator_traits.h is dual Apache 2.0 and MIT
# ./thrust/detail/complex contains BSD 2 clause licensed headers

URL:            https://github.com/ROCm/rocm-libraries
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  hipcc
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  cmake(rocprim)
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}

%if %{with check}
BuildRequires:  gtest-devel
BuildRequires:  rocminfo
%endif

ExclusiveArch:  x86_64 riscv64

%description
Thrust is a parallel algorithm library. This library has been
ported to HIP/ROCm platform, which uses the rocPRIM library.

%package devel
Summary:        The %{upstreamname} development package
Provides:       %{name}-static = %{version}-%{release}

%description devel
The %{upstreamname} development package.

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/rocthrust
%else
%autosetup -n %{upstreamname} -p1
%endif

#
# The ROCMExportTargetsHeaderOnly.cmake file
# generates a files that reference the install location of other files
# Make this change so they match
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{pkg_libdir}/' cmake/ROCMExportTargetsHeaderOnly.cmake

%build
%if %{with gitcommit}
cd projects/rocthrust
%endif


%if %{with check}
# Building all the gpu's does not make sense
# Build only the first one, this only works well with rpmbuild.
gpu=`rocm_agent_enumerator | head -n 1`
%endif

%cmake \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
    -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \
    -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \
    -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DBUILD_TEST=%{build_test} \
%if %{with check}
    -DAMDGPU_TARGETS=${gpu} \
%endif
    -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \
    -DROCM_SYMLINK_LIBS=OFF

%cmake_build

%install
%cmake_install

# Extra license
rm -f %{buildroot}%{pkg_prefix}/share/doc/rocthrust/LICENSE

%check
%if %{with check}
%ctest
%endif

%files devel
%doc README.md
%license LICENSE
%license NOTICES.txt
%{pkg_prefix}/include/thrust
%{pkg_prefix}/%{pkg_libdir}/cmake/rocthrust/

%changelog
* Mon Jan 26 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
