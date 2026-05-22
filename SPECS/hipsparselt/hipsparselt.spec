%define python_exec python3
%define python_expand python3

%bcond gitcommit 0
%if %{with gitcommit}
%global commit0 2584e35062ad9c2edb68d93c464cf157bc57e3b0
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global date0 20250926
%endif

%global upstreamname hipSPARSELt
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
%global hipsparselt_name hipsparselt

# The tensilelite that hipSPARELt use comes from hipBLASLt
# But not the matching release tag, a custom commit that is
# stored in the toplevel tensilelite_tag.txt file
#
# https://github.com/ROCm/hipSPARSELt/issues/248
#
# When keeping sync the hipblaslt project patch is difficult,
# use the hipblaslt repo tag, not the tensilelit_tag file
# This it the hipblaslt 7.1.1 repo tag
%global hipblaslt_commit 7c0ea90bd75ec971502a9232373f8ae7484a5cfa
%global hipblaslt_scommit %(c=%{hipblaslt_commit}; echo ${c:0:7})

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

# On CS10
# Depends on finding the build dir
# $ hipsparselt-test 
# hipSPARSELt version: 203
# ...
# [ FATAL ] /builddir/build/BUILD/googletest-1.14.0/googletest/src/gtest-internal-inl.h:685:: Condition !original_working_dir_.IsEmpty() failed. Failed to get the current working directory.
#
# So need to build with rpmbuild, not mock and run test on same machine with a newer gtest
%bcond test 0
%if %{with test}
%global __brp_check_rpaths %{nil}
%global build_test ON
%else
%global build_test OFF
%endif
# Fortran is only used in testing
%global build_fflags %{nil}

%global tensile_version 4.33.0
%global tensile_verbose 1

# match hipblaslt
%global gpu_list %{rocm_gpu_list_default}
# For testing
%global _gpu_list "gfx1100"

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

%bcond ninja 1

%if %{with ninja}
%global cmake_generator -G Ninja
%else
%global cmake_generator %{nil}
%endif

# Request for python-nanobind on EPEL
# https://bugzilla.redhat.com/show_bug.cgi?id=2402409
%bcond nanobind 0

Name:           %{hipsparselt_name}
%if %{with gitcommit}
Version:        git%{date0}.%{shortcommit0}
Release:        2%{?dist}
%else
Version:        %{rocm_version}
Release:        1%{?dist}
%endif
Summary:        A SPARSE marshaling library
License:        MIT

%if %{with gitcommit}
Url:            https://github.com/ROCm/rocm-libraries
Source0:        %{url}/archive/%{commit0}/rocm-libraries-%{shortcommit0}.tar.gz
%else
Url:            https://github.com/ROCm/%{upstreamname}
Source0:        %{url}/archive/rocm-%{rocm_version}.tar.gz#/%{upstreamname}-%{rocm_version}.tar.gz
%endif

# TODO : track down the gitcommit for this
Source1:        https://github.com/ROCm/hipBLASLt/archive/%{hipblaslt_commit}/hipBLASLt-%{hipblaslt_scommit}.tar.gz
# This are patches from the hiblaslt package for patching tensile
Source2:        0001-hipblaslt-tensilelite-remove-yappi-dependency.patch
Source3:        0001-hipblaslt-tensilelite-use-fedora-paths.patch
Source4:        0001-hipblaslt-find-origami-package.patch
# do not try to fetch, point to the nanobind tarball
Source5:        0001-hipblaslt-tensilelite-use-nanobind-tarball.patch
Source6:        0001-hipblaslt-tensilelite-use-clang.patch

%global nanobind_version 2.9.2
%global nanobind_giturl https://github.com/wjakob/nanobind
Source10:       %{nanobind_giturl}/archive/v%{nanobind_version}/nanobind-%{nanobind_version}.tar.gz
%global robinmap_version 1.3.0
%global robinmap_giturl https://github.com/Tessil/robin-map
Source11:       %{robinmap_giturl}/archive/v%{robinmap_version}/robin-map-%{robinmap_version}.tar.gz


%if %{with ninja}
BuildRequires:  ninja
%endif

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hipcc%{pkg_suffix}
BuildRequires:  hipsparse%{pkg_suffix}-devel
BuildRequires:  libzstd-devel
BuildRequires:  rocminfo%{pkg_suffix}
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  rocm-origami%{pkg_suffix}-devel
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
BuildRequires:  rocm-smi%{pkg_suffix}-devel
BuildRequires:  rocsparse%{pkg_suffix}-devel
BuildRequires:  roctracer%{pkg_suffix}-devel
BuildRequires:  zlib-devel

# For tensilelite
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(joblib)
BuildRequires:  python3dist(msgpack)
%if %{with nanobind}
BuildRequires:  python3dist(nanobind)
%endif
BuildRequires:  msgpack-devel
%global tensile_library_format msgpack
%global tensile_verbose 1

