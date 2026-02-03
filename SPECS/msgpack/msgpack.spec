# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           msgpack
Version:        3.1.0
Release:        %autorelease
Summary:        Binary-based efficient object serialization library

# Automatically converted from old format: Boost - review is highly recommended.
License:        BSL-1.0
URL:            http://msgpack.org
Source0:        https://github.com/msgpack/msgpack-c/releases/download/cpp-%{version}/%{name}-%{version}.tar.gz
Patch0:         0001-Fixed-724.patch
Patch1:         0002-msgpack-cmake4.patch

BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  doxygen
# for %%check
BuildRequires:  gtest-devel
BuildRequires:  zlib-devel

%description
MessagePack is a binary-based efficient object serialization
library. It enables to exchange structured objects between many
languages like JSON. But unlike JSON, it is very fast and small.

%package devel
Summary:  Libraries and header files for %{name}
Requires:  %{name}%{?_isa} = %{version}-%{release}

%description devel
Libraries and header files for %{name}

%prep -a

# gtest 1.17.0 requires at least C++17
sed -i "s|-std=c++98|-std=gnu++17|g" CMakeLists.txt

%build
# TODO: Please submit an issue to upstream (rhbz#2380918)
export CMAKE_POLICY_VERSION_MINIMUM=3.5
%cmake -DCMAKE_INSTALL_LIBDIR=%{_libdir} -Dlibdir=%{_libdir} -DBUILD_SHARED_LIBS=ON
%cmake_build

%check
# https://github.com/msgpack/msgpack-c/issues/697
export GTEST_FILTER=-object_with_zone.ext_empty
%ctest
cat %_vpath_builddir/Testing/Temporary/LastTest.log

%install
%cmake_install

%files
%license LICENSE_1_0.txt COPYING
%doc AUTHORS ChangeLog NOTICE README README.md
%{_libdir}/*.so.*

%files devel
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/msgpack.pc
%{_libdir}/cmake/msgpack

%changelog
%autochangelog
