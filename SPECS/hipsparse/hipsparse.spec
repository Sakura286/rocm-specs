%bcond gitcommit 0
%if %{with gitcommit}
%global commit0 2584e35062ad9c2edb68d93c464cf157bc57e3b0
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global date0 20250926
%endif

%global upstreamname hipsparse
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
%global hipsparse_name hipsparse%{pkg_suffix}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# export an llvm compilation database
# Useful for input for other llvm tools
%bcond export 0
%if %{with export}
%global build_compile_db ON
%else
%global build_compile_db OFF
%endif

# downloads tests, use mock --enable-network
%bcond test 0
%if %{with test}
%global build_test ON
%global __brp_check_rpaths %{nil}
%else
%global build_test OFF
%endif

%bcond check 0

# gfortran and clang rpm macros do not mix
%global build_fflags %{nil}

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

Name:           %{hipsparse_name}
%if %{with gitcommit}
Version:        git%{date0}.%{shortcommit0}
Release:        1%{?dist}
%else
Version:        %{rocm_version}
Release:        1%{?dist}
%endif
Summary:        ROCm SPARSE marshalling library
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries

%if %{with gitcommit}
Source0:        %{url}/archive/%{commit0}/rocm-libraries-%{shortcommit0}.tar.gz
%else
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz
%endif

Patch1:         0001-hipsparse-change-test-download-dir.patch

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
BuildRequires:  gcc-fortran
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
BuildRequires:  cmake(rocprim)
BuildRequires:  rocsparse%{pkg_suffix}-devel

%if %{with test}
BuildRequires:  gtest-devel
BuildRequires:  rocblas%{pkg_suffix}-devel
%endif

%if %{with check}
%if %{with export}
BuildRequires:  cppcheck
BuildRequires:  cppcheck-htmlreport
BuildRequires:  rocm-clang-analyzer%{pkg_suffix}
BuildRequires:  rocm-clang-tools-extra%{pkg_suffix}
%endif
%endif

Provides:       hipsparse%{pkg_suffix} = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
hipSPARSE is a SPARSE marshalling library with multiple
supported backends. It sits between your application and
a 'worker' SPARSE library, where it marshals inputs to
the backend library and marshals results to your
application. hipSPARSE exports an interface that doesn't
require the client to change, regardless of the chosen
backend. Currently, hipSPARSE supports rocSPARSE and
cuSPARSE backends.

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       hipsparse%{pkg_suffix}-devel = %{version}-%{release}

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/hiprand
%patch -P1 -p1
%else
%autosetup -p1 -n %{upstreamname}
%endif

# A better default for the matrices dir
sed -i -e 's@hipsparse_exepath() + "../matrices/"@"%{pkg_prefix}/share/hipsparse/matrices/"@' clients/include/utility.hpp

%build
%if %{with gitcommit}
cd projects/hipsparse
%endif

%cmake \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=%{build_compile_db} \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
    -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \
    -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \
    -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \
    -DCMAKE_BUILD_TYPE=%build_type \
    -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \
    -DCMAKE_SKIP_RPATH=ON \
    -DROCM_SYMLINK_LIBS=OFF \
    -DHIP_PLATFORM=amd \
    -DGPU_TARGETS=%{rocm_gpu_list_default} \
    -DBUILD_CLIENTS_BENCHMARKS=%{build_test} \
    -DBUILD_CLIENTS_SAMPLES=OFF \
    -DBUILD_CLIENTS_TESTS=%{build_test} \
    -DBUILD_CLIENTS_TESTS_OPENMP=OFF \
    -DCMAKE_MATRICES_DIR=%{_builddir}/hipsparse-test-matrices/ \
    -DBUILD_FORTRAN_CLIENTS=OFF

%cmake_build

%if %{with check}
%check
%if %{with export}
json=`find . -name 'compile_commands.json'`
json=`realpath $json`
json_dir=`dirname $json`
if [ -f ${json} ]; then
    jobs=`nproc`
    export PATH=%{rocmllvm_bindir}:$PATH
    output=/tmp/%{name}-tidy/
    mkdir -p ${output}
    # Use echo to consume tidy's error code
    %{rocmllvm_bindir}/run-clang-tidy -p ${json_dir} &> ${output}/tidy.log || echo "ran clang-tidy"
    
    output=/tmp/%{name}-cppcheck/
    mkdir -p ${output}
    cppcheck --project=${json} -j ${jobs} --std=c++17 --safety --output-file=${output}/cppcheck.txt
    cppcheck --project=${json} -j ${jobs} --std=c++17 --safety --xml --output-file=${output}/cppcheck.xml
    cppcheck-htmlreport --file=${output}/cppcheck.xml --report-dir=${output}
fi
%endif
%endif

%install
%if %{with gitcommit}
cd projects/hipsparse
%endif

%cmake_install

rm -f %{buildroot}%{pkg_prefix}/share/doc/hipsparse/LICENSE.md

%if %{with test}
mkdir -p %{buildroot}/%{pkg_prefix}/share/hipsparse/matrices
install -pm 644 %{_builddir}/%{name}-test-matrices/* %{buildroot}/%{pkg_prefix}/share/hipsparse/matrices
%endif

%files
%if %{with gitcommit}
%doc projects/hipsparse/README.md
%license projects/hipsparse/LICENSE.md
%else
%doc README.md
%license LICENSE.md
%endif

%{pkg_prefix}/%{pkg_libdir}/libhipsparse.so.4{,.*}

%files devel
%{pkg_prefix}/include/hipsparse/
%{pkg_prefix}/%{pkg_libdir}/libhipsparse.so
%{pkg_prefix}/%{pkg_libdir}/cmake/hipsparse/

%if %{with test}
%files test
%{pkg_prefix}/bin/hipsparse*
%{pkg_prefix}/share/hipsparse/
%endif

%changelog
* Mon Feb 2 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