%if %{with test}
BuildRequires:  chrpath
BuildRequires:  flexiblas-devel
BuildRequires:  gcc-gfortran
BuildRequires:  gtest-devel
BuildRequires:  gmock-devel
BuildRequires:  rocm-omp-devel
%endif

Provides:       hipsparselt%{pkg_suffix} = %{version}-%{release}
Provides:       bundled(python-tensile) = %{tensile_version}

%if %{without nanobind}
# BSD-3-Clause
Provides:       bundled(nanobind) = %{nanobind_version}
Provides:       bundled(robin-map) = %{robinmap_version}
%endif

ExclusiveArch:  x86_64 riscv64

%description
hipSPARSELt is a SPARSE marshaling library, with multiple
supported backends. It sits between the application and a
'worker' SPARSE library, marshaling inputs into the backend
library and marshaling results back to the application.
hipSPARSELt exports an interface that does not require the
client to change, regardless of the chosen backend. Currently,
hipSPARSELt supports the rocSPARSELt backend.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       hipsparselt%{pkg_suffix}-devel = %{version}-%{release}

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
cd projects/hipsparselt
%else
%autosetup -p1 -n %{upstreamname}-rocm-%{version}
%endif

#tar xf %{SOURCE1}
cp %{_sourcedir}/hipBLASLt-MACRO.tar.gz %{_sourcedir}/hipBLASLt-%{hipblaslt_scommit}.tar.gz
tar xf %{_sourcedir}/hipBLASLt-MACRO.tar.gz
mv hipBLASLt-%{hipblaslt_commit} hipBLASLt
cd hipBLASLt

patch -p1 < %{SOURCE2}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}
patch -p1 < %{SOURCE5}

# Use PATH to find where TensileGetPath and other tensile bins are
sed -i -e 's@${Tensile_PREFIX}/bin/TensileGetPath@TensileGetPath@g'            tensilelite/Tensile/cmake/TensileConfig.cmake

# Make sure hip/hip_runtime.h is found
sed -i -e 's@-x hip @-I%{pkg_prefix}/include -x hip @' device-library/matrix-transform/CMakeLists.txt
sed -i -e 's@"-D__HIP_HCC_COMPAT_MODE__=1"@"-D__HIP_HCC_COMPAT_MODE__=1","-I%{pkg_prefix}/include"@' tensilelite/Tensile/Toolchain/Component.py

%if %{with nanobind}
# Disable download of nanobind
sed -i -e 's@FetchContent_MakeAvailable(nanobind)@find_package(nanobind)@' tensilelite/rocisa/CMakeLists.txt
%else
# Use bundled nanobind
tar xf %{SOURCE10}
mv nanobind-* nanobind
cd nanobind
tar xf %{SOURCE11}
cp -r robin-map-*/* ext/robin_map/
cd ..
tar czf nanobind.tar.gz nanobind
%endif

cd ..

# Prevent the virtualenv install from cmake
sed -i -e 's@virtualenv_install@#virtualenv_install@' CMakeLists.txt

# Unforce the setting of libdir
# https://github.com/ROCm/hipSPARSELt/issues/256
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

# change looking for cblas to flexiblas
sed -i -e 's@find_package( cblas REQUIRED CONFIG )@#find_package( cblas REQUIRED CONFIG )@' clients/CMakeLists.txt
sed -i -e 's@set( BLAS_LIBRARY "blas" )@set( BLAS_LIBRARY "flexiblas" )@' clients/CMakeLists.txt
sed -i -e 's@lapack cblas@flexiblas@' clients/gtest/CMakeLists.txt

# We are building from a tarball, not a git repo
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' hipBLASLt/cmake/dependencies.cmake
sed -i -e 's@find_package(Git REQUIRED)@#find_package(Git REQUIRED)@' cmake/Dependencies.cmake

# Forcefully replace all mentions of 'amdclang' with 'clang' in the Tensile Python files
find hipBLASLt/tensilelite -type f -name "*.py" -exec sed -i 's/amdclang++/clang++/g; s/amdclang/clang/g' {} +

%build
%if %{with gitcommit}
cd projects/hipsparselt
%endif

HIPBLASLT_PATH=$PWD/hipBLASLt
cd hipBLASLt
# disable openmp
sed -i -e 's@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." ON)@option(HIPBLASLT_ENABLE_OPENMP "Use OpenMP to improve performance." OFF)@' CMakeLists.txt

# Do a manual install instead of cmake's virtualenv
cd tensilelite
TL=$PWD

python3 setup.py install --root $TL
cd ../..

# Should not have to do this
export PATH=%{pkg_prefix}/bin:%{rocmllvm_bindir}:$PATH
CLANG_PATH=`hipconfig --hipclangpath`
ROCM_CLANG=${CLANG_PATH}/clang
RESOURCE_DIR=`${ROCM_CLANG} -print-resource-dir`
export DEVICE_LIB_PATH=${RESOURCE_DIR}/amdgcn/bitcode
export TENSILE_ROCM_ASSEMBLER_PATH=${CLANG_PATH}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=${CLANG_PATH}/clang-offload-bundler

# Look for the just built tensilelite
export PATH=${TL}/%{_bindir}:$PATH
export PYTHONPATH=${TL}%{python3_sitelib}:$PYTHONPATH
export Tensile_DIR=${TL}%{python3_sitelib}/Tensile
# Uncomment and see if the path is sane
# TensileGetPath

%cmake %{cmake_generator} \
       -DGPU_TARGETS=%{gpu_list} \
       -DBLAS_INCLUDE_DIR=%{_includedir}/flexiblas \
       -DBUILD_CLIENTS_TESTS=%{build_test} \
       -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
       -DBUILD_VERBOSE=ON \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang \
       -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ \
       -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
       -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
       -DCMAKE_PREFIX_PATH=%{python3_sitelib}/nanobind \
       -DCMAKE_Fortran_COMPILER=gfortran \
       -DCMAKE_VERBOSE_MAKEFILE=ON \
       -DHIP_PLATFORM=amd \
       -DHIPSPARSELT_HIPBLASLT_PATH=${HIPBLASLT_PATH} \
       -DROCM_SYMLINK_LIBS=OFF \
       -DTensile_COMPILER=clang++ \
       -DTensile_LIBRARY_FORMAT=%{tensile_library_format} \
       -DTensile_TEST_LOCAL_PATH=${TL} \
       -DTensile_VERBOSE=%{tensile_verbose} \
       -DVIRTUALENV_BIN_DIR=%{_bindir} \
       -DVIRTUALENV_SITE_PATH=${TL}%{python3_sitelib} \
       %{nil}

%cmake_build

%install
%if %{with gitcommit}
cd projects/hipsparselt
%endif

%cmake_install

# Extra license
rm -f %{buildroot}%{pkg_prefix}/share/doc/hipsparselt/LICENSE.md

# hipsparselt.x86_64: W: unstripped-binary-or-object /usr/lib64/hipsparselt/library/Kernels.so-000-gfx1100.hsaco
%{rocmllvm_bindir}/llvm-strip %{buildroot}%{pkg_prefix}/%{pkg_libdir}/hipsparselt/library/Kernels*.hsaco

# hipsparselt.x86_64: E: ldd-failed /usr/lib64/hipsparselt/library/Kernels.so-000-gfx1100.hsaco /usr/bin/bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8): No such file or directory
# ldd: warning: you do not have execution permission for `/usr/lib64/hipsparselt/library/Kernels.so-000-gfx1100.hsaco'
# 	not a dynamic executable
# Do something about the prems
chmod a+x %{buildroot}%{pkg_prefix}/%{pkg_libdir}/hipsparselt/library/Kernels*.hsaco
# But not much to do about the rest, this is not a normal *.so
# file /usr/lib64/hipsparselt/library/Kernels.so-000-gfx1100.hsaco 
# /usr/lib64/hipsparselt/library/Kernels.so-000-gfx1100.hsaco: ELF 64-bit LSB shared object, AMD GPU architecture version 1, dynamically linked, BuildID[sha1]=99e2194d9647da308804928d27ea1f336bfd76cc, stripped

%if %{with test}
# hipsparselt-test's rpath is pretty messed up
# chrpath -l /usr/bin/hipsparselt-test 
# /usr/bin/hipsparselt-test: RUNPATH=$ORIGIN/../lib:$ORIGIN/../lib/hipsparselt-clients/lib:/usr/llvm/lib
# So adjust it here
chrpath -r %{rocmllvm_libdir} %{buildroot}%{pkg_prefix}/bin/hipsparselt-test
%endif

%files
%if %{with gitcommit}
%doc projects/hipsparselt/README.md
%license projects/hipsparselt/LICENSE.md
%else
%doc README.md
%license LICENSE.md
%endif
%{pkg_prefix}/%{pkg_libdir}/libhipsparselt.so.*
%{pkg_prefix}/%{pkg_libdir}/hipsparselt/

%files devel
%{pkg_prefix}/include/hipsparselt/
%{pkg_prefix}/%{pkg_libdir}/cmake/hipsparselt/
%{pkg_prefix}/%{pkg_libdir}/libhipsparselt.so

%if %{with test}
%files test
%{pkg_prefix}/bin/hipsparselt*
%endif

%changelog
* Mon Feb 2 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
